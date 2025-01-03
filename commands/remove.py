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
        self.bot: commands.Bot = bot
        self.db = bot.get_cog("DatabaseCog")

    @commands.slash_command(name="remove", description="Remove anime command", guild_ids=TEST_GUILDS)
    async def remove(self, ctx: ApplicationContext):
        channel = ctx.channel
        channel_id = channel.id

        is_anime_channel = await self.db.is_anime_channel(channel_id)
        if not is_anime_channel:
            await ctx.respond("This channel is not an anime channel!", ephemeral=True)
            return

        await self.db.remove_anime(channel_id)

        await channel.delete()


def setup(bot):
    bot.add_cog(Remove(bot))
