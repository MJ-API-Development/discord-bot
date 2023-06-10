import functools
from discord import Message


def mention_wrapper(func):
    @functools.wraps(func)
    async def wrapped(self, message: Message):
        mention = message.author.mention
        if mention not in self._rate_limit_flags:
            self._rate_limit_flags.add(message.author.mention)
            response = await func(self, message)
            self._rate_limit_flags.remove(message.author.mention)
            return response
        else:
            await message.reply(f"{mention} Wait until your previous command finished executing")

    return wrapped
