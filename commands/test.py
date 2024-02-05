# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands
from .database_cog import DatabaseCog

from main import TEST_GUILDS


class Test(DatabaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="test", aliases=["t"], description="Test command", guild_ids=TEST_GUILDS)
    async def test(self, ctx: ApplicationContext):
        await ctx.respond("Test command")
        await super().add_anime("Test", "https://www.example.com")


def setup(bot):
    bot.add_cog(Test(bot))
