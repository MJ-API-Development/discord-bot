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
!articles-paged page_number
!articles-by-ticker ticker_code
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
        # channel = client.get_channel(news_channel_id)
        await message.author.send(channel_message)
        # await channel.send(channel_message)

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
            await message.author.send([f"[{article['title']}]({article['link']})" for article in articles])

        except IndexError:
            await message.author.send("Please supply Page Number with this command example !articles-paged 1")

    elif message.content.startswith('!articles-by-ticker'):
        try:
            _ticker: str = message.content.split(" ")[1].strip()
            if _ticker:
                _ticker = _ticker.lower()
                channel = client.get_channel(news_channel_id)
                articles: list[dict[str, str]] = await tasks_executor.articles_by_ticker(ticker=_ticker)
                _count: int = len(articles)
                mention = message.author.mention
                await channel.send(f"Hi {mention}, I am sending {_count} {_ticker.upper()} Articles to your DM")
                await message.author.send([f"[{article['title']}]({article['link']})" for article in articles])
            else:
                await message.author.send("Please supply the ticker symbols example !articles-by-ticker MSFT")

        except IndexError:
            await message.author.send("Please supply the ticker symbols example !articles-by-ticker MSFT")

    elif message.content.startswith('!articles-by-company'):
        try:
            _company: str = message.content.split(" ")[1].strip()
            if _company:
                _company = _company.lower()
            else:
                await message.author.send("Please supply the Company Name Example !articles-by-company Apple")

        except IndexError:
            await message.author.send("Please supply the Company Name Example !articles-by-company Apple")

    elif message.content.startswith('!articles-by-exchange'):
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

    elif message.content.startswith('!companies-by-exchange'):
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

    elif message.content.startswith('!tickers-by-exchange'):
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

    elif message.content.startswith('!list-publishers'):
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

    elif message.content.startswith('!list-exchanges'):
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


@client.event
async def on_member_join(member):
    # Send a welcome message to the newly joined member
    welcome_message = f"Welcome, {member.mention}! TO EOD-STOCK-API-VERSION-0.0.1"
    await member.send(welcome_message)

    # Perform additional actions if needed


@client.event
async def on_member_remove(member):
    # Perform actions or logging for the departed member
    farewell_message = f"Goodbye, {member.name}! We'll miss you."
    farewell_channel = client.get_channel(news_channel_id)
    await farewell_channel.send(farewell_message)
