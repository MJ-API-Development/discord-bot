import asyncio
import json
from typing import Callable
from uuid import uuid4

import discord
from discord import Message

from src.config import config_instance
from src.logger import init_logger
from src.tasks import tasks_executor
from src.tools import mention_wrapper

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)
news_channel_id: int = config_instance().DISCORD_SETTINGS.NEWS_API_CHANNEL_ID

channel_message: str = f"""
Access Our Financial & Business News API.

Use the following commands in order to access Financial & Business News:

    !article-by-uuid UUID
    !articles-bounded count
    !articles-by-date date
    !articles-by-publisher publisher_name
    !articles-paged page_number
    !articles-by-ticker ticker_code
    !tickers-by-exchange exchange_code
    !list-publishers
    !list-exchanges
------------------------------------------------------------------------    
------------------------------------------------------------------------
"""
ADDED_RATE_LIMIT: int = 60
STOP_FLAG: str = "admin_stop"
INCREASE_RATE_LIMIT_FLAG: str = "increase_rate_limit"


# noinspection PyMethodMayBeStatic,DuplicatedCode
class CommandProcessor:
    """

    """

    def __init__(self, _client=client):
        self._logger = init_logger(self.__class__.__name__)
        self._client = _client
        self._resource_links: dict[str, dict[str, str | list[dict[str, str]]]] = {}
        self._chunk_size: int = 1000
        self._rate_limit_flags: set[str] = set()
        self.admin_flags: set[str] = set()

    async def get_resource_by_key(self, resource_key: str) -> dict[str, str | list[dict[str, str]]]:
        """
        **get_resource_by_key**
            this will return resources by resource key

        :param resource_key:
        :return: dict[str, str]
        """
        return self._resource_links.get(resource_key)

    async def set_resource_by_key(self, resource) -> str:
        """
        **set_resource_by_key**
            adds resource by a unique key so the resource can be accessed via web links.

        :param resource:
        :return:
        """
        resource_key: str = str(uuid4())
        self._resource_links[resource_key] = resource
        return resource_key

    async def create_resource_link(self, resource_key: str) -> str:
        return f"https://discord.news-api.site/resource/{resource_key}"

    async def admin_commands(self, message: Message):
        """
            **admin_commands**
                this method executes commands for admin users

        :param message:
        :return: None
        """

        if str(message.author.id) == config_instance().DISCORD_SETTINGS.ADMIN_ID:
            sub_command = message.content.split(" ")[1].strip()

            if sub_command.casefold() == "stop-bot":
                self.admin_flags.add(STOP_FLAG)
                await message.reply("bot has been paused")

            if sub_command.casefold() == "reset-bot":
                self.admin_flags.remove(STOP_FLAG)
                await message.reply("bot has been disabled")

            elif sub_command.casefold() == "rate-limit":
                self.admin_flags.add(INCREASE_RATE_LIMIT_FLAG)
                await message.reply("rate limit enabled")

            elif sub_command.casefold() == "reset-limit":
                self.admin_flags.remove(INCREASE_RATE_LIMIT_FLAG)
                await message.reply("reset limit enabled")

            elif sub_command.casefold() == "reset-flags":
                self.admin_flags.clear()
                await message.reply("flags cleared")

            else:
                await message.reply("Unable to understand the command")

        else:
            _id: int = message.author.id
            await message.reply(f"User not authorized : {_id}")

    @mention_wrapper
    async def send_commands(self, message: Message):
        """
            **send_commands**
                this method executes and send responses to clients using our bots
        :param message:
        :return: None
        """
        # channel = client.get_channel(news_channel_id)
        self._logger.info(f'sending commands for: {message.author.mention}')
        _ = client.get_channel(news_channel_id)
        await message.author.send(channel_message)

        # await channel.send(channel_message)

    @mention_wrapper
    async def articles_by_uuid(self, message: Message):
        """
            **articles_by_uuid**
                given an article uuid return article
        :param message:
        :return:
        """
        try:
            self._logger.info(f'listing articles by uuid for: {message.author.mention}')

            uuid = message.content.split(" ")[1].strip()
            if uuid:
                article: dict[str, str] = await tasks_executor.get_article_by_uuid(uuid=uuid)
                mention = message.author.mention
                resource_key = await self.set_resource_by_key(resource=article)
                resource_link = await self.create_resource_link(resource_key=resource_key)

                await message.reply(f"Hi {mention}, I am sending the Article to your DM")
                await message.reply(f"You can also download your article from")
                await message.reply(resource_link)
            else:
                await message.reply(
                    "Please supply Article UUID to retrieve Example !article-by-uuid' 10")
        except IndexError:
            await message.reply(
                "Please supply Article UUID to retrieve Example !article-by-uuid' 10")

    @mention_wrapper
    async def articles_bounded(self, message: Message):
        """
            **articles_bounded**

        :param message:
        :return:
        """
        try:

            self._logger.info(f'listing articles bounded for: {message.author.mention}')
            count: str = message.content.split(" ")[1].strip()
            if count.isdecimal():
                mention = message.author.mention
                _count: int = int(count)
                if _count > 99:
                    self._rate_limit_flags.remove(mention)
                    await message.reply(f"Cannot send more than 99 articles")
                    return
                # Use the date_obj for further processing
                articles: list[dict[str, str]] = await tasks_executor.get_articles_bounded(count=_count)
                _count: int = len(articles)
                resource_key = await self.set_resource_by_key(resource=articles)
                resource_link = await self.create_resource_link(resource_key=resource_key)
                await message.reply(f"Hi {mention}, I am sending {_count} Articles to your DM")
                await message.reply(f"You can also download your articles from")
                await message.reply(resource_link)

                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]

                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
            else:
                await message.reply(
                    "Please supply Number of Articles to retrieve Example !articles-bounded 10")

        except IndexError:
            await message.reply(
                "Please supply Number of Articles to retrieve Example !articles-bounded 10")

    @mention_wrapper
    async def articles_by_date(self, message: Message):
        try:

            self._logger.info(f'listing articles by date for: {message.author.mention}')

            _date: str = message.content.split(" ")[1].strip()
            # Use the date_obj for further processing

            articles: list[dict[str, str]] = await tasks_executor.articles_by_date(_date=_date)
            resource_key = await self.set_resource_by_key(resource=articles)
            resource_link = await self.create_resource_link(resource_key=resource_key)

            mention = message.author.mention
            _count: int = len(articles)
            await message.reply(f"Hi {mention}, I am sending {_count} Articles to your DM")
            await message.reply(f"You can also download your articles from")
            await message.reply(resource_link)

            formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
            await message.author.send(f"Sending {_count} articles")
            for article in formatted_articles:
                await message.author.send(article)

        except IndexError:
            await message.reply(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    @mention_wrapper
    async def articles_by_publisher(self, message: Message):
        try:

            self._logger.info(f'listing articles by publisher for: {message.author.mention}')
            _publisher: str = message.content.split(" ")[1].strip()

            if _publisher:
                _publisher = _publisher.lower()

                articles: list[dict[str, str]] = await tasks_executor.articles_by_publisher(publisher=_publisher)
                resource_key = await self.set_resource_by_key(resource=articles)
                resource_link = await self.create_resource_link(resource_key=resource_key)

                _count: int = len(articles)
                mention = message.author.mention

                await message.reply(f"Hi {mention}, I am sending {_count} Articles to your DM")
                await message.reply(f"You can also download your articles from")
                await message.reply(resource_link)

                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
            else:
                await message.author.send(
                    "Please supply Publisher Name with this command example !articles-by-publisher bloomberg")
        except IndexError:
            await message.reply(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    @mention_wrapper
    async def articles_paged(self, message: Message):
        try:
            self._logger.info(f'listing paged articles for: {message.author.mention}')
            _page_number: str = message.content.split(" ")[1].strip()

            if _page_number.isdecimal():
                _page_number: int = int(_page_number)
            else:
                raise ValueError("Invalid page number")

            articles: list[dict[str, str]] = await tasks_executor.articles_by_page(number=_page_number)
            resource_key = await self.set_resource_by_key(resource=articles)
            resource_link = await self.create_resource_link(resource_key=resource_key)

            _count: int = len(articles)
            mention = message.author.mention

            await message.reply(f"Hi {mention}, I am sending {_count} Articles to your DM")
            await message.reply(f"You can also download your articles from")
            await message.reply(resource_link)

            formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
            await message.author.send(f"Sending {_count} articles")

            for article in formatted_articles:
                await message.author.send(article)

        except IndexError:
            await message.reply("Please supply Page Number with this command example !articles-paged 1")

    @mention_wrapper
    async def articles_by_ticker(self, message: Message):
        try:
            self._logger.info(f'listing articles by ticker for: {message.author.mention}')
            _ticker: str = message.content.split(" ")[1].strip()

            if _ticker:
                _ticker = _ticker.lower()

                articles: list[dict[str, str]] = await tasks_executor.articles_by_ticker(ticker=_ticker)
                resource_key = await self.set_resource_by_key(resource=articles)
                resource_link = await self.create_resource_link(resource_key=resource_key)

                _count: int = len(articles)
                mention = message.author.mention

                await message.reply(f"Hi {mention}, I am sending {_count} Articles to your DM")
                await message.reply(f"You can also download your articles from")
                await message.reply(resource_link)

                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
            else:
                await message.reply("Please supply the ticker symbols example !articles-by-ticker MSFT")

        except IndexError:
            await message.reply("Please supply the ticker symbols example !articles-by-ticker MSFT")

    @mention_wrapper
    async def articles_by_company(self, message: Message):
        try:
            self._logger.info(f'listing articles by company for {message.author.mention}')
            _company: str = message.content.split(" ")[1].strip()
            _ = client.get_channel(news_channel_id)
            if _company:
                _company = _company.lower()
                await message.author.send("Endpoint still under development")
            else:
                await message.reply("Please supply the Company Name Example !articles-by-company Apple")

        except IndexError:
            await message.reply("Please supply the Company Name Example !articles-by-company Apple")

    @mention_wrapper
    async def articles_by_exchange(self, message: Message):
        try:
            self._logger.info(f'listing articles by exchange for {message.author.mention}')
            _exchange: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if _exchange:
                _exchange = _exchange.lower()
                companies = await tasks_executor.articles_by_exchange(exchange_code=_exchange)
                await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
                formatted_tickers = json.dumps(companies, indent=4)
                # Split the content into chunks of maximum 2000 characters
                # Send each chunk as a separate message
                for chunk in [formatted_tickers[i:i + self._chunk_size]
                              for i in range(0, len(formatted_tickers), self._chunk_size)]:
                    await message.author.send(chunk)

            else:
                await message.reply("Please supply the Exchange Code Example !!articles-by-exchange US")

        except IndexError:
            await message.reply("Please supply the Exchange Code Example !!articles-by-exchange US")

    @mention_wrapper
    async def companies_by_exchange(self, message: Message):
        try:
            self._logger.info(f'listing companies for {message.author.mention}')
            _exchange_code: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if _exchange_code:
                _exchange_code = _exchange_code.lower()

                companies = await tasks_executor.companies_by_exchange(exchange_code=_exchange_code)

                await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
                formatted_tickers = json.dumps(companies, indent=4)
                # Split the content into chunks of maximum 2000 characters
                # Send each chunk as a separate message
                for chunk in [formatted_tickers[i:i + self._chunk_size]
                              for i in range(0, len(formatted_tickers), self._chunk_size)]:
                    await message.author.send(chunk)

            else:
                await message.reply("Please supply the Exchange Code Example !companies-by-exchange US")

        except IndexError:
            await message.reply("Please supply the Exchange Code Example !companies-by-exchange US")

    @mention_wrapper
    async def tickers_by_exchange(self, message: Message):
        try:
            self._logger.info(f'listing tickers for: {message.author.mention}')
            _exchange_code: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if _exchange_code:
                _exchange_code = _exchange_code.lower()

                tickers = await tasks_executor.tickers_by_exchange(exchange_code=_exchange_code)
                resource_key = await self.set_resource_by_key(resource=tickers)
                resource_link = await self.create_resource_link(resource_key=resource_key)

                await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
                await news_channel.send(f"Hi {mention}, you can also download your ticker list from")
                await news_channel.send(resource_link)

                formatted_tickers = json.dumps(tickers, indent=4)
                # Send each chunk as a separate message
                for chunk in [formatted_tickers[i:i + self._chunk_size]
                              for i in range(0, len(formatted_tickers), self._chunk_size)]:
                    await message.author.send(chunk)
            else:
                await message.reply("Please supply the Exchange Code Example !tickers-by-exchange US")
        except IndexError:
            await message.reply("Please supply the Exchange Code Example !tickers-by-exchange US")

    @mention_wrapper
    async def list_publishers(self, message: Message):
        self._logger.info(f'listing publishers for: {message.author.mention}')
        mention = message.author.mention
        news_channel = client.get_channel(news_channel_id)
        publishers = await tasks_executor.list_publishers()
        resource_key = await self.set_resource_by_key(resource=publishers)
        resource_link = await self.create_resource_link(resource_key=resource_key)

        await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
        await news_channel.send(f"Hi {mention}, you can also download your publisher list from")
        await news_channel.send(resource_link)

        # Assuming the JSON string is stored in the 'publishers' variable
        formatted_publishers = json.dumps(publishers, indent=4)

        # Send each chunk as a separate message
        for chunk in [formatted_publishers[i:i + self._chunk_size]
                      for i in range(0, len(formatted_publishers), self._chunk_size)]:
            await message.author.send(chunk)

    @mention_wrapper
    async def list_exchanges(self, message: Message):

        self._logger.info(f'listing exchanges for: {message.author.mention}')
        mention = message.author.mention
        news_channel = client.get_channel(news_channel_id)
        exchanges = await tasks_executor.list_exchanges()
        resource_key = await self.set_resource_by_key(resource=exchanges)
        resource_link = await self.create_resource_link(resource_key=resource_key)

        await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
        await news_channel.send(f"Hi {mention}, you can also download your exchange list from")
        await news_channel.send(resource_link)

        # Assuming the JSON string is stored in the 'publishers' variable
        formatted_exchanges = json.dumps(exchanges, indent=4)
        # Send each chunk as a separate message
        for chunk in [formatted_exchanges[i:i + self._chunk_size]
                      for i in range(0, len(formatted_exchanges), self._chunk_size)]:
            await message.author.send(chunk)


command_processor = CommandProcessor(_client=client)
_commands_lookup: dict[str, Callable] = {
    '!admin': command_processor.admin_commands,
    '!commands': command_processor.send_commands,
    '!article-by-uuid': command_processor.articles_by_uuid,
    '!articles-bounded': command_processor.articles_bounded,
    '!articles-by-date': command_processor.articles_by_date,
    '!articles-by-publisher': command_processor.articles_by_publisher,
    '!articles-paged': command_processor.articles_paged,
    '!articles-by-ticker': command_processor.articles_by_ticker,
    '!articles-by-company': command_processor.articles_by_company,
    '!articles-by-exchange': command_processor.articles_by_exchange,
    '!companies-by-exchange': command_processor.companies_by_exchange,
    '!tickers-by-exchange': command_processor.tickers_by_exchange,
    '!list-publishers': command_processor.list_publishers,
    '!list-exchanges': command_processor.list_exchanges,
}


@client.event
async def on_ready():
    channel = client.get_channel(news_channel_id)
    if channel:
        await channel.send(channel_message)
    else:
        pass


@client.event
async def on_message(message: Message):
    # Prevent sending message to itself
    if message.author == client.user:
        return

    try:
        if not message.content.startswith("!admin"):
            # this enables admin flags for everyone else except admin
            if STOP_FLAG in command_processor.admin_flags:
                await message.reply("Server Has been paused by admin")
                return

            if INCREASE_RATE_LIMIT_FLAG in command_processor.admin_flags:
                await asyncio.sleep(ADDED_RATE_LIMIT)

        await _commands_lookup.get(message.content.split(" ")[0], command_processor.send_commands)(message)
        # await _commands_lookup[message.content.split(" ")[0]](message)
    except IndexError:
        await command_processor.send_commands(message)


@client.event
async def on_member_join(member):
    # Send a welcome message to the newly joined member
    welcome_message = f"Welcome, {member.mention}! TO EOD-STOCK-API VERSION-0.0.1"
    await member.send(welcome_message)

    # Perform additional actions if needed


@client.event
async def on_member_remove(member):
    # Perform actions or logging for the departed member
    farewell_message = f"Goodbye, {member.name}! We'll miss you."
    farewell_channel = client.get_channel(news_channel_id)
    await farewell_channel.send(farewell_message)
