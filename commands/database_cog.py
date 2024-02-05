from discord.ext import commands
from identifier import DatabaseWrapper


class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseWrapper('identifier.sqlite')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')
        await self.db.connect()

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.db.close()

    # Define methods for interacting with the database here
    # For example:
    @commands.command()
    async def add_anime(self, ctx, anime_name: str, anime_title_url: str):
        async with self.db.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO AnimeSeries (anime_name, anime_title_url) VALUES (?, ?)",
                                 (anime_name, anime_title_url))
            await self.db.conn.commit()
        await ctx.send(f'Anime {anime_name} added successfully!')

    # More commands that interact with the database...


def setup(bot):
    bot.add_cog(DatabaseCog(bot))
