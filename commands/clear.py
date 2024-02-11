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
        cursor = await self.db.cursor()
        await cursor.execute("DELETE FROM AnimeSeries")
        await cursor.execute("DELETE FROM Channel")
        await cursor.execute("DELETE FROM AnimeChannelLink")
        await self.db.commit()
        await ctx.respond("Cleared all tables!")


def setup(bot):
    bot.add_cog(Clear(bot))
