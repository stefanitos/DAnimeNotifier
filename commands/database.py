import aiosqlite
from discord.ext import commands


class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connect_to_db())

    async def connect_to_db(self):
        self.db = await aiosqlite.connect("database/identifier.sqlite")

    async def get_all_anime(self):
        cursor = await self.db.cursor()
        await cursor.execute("SELECT * FROM AnimeSeries")
        return await cursor.fetchall()

    async def add_anime(self, anime_name, anime_title_url):
        cursor = await self.db.cursor()
        await cursor.execute("INSERT INTO AnimeSeries (anime_name, anime_title_url) VALUES (?, ?)",
                             (anime_name, anime_title_url))
        await self.db.commit()

    async def remove_anime(self, anime_name):
        cursor = await self.db.cursor()
        await cursor.execute("DELETE FROM AnimeSeries WHERE anime_name=?", (anime_name,))
        await self.db.commit()

    async def get_anime(self, anime_name):
        cursor = await self.db.cursor()
        await cursor.execute("SELECT * FROM AnimeSeries WHERE anime_name=?", (anime_name,))
        return await cursor.fetchone()

    async def update_last_episode(self, anime_name, last_episode):
        cursor = await self.db.cursor()
        await cursor.execute("UPDATE AnimeSeries SET last_episode=? WHERE anime_name=?", (last_episode, anime_name))
        await self.db.commit()


def setup(bot):
    bot.add_cog(DatabaseCog(bot))
