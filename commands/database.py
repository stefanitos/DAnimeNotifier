import aiosqlite
from discord.ext import commands
from discord.commands import ApplicationContext


class DatabaseCog(commands.Cog):
    """Database creaation script:
create table AnimeChannelLink
(
    anime_id   INTEGER
        references AnimeSeries,
    channel_id INTEGER
        references Channel,
    primary key (anime_id, channel_id)
);
create table AnimeSeries
(
    anime_id        INTEGER
        primary key autoincrement,
    anime_name      TEXT    not null,
    anime_title_url TEXT    not null
        unique,
    last_episode    INTEGER not null
);
create table Channel
(
    channel_id INTEGER not null
        primary key
        unique,
    guild_id   INTEGER
        references Guild
);
create table Guild
(
    guild_id   INTEGER not null
        primary key
        unique,
    guild_name TEXT    not null
);
"""

    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connect_to_db())

    async def connect_to_db(self):
        self.db = await aiosqlite.connect("database/identifier.sqlite")

    async def guild_has_anime(self, guild_id, anime_name_url) -> bool:
        cursor = await self.db.cursor()
        await cursor.execute(
            "SELECT * FROM AnimeChannelLink WHERE anime_id = (SELECT anime_id FROM AnimeSeries WHERE anime_title_url = ?) AND channel_id = (SELECT channel_id FROM Channel WHERE guild_id = ?)",
            (anime_name_url, guild_id)
        )
        return bool(await cursor.fetchone())

    async def register_guild(self, guild_id, guild_name):
        cursor = await self.db.cursor()
        await cursor.execute("INSERT INTO Guild (guild_id, guild_name) VALUES (?, ?)", (guild_id, guild_name))
        await self.db.commit()
        print(f"Registered {guild_name} with id {guild_id}")

    async def get_all_guild_anime(self, guild_id):
        cursor = await self.db.cursor()
        await cursor.execute(
            "SELECT anime_name, anime_title_url, last_episode FROM AnimeSeries WHERE anime_id IN (SELECT anime_id FROM AnimeChannelLink WHERE channel_id IN (SELECT channel_id FROM Channel WHERE guild_id = ?))",
            (guild_id,)
        )
        return await cursor.fetchall()

    async def add_anime(self, guild_id, channel_id, search_results: dict, last_episode):
        cursor = await self.db.cursor()
        await cursor.execute(
            "INSERT INTO AnimeSeries (anime_name, anime_title_url, last_episode) VALUES (?, ?, ?)",
            (search_results["name"], search_results["url"], last_episode))

        anime_id = await self.get_anime_id(search_results["url"])

        await cursor.execute(
            "INSERT INTO Channel (channel_id, guild_id) VALUES (?, ?)", (channel_id, guild_id)
        )

        await cursor.execute(
            "INSERT INTO AnimeChannelLink (anime_id, channel_id) VALUES (?, ?)",
            (anime_id, channel_id)
        )

        await self.db.commit()

    # remove anime from animeseries and animechannellink and the channel from channel
    async def remove_anime(self, anime_name_url, guild_id):
        anime_id = await self.get_anime_id(anime_name_url)
        cursor = await self.db.cursor()
        await cursor.execute("DELETE FROM AnimeChannelLink WHERE anime_id = ?", (anime_id,))
        await cursor.execute("DELETE FROM AnimeSeries WHERE anime_id = ?", (anime_id,))
        await cursor.execute("DELETE FROM Channel WHERE channel_id = ?", (anime_id,))
        await self.db.commit()

    async def get_anime_id(self, anime_name_url):
        cursor = await self.db.cursor()
        await cursor.execute("SELECT anime_id FROM AnimeSeries WHERE anime_title_url = ?", (anime_name_url,))
        return (await cursor.fetchone())[0]


def setup(bot):
    bot.add_cog(DatabaseCog(bot))
