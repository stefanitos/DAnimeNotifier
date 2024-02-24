# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands


from main import TEST_GUILDS


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.db = bot.get_cog("DatabaseCog")

    @commands.slash_command(name="clear", description="Clear all table items", guild_ids=TEST_GUILDS)
    async def clear(self, ctx: ApplicationContext):
        await self.db.clear_all()
        await ctx.respond("Cleared all items!")


def setup(bot):
    bot.add_cog(Clear(bot))
