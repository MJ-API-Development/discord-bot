import datetime
import json

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
!articles-paged page_count page_number
!articles-by-ticker ticker_code
!articles-by-company company_name
!articles-by-exchange exchange_code
!companies-by-exchange exchange_code
!tickers-by-exchange exchange_code
!list-publishers
!list-exchanges

Note: The above commands are rate-limited to one request per minute.
"""


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
    if message.content.startswith('!commands'):
        channel = client.get_channel(news_channel_id)
        await channel.send(channel_message)

    elif message.content.startswith('!article-by-uuid'):
        uuid = message.content.split(" ")[1].strip()
        if uuid:
            # TODO - fetch articles by uuid
            pass
        else:
            # TODO - raise error UUID not present
            pass
    elif message.content.startswith('!articles-bounded'):
        count: str = message.content.split(" ")[1].strip()
        if count.isdecimal():
            _count: int = int(count)
            # TODO - send request to endpoint and return articles
        else:
            pass
    elif message.content.startswith('!articles-by-date'):
        _date: str = message.content.split(" ")[1].strip()
        try:

            date_obj = datetime.date.fromisoformat(_date)
            # Use the date_obj for further processing
            print(date_obj)
        except ValueError:
            print("Invalid date format. Please provide the date in the format 'YYYY-MM-DD'.")

    elif message.content.startswith('!articles-by-publisher'):
        _publisher: str = message.content.split(" ")[1].strip()
        if _publisher:
            _publisher = _publisher.lower()
        else:
            pass

    elif message.content.startswith('!articles-paged'):
        try:
            _page_count: str = message.content.split(" ")[1].strip()
            _page_number: str = message.content.split(" ")[2].strip()
            if _page_number.isdecimal():
                _page_number: int = int(_page_number)
            else:
                raise ValueError("Invalid page number")
            if _page_count.isdecimal():
                _page_count: int = int(_page_count)
            else:
                raise ValueError("Invalid page count")
        except IndexError:
            raise ValueError("Please supply both a page count and a page number separated by whitespace")

    elif message.content.startswith('!articles-by-ticker'):
        try:
            _ticker: str = message.content.split(" ")[1].strip()
            if _ticker:
                _ticker = _ticker.lower()
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Ticker Code Required")

    elif message.content.startswith('!articles-by-company'):
        try:
            _company: str = message.content.split(" ")[1].strip()
            if _company:
                _company = _company.lower()
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Company Name Required")

    elif message.content.startswith('!articles-by-exchange'):
        try:
            _exchange: str = message.content.split(" ")[1].strip()
            if _exchange:
                _exchange = _exchange.lower()
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Exchange Required")

    elif message.content.startswith('!companies-by-exchange'):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            if _exchange_code:
                _exchange_code = _exchange_code.lower()
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Exchange Code Required")

    elif message.content.startswith('!tickers-by-exchange'):
        try:
            _exchange_code: str = message.content.split(" ")[1].strip()
            if _exchange_code:
                _exchange_code = _exchange_code.lower()
                channel = client.get_channel(news_channel_id)
                tickers = await tasks_executor.tickers_by_exchange(exchange_code=_exchange_code)

                formatted_tickers = json.dumps(tickers, indent=4)
                # Split the content into chunks of maximum 2000 characters
                chunks = [formatted_tickers[i:i + 2000] for i in range(0, len(formatted_tickers), 2000)]
                # Send each chunk as a separate message
                for chunk in chunks:
                    await channel.send(chunk)
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Exchange Code Required")

    elif message.content.startswith('!list-publishers'):
        try:
            print("listing publishers")
            channel = client.get_channel(news_channel_id)
            publishers = await tasks_executor.list_publishers()
            # Assuming the JSON string is stored in the 'publishers' variable
            formatted_publishers = json.dumps(publishers, indent=4)
            # Split the content into chunks of maximum 2000 characters
            chunks = [formatted_publishers[i:i + 2000] for i in range(0, len(formatted_publishers), 2000)]
            # Send each chunk as a separate message
            for chunk in chunks:
                await channel.send(chunk)
        except IndexError:
            raise ValueError("Exchange Code Required")

    elif message.content.startswith('!list-exchanges'):
        try:
            print("listing publishers")
            channel = client.get_channel(news_channel_id)
            exchanges = await tasks_executor.list_exchanges()
            # Assuming the JSON string is stored in the 'publishers' variable
            formatted_exchanges = json.dumps(exchanges, indent=4)
            # Split the content into chunks of maximum 2000 characters
            chunks = [formatted_exchanges[i:i + 2000] for i in range(0, len(formatted_exchanges), 2000)]
            # Send each chunk as a separate message
            for chunk in chunks:
                await channel.send(chunk)
        except IndexError:
            raise ValueError("Exchange Code Required")


class TaskScheduler:

    def __init__(self):
        # self._discord = discord.Client()
        self.settings = config_instance().DISCORD_SETTINGS

    async def run(self):
        client.run(token=self.settings.TOKEN)
