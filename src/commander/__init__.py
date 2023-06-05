
import json
from typing import Callable
from uuid import uuid4
from src.config import config_instance
import discord
from discord import Message, Client, Member
from src.tasks import tasks_executor

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


# noinspection PyMethodMayBeStatic
class CommandProcessor:
    def __init__(self, _client=client):
        self._client = _client
        self._resource_links: dict[str, dict[str, str | list[dict[str, str]]]] = {}
        self._chunk_size: int = 1000
        self._users_flags: set[str] = set()

    async def get_resource_by_key(self, resource_key: str) -> dict[str, str | list[dict[str, str]]]:
        """
        :param resource_key:
        :return:
        """
        # TODO send tickers by link
        return self._resource_links.get(resource_key)

    async def set_resource_by_key(self, resource: dict[str, str | list[dict[str, str]]]) -> str:
        """
            will set resource and return key
        :param resource:
        :return:
        """
        resource_key: str = str(uuid4())
        self._resource_links[resource_key] = resource
        return resource_key

    async def send_commands(self, message: Message):
        # channel = client.get_channel(news_channel_id)
        _mention = message.author.mention
        _ = client.get_channel(news_channel_id)

        if _mention not in self._users_flags:
            self._users_flags.add(message.author.mention)
            await message.author.send(channel_message)
            self._users_flags.remove(message.author.mention)
        else:
            await message.reply(f" {_mention} Wait until your previous command finished executing")

        # await channel.send(channel_message)

    async def articles_by_uuid(self, message: Message):
        try:
            uuid = message.content.split(" ")[1].strip()
            news_channel = client.get_channel(news_channel_id)

            if uuid:

                article: dict[str, str] = await tasks_executor.get_article_by_uuid(uuid=uuid)
                mention = message.author.mention

                if mention not in self._users_flags:
                    self._users_flags.add(message.author.mention)
                    await news_channel.send(f"Hi {mention}, I am sending Article to your DM")
                    await message.author.send(f"[{article['title']}]({article['link']})")
                    self._users_flags.remove(message.author.mention)
                else:
                    await message.reply(f" {mention} Wait until your previous command finished executing")
            else:
                await message.reply(
                    "Please supply Article UUID to retrieve Example !article-by-uuid' 10")
        except IndexError:
            await message.reply(
                "Please supply Article UUID to retrieve Example !article-by-uuid' 10")

    async def articles_bounded(self, message: Message):
        try:
            count: str = message.content.split(" ")[1].strip()
            if count.isdecimal():
                mention = message.author.mention
                news_channel = client.get_channel(news_channel_id)

                if mention not in self._users_flags:
                    self._users_flags.add(mention)
                    _count: int = int(count)
                    # Use the date_obj for further processing
                    articles: list[dict[str, str]] = await tasks_executor.get_articles_bounded(count=_count)
                    _count: int = len(articles)

                    await news_channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                    formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                    await message.author.send(f"Sending {_count} articles")
                    for article in formatted_articles:
                        await message.author.send(article)
                    self._users_flags.remove(mention)
                else:
                    await message.reply(f" {mention} Wait until your previous command finished executing")
            else:
                await message.reply(
                    "Please supply Number of Articles to retrieve Example !articles-bounded 10")

        except IndexError:
            await message.reply(
                "Please supply Number of Articles to retrieve Example !articles-bounded 10")

    async def articles_by_date(self, message: Message):
        try:
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
                _date: str = message.content.split(" ")[1].strip()
                # Use the date_obj for further processing

                articles: list[dict[str, str]] = await tasks_executor.articles_by_date(_date=_date)
                _count: int = len(articles)

                await news_channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
                self._users_flags.remove(mention)
            else:
                await message.reply(f" {mention} Wait until your previous command finished executing")

        except IndexError:
            await message.reply(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    async def articles_by_publisher(self, message: Message):
        try:
            _publisher: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
                if _publisher:
                    _publisher = _publisher.lower()
                    self._users_flags.add(mention)
                    articles: list[dict[str, str]] = await tasks_executor.articles_by_publisher(publisher=_publisher)
                    _count: int = len(articles)

                    await news_channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                    formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                    await message.author.send(f"Sending {_count} articles")
                    for article in formatted_articles:
                        await message.author.send(article)
                else:
                    await message.author.send(
                        "Please supply Publisher Name with this command example !articles-by-publisher bloomberg")
                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, Wait until your previous command finishes executing")

        except IndexError:
            await message.reply(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    async def articles_paged(self, message: Message):
        try:
            _page_number: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
                if _page_number.isdecimal():
                    _page_number: int = int(_page_number)
                else:
                    raise ValueError("Invalid page number")

                articles: list[dict[str, str]] = await tasks_executor.articles_by_page(number=_page_number)
                _count: int = len(articles)

                await news_channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)

                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, Wait until your previous command finished executing")

        except IndexError:
            await message.reply("Please supply Page Number with this command example !articles-paged 1")

    async def articles_by_ticker(self, message: Message):
        try:
            _ticker: str = message.content.split(" ")[1].strip()

            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
                if _ticker:
                    _ticker = _ticker.lower()

                    articles: list[dict[str, str]] = await tasks_executor.articles_by_ticker(ticker=_ticker)
                    _count: int = len(articles)

                    await news_channel.send(f"Hi {mention}, I am sending {_count} {_ticker.upper()} Articles to your DM")
                    formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                    await message.author.send(f"Sending {_count} articles")
                    for article in formatted_articles:
                        await message.author.send(article)
                else:
                    await message.reply("Please supply the ticker symbols example !articles-by-ticker MSFT")
                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, please wait until previous command finishes")

        except IndexError:
            await message.reply("Please supply the ticker symbols example !articles-by-ticker MSFT")

    async def articles_by_company(self, message: Message):
        try:
            _company: str = message.content.split(" ")[1].strip()
            _ = client.get_channel(news_channel_id)
            if _company:
                _company = _company.lower()
                await message.author.send("Endpoint still under development")
            else:
                await message.reply("Please supply the Company Name Example !articles-by-company Apple")

        except IndexError:
            await message.reply("Please supply the Company Name Example !articles-by-company Apple")

    async def articles_by_exchange(self, message: Message):
        try:
            _exchange: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
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
                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, please wait until previous command finishes")

        except IndexError:
            await message.reply("Please supply the Exchange Code Example !!articles-by-exchange US")

    async def companies_by_exchange(self, message: Message):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
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
                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, please wait until previous command finishes")

        except IndexError:
            await message.reply("Please supply the Exchange Code Example !companies-by-exchange US")

    async def tickers_by_exchange(self, message: Message):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            mention = message.author.mention
            news_channel = client.get_channel(news_channel_id)

            if mention not in self._users_flags:
                self._users_flags.add(mention)
                if _exchange_code:
                    _exchange_code = _exchange_code.lower()

                    tickers = await tasks_executor.tickers_by_exchange(exchange_code=_exchange_code)

                    await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
                    formatted_tickers = json.dumps(tickers, indent=4)
                    # Send each chunk as a separate message
                    for chunk in [formatted_tickers[i:i + self._chunk_size]
                                  for i in range(0, len(formatted_tickers), self._chunk_size)]:
                        await message.author.send(chunk)
                else:
                    await message.reply("Please supply the Exchange Code Example !tickers-by-exchange US")
                self._users_flags.remove(mention)
            else:
                await message.reply(f"Hi {mention}, please wait until previous command finishes")

        except IndexError:
            await message.reply("Please supply the Exchange Code Example !tickers-by-exchange US")

    async def list_publishers(self, message: Message):

        mention = message.author.mention
        news_channel = client.get_channel(news_channel_id)

        if mention not in self._users_flags:
            self._users_flags.add(mention)
            publishers = await tasks_executor.list_publishers()
            await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
            # Assuming the JSON string is stored in the 'publishers' variable
            formatted_publishers = json.dumps(publishers, indent=4)

            # Send each chunk as a separate message
            for chunk in [formatted_publishers[i:i + self._chunk_size]
                          for i in range(0, len(formatted_publishers), self._chunk_size)]:
                await message.author.send(chunk)
            self._users_flags.remove(mention)
        else:
            await message.reply(f"Hi {mention}, please wait until previous command finishes")

    async def list_exchanges(self, message):
        print("listing Exchanges")

        mention = message.author.mention
        news_channel = client.get_channel(news_channel_id)

        if mention not in self._users_flags:
            self._users_flags.add(mention)
            exchanges = await tasks_executor.list_exchanges()
            await news_channel.send(f"Hi {mention}, I am sending the response to your DM")
            # Assuming the JSON string is stored in the 'publishers' variable
            formatted_exchanges = json.dumps(exchanges, indent=4)
            # Send each chunk as a separate message
            for chunk in [formatted_exchanges[i:i + self._chunk_size]
                          for i in range(0, len(formatted_exchanges), self._chunk_size)]:
                await message.author.send(chunk)

            self._users_flags.remove(mention)
        else:
            await message.reply(f"Hi {mention}, please wait until previous command finishes")


command_processor = CommandProcessor(_client=client)
_commands_lookup: dict[str, Callable] = {
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
async def on_message(message):

    # Prevent sending message to itself
    if message.author == client.user:
        return

    try:
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
