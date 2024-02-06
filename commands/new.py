from discord.commands import ApplicationContext
from discord.ext import commands
from discord import Embed, Option
from asyncio import TimeoutError as AsyncTimeoutError

from main import TEST_GUILDS
from AnitakuWrapper import AnitakuWrapper


# Helper functions
def list_to_num_string(anime_list):
    if isinstance(anime_list[0], dict):
        anime_list = [anime["name"] for anime in anime_list]
    formatted_list = [f"{i + 1}. {anime}" for i, anime in enumerate(anime_list)]
    return "\n".join(formatted_list)


async def create_category(ctx):
    for category in ctx.guild.categories:
        if category.name == "Anime Notifications":
            return category
    return await ctx.guild.create_category("Anime Notifications")


class New(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="new", description="Create a new channel ", guild_ids=TEST_GUILDS)
    async def new(self, ctx: ApplicationContext, anime_name: Option(str, "The name of the anime you want to add")):
        database = self.bot.get_cog("DatabaseCog")
        await ctx.defer(ephemeral=True)
        async with AnitakuWrapper() as anitaku:
            anime_search = await anitaku.search(anime_name)

            if not anime_search:
                await ctx.respond(f"'{anime_name}' not found!", ephemeral=True)
                return

            embed_list = [
                Embed(title=f"{i + 1}. {anime['name']}", url=anime["full_url"]).set_thumbnail(url=anime["image"]) for
                i, anime in enumerate(anime_search[:10])]

            await ctx.respond(embeds=embed_list)

            def check(m):
                return (
                        m.author == ctx.author and
                        m.channel == ctx.channel and
                        m.content.isdigit() and
                        int(m.content) in range(1, len(anime_search) + 1)
                )

            try:
                response = await self.bot.wait_for("message", check=check, timeout=60)
            except AsyncTimeoutError:
                await ctx.respond("You took too long to respond!", ephemeral=True)
                return

            selection = int(response.content) - 1
            selected_anime = anime_search[selection]
            print(selected_anime)

            current_episode = await anitaku.get_new_episode(selected_anime["href"])
            print(current_episode)

            category = await create_category(ctx)
            new_channel = await ctx.guild.create_text_channel(selected_anime["name"], category=category)
            await database.add_anime(ctx.guild.id, new_channel.id, selected_anime, current_episode)

            await ctx.respond(f"Created channel for {selected_anime['name']}", ephemeral=True)


def setup(bot):
    bot.add_cog(New(bot))
