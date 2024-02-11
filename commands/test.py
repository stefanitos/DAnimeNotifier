# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands
import time


from main import TEST_GUILDS


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.db = bot.get_cog("DatabaseCog")

    @commands.slash_command(name="test", aliases=["t"], description="Test command", guild_ids=TEST_GUILDS)
    async def test(self, ctx: ApplicationContext):
        start = time.time()
        await ctx.respond("Test command!")
        anim_list = await self.db.get_anime_list()
        print(anim_list)
        print(time.time() - start)


def setup(bot):
    bot.add_cog(Test(bot))
