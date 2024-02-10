# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext, Option
from discord.ext import commands
from discord import Embed
from asyncio import TimeoutError as AsyncTimeoutError

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
        all_guild_anime = await db.get_all_guild_anime(
            ctx.guild.id)  # [('Naruto (Shinsaku Anime)', 'naruto-shinsaku-anime', 0), ('Sousou no Frieren', 'sousou-no-frieren', 21)]
        if not all_guild_anime:
            await ctx.respond("No anime found in this server!")
            return

        anime_list = await list_to_num_string(all_guild_anime)
        await ctx.respond(f"Which anime would you like to remove?\n{anime_list}")

        def check(m):
            return (
                    m.author == ctx.author and
                    m.channel == ctx.channel and
                    m.content.isdigit() and
                    int(m.content) in range(1, len(all_guild_anime) + 1)
            )

        try:
            response = await self.bot.wait_for("message", check=check, timeout=60)
        except AsyncTimeoutError:
            await ctx.respond("You took too long to respond!")
            return

        anime_name_url = all_guild_anime[int(response.content) - 1][1]
        anime_name = all_guild_anime[int(response.content) - 1][0]

        channel = ctx.guild.get_channel(await db.get_channel_id(anime_name_url, ctx.guild.id))
        await channel.delete()
        await db.remove_anime(anime_name_url, ctx.guild.id)
        await ctx.respond(f"Removed {anime_name} from this server!")


def setup(bot):
    bot.add_cog(Remove(bot))
