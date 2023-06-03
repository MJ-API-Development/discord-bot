import datetime

import discord


client = discord.Client()


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!article-by-uuid'):
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
            else:
                raise ValueError("Invalid ticker")

        except IndexError:
            raise ValueError("Exchange Code Required")

    elif message.content.startswith('!list-publishers'):
        try:
            pass

        except IndexError:
            raise ValueError("Exchange Code Required")

    elif message.content.startswith('!list-exchanges'):
        try:
            pass

        except IndexError:
            raise ValueError("Exchange Code Required")


class TaskScheduler:

    def __init__(self):
        self._discord = discord.Client()


    async def run(self):
        pass


