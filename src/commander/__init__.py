import datetime
import json
from typing import Callable
from uuid import uuid4
from src.config import config_instance
import discord
from discord.ext import commands

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

Note: The above commands are rate-limited to one request per minute.
"""


# noinspection PyMethodMayBeStatic
class CommandProcessor:
    def __init__(self):
        self._resource_links: dict[str, dict[str, str | list[dict[str, str]]]] = {}

    async def get_resource_by_key(self, resource_key: str) -> dict[str, str | list[dict[str, str]]]:
        """
        :param resource_key:
        :return:
        """
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

    async def send_commands(self, message):
        # channel = client.get_channel(news_channel_id)
        await message.author.send(channel_message)
        # await channel.send(channel_message)

    async def articles_by_uuid(self, message):
        try:
            uuid = message.content.split(" ")[1].strip()
            if uuid:
                channel = client.get_channel(news_channel_id)
                article: dict[str, str] = await tasks_executor.get_article_by_uuid(uuid=uuid)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending Article to your DM")
                await message.author.send(f"[{article['title']}]({article['link']})")
            else:
                await message.author.send(
                    "Please supply Article UUID to retrieve Example !article-by-uuid' 10")
        except IndexError:
            await message.author.send(
                "Please supply Article UUID to retrieve Example !article-by-uuid' 10")

    async def articles_bounded(self, message):
        try:
            count: str = message.content.split(" ")[1].strip()
            if count.isdecimal():
                _count: int = int(count)
                # Use the date_obj for further processing
                channel = client.get_channel(news_channel_id)
                articles: list[dict[str, str]] = await tasks_executor.get_articles_bounded(count=_count)
                _count: int = len(articles)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)

            else:
                await message.author.send(
                    "Please supply Total Articles to retrieve Example !articles-bounded 10")

        except IndexError:
            await message.author.send(
                "Please supply Total Articles to retrieve Example !articles-bounded 10")

    async def articles_by_date(self, message):
        try:
            _date: str = message.content.split(" ")[1].strip()
            # Use the date_obj for further processing
            channel = client.get_channel(news_channel_id)
            articles: list[dict[str, str]] = await tasks_executor.articles_by_date(_date=_date)
            _count: int = len(articles)
            mention = message.author.mention
            await channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
            formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
            await message.author.send(f"Sending {_count} articles")
            for article in formatted_articles:
                await message.author.send(article)
        except IndexError:
            await message.author.send(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    async def articles_by_publisher(self, message):
        try:
            _publisher: str = message.content.split(" ")[1].strip()
            if _publisher:
                _publisher = _publisher.lower()
                channel = client.get_channel(news_channel_id)
                articles: list[dict[str, str]] = await tasks_executor.articles_by_publisher(publisher=_publisher)
                _count: int = len(articles)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
            else:
                await message.author.send(
                    "Please supply Publisher Name with this command example !articles-by-publisher bloomberg")
        except IndexError:
            await message.author.send(
                "Please supply Page Number with this command example !articles-by-publisher bloomberg")

    async def articles_paged(self, message):
        try:
            _page_number: str = message.content.split(" ")[1].strip()
            if _page_number.isdecimal():
                _page_number: int = int(_page_number)
            else:
                raise ValueError("Invalid page number")

            channel = client.get_channel(news_channel_id)
            articles: list[dict[str, str]] = await tasks_executor.articles_by_page(number=_page_number)
            _count: int = len(articles)
            mention = message.author.mention
            await channel.send(f"Hi {mention}, I am sending {_count} Articles to your DM")
            formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
            await message.author.send(f"Sending {_count} articles")
            for article in formatted_articles:
                await message.author.send(article)
        except IndexError:
            await message.author.send("Please supply Page Number with this command example !articles-paged 1")

    async def articles_by_ticker(self, message):
        try:
            _ticker: str = message.content.split(" ")[1].strip()
            if _ticker:
                _ticker = _ticker.lower()
                channel = client.get_channel(news_channel_id)
                articles: list[dict[str, str]] = await tasks_executor.articles_by_ticker(ticker=_ticker)
                _count: int = len(articles)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending {_count} {_ticker.upper()} Articles to your DM")
                formatted_articles = [f"[{article['title']}]({article['link']})" for article in articles]
                await message.author.send(f"Sending {_count} articles")
                for article in formatted_articles:
                    await message.author.send(article)
            else:
                await message.author.send("Please supply the ticker symbols example !articles-by-ticker MSFT")

        except IndexError:
            await message.author.send("Please supply the ticker symbols example !articles-by-ticker MSFT")

    async def articles_by_company(self, message):
        try:
            _company: str = message.content.split(" ")[1].strip()
            if _company:
                _company = _company.lower()
                await message.author.send("Endpoint still under development")
            else:
                await message.author.send("Please supply the Company Name Example !articles-by-company Apple")

        except IndexError:
            await message.author.send("Please supply the Company Name Example !articles-by-company Apple")

    async def articles_by_exchange(self, message):
        try:
            _exchange: str = message.content.split(" ")[1].strip()
            if _exchange:
                _exchange = _exchange.lower()
                channel = client.get_channel(news_channel_id)
                companies = await tasks_executor.articles_by_exchange(exchange_code=_exchange)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending the response to your DM")

                formatted_tickers = json.dumps(companies, indent=4)
                # Split the content into chunks of maximum 2000 characters
                chunks = [formatted_tickers[i:i + 2000] for i in range(0, len(formatted_tickers), 2000)]
                # Send each chunk as a separate message
                for chunk in chunks:
                    await message.author.send(chunk)

            else:
                await message.author.send("Please supply the Exchange Code Example !!articles-by-exchange US")

        except IndexError:
            await message.author.send("Please supply the Exchange Code Example !!articles-by-exchange US")

    async def companies_by_exchange(self, message):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            if _exchange_code:
                _exchange_code = _exchange_code.lower()

                channel = client.get_channel(news_channel_id)
                companies = await tasks_executor.companies_by_exchange(exchange_code=_exchange_code)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending the response to your DM")

                formatted_tickers = json.dumps(companies, indent=4)
                # Split the content into chunks of maximum 2000 characters
                chunks = [formatted_tickers[i:i + 2000] for i in range(0, len(formatted_tickers), 2000)]
                # Send each chunk as a separate message
                for chunk in chunks:
                    await message.author.send(chunk)

            else:
                await message.author.send("Please supply the Exchange Code Example !companies-by-exchange US")

        except IndexError:
            await message.author.send("Please supply the Exchange Code Example !companies-by-exchange US")

    async def tickers_by_exchange(self, message):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            if _exchange_code:
                _exchange_code = _exchange_code.lower()
                channel = client.get_channel(news_channel_id)
                tickers = await tasks_executor.tickers_by_exchange(exchange_code=_exchange_code)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending the response to your DM")

                formatted_tickers = json.dumps(tickers, indent=4)
                # Split the content into chunks of maximum 2000 characters
                chunks = [formatted_tickers[i:i + 2000] for i in range(0, len(formatted_tickers), 2000)]
                # Send each chunk as a separate message
                for chunk in chunks:
                    await message.author.send(chunk)
            else:
                await message.author.send("Please supply the Exchange Code Example !tickers-by-exchange US")

        except IndexError:
            await message.author.send("Please supply the Exchange Code Example !tickers-by-exchange US")

    async def list_publishers(self, message):
        channel = client.get_channel(news_channel_id)
        publishers = await tasks_executor.list_publishers()
        mention = message.author.mention
        await channel.send(f"Hi {mention}, I am sending the response to your DM")

        # Assuming the JSON string is stored in the 'publishers' variable
        formatted_publishers = json.dumps(publishers, indent=4)
        # Split the content into chunks of maximum 2000 characters
        chunks = [formatted_publishers[i:i + 2000] for i in range(0, len(formatted_publishers), 2000)]
        # Send each chunk as a separate message
        for chunk in chunks:
            await message.author.send(chunk)

    async def list_exchanges(self, message):
        print("listing publishers")
        channel = client.get_channel(news_channel_id)
        exchanges = await tasks_executor.list_exchanges()
        mention = message.author.mention
        await channel.send(f"Hi {mention}, I am sending the response to your DM")
        # Assuming the JSON string is stored in the 'publishers' variable
        formatted_exchanges = json.dumps(exchanges, indent=4)
        # Split the content into chunks of maximum 2000 characters
        chunks = [formatted_exchanges[i:i + 2000] for i in range(0, len(formatted_exchanges), 2000)]
        # Send each chunk as a separate message
        for chunk in chunks:
            await message.author.send(chunk)


command_processor = CommandProcessor()
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
        await channel.send('Welcome to Business & Financial News API Channel')
        await channel.send(channel_message)
    else:
        print('Invalid channel ID.')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await _commands_lookup[message.content.split(" ")[0]](message)


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