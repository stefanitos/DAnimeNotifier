# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands

from main import TEST_GUILDS


async def list_to_num_string(anime_list):
    if isinstance(anime_list[0], dict):
        anime_list = [anime["name"] for anime in anime_list]
    formatted_list = [f"{i + 1}. {anime}" for i, anime in enumerate(anime_list)]
    return "\n".join(formatted_list)


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="remove", description="Remove anime command", guild_ids=TEST_GUILDS)
    async def remove(self, ctx: ApplicationContext):
        db = self.bot.get_cog("DatabaseCog")
        channel = ctx.channel

        if channel.category.name != "Anime Notifications":
            await ctx.respond("This command can only be used in the Anime Notifications category!", ephemeral=True)
            return





def setup(bot):
    bot.add_cog(Remove(bot))
