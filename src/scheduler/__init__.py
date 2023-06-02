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
            count = int(count)
            # TODO - send request to endpoint and return articles
        else:

            pass
    e


class TaskScheduler:

    def __init__(self):
        self._discord = discord.Client()


    async def run(self):
        pass


