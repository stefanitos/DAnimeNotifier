# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands


from main import TEST_GUILDS


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="test", aliases=["t"], description="Test command", guild_ids=TEST_GUILDS)
    async def test(self, ctx: ApplicationContext):
        await ctx.respond("Test command")
        db = self.bot.get_cog("DatabaseCog")
        print(await db.get_all_anime())


def setup(bot):
    bot.add_cog(Test(bot))
