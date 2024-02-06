import aiosqlite
from discord.ext import commands


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
    anime_name      TEXT not null,
    anime_title_url TEXT not null
        unique,
    last_episode    INTEGER not null
);

create table Channel
(
    channel_id   INTEGER not null unique,
    guild_id     INTEGER
        references Guild,
    primary key (channel_id)
);

create table Guild
(
    guild_id   INTEGER not null unique,
    guild_name TEXT not null,
    primary key (guild_id)
);
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connect_to_db())

    async def connect_to_db(self):
        self.db = await aiosqlite.connect("database/identifier.sqlite")

    async def register_guild(self, guild_id, guild_name):
        cursor = await self.db.cursor()
        await cursor.execute("INSERT INTO Guild (guild_id, guild_name) VALUES (?, ?)", (guild_id, guild_name))
        await self.db.commit()
        print(f"Registered {guild_name} with id {guild_id}")

    async def get_all_anime(self):
        cursor = await self.db.cursor()
        await cursor.execute("SELECT * FROM AnimeSeries")
        return await cursor.fetchall()

    async def add_anime(self, guild_id, channel_id, search_results: dict, last_episode):
        """
        search_results:
            {
                "name": name,
                "url": href.split("/category/")[-1],
                "full_url": f"{self.BASE_URL}{href}",
                "href": href,
                "image": image,
            }
        """

        cursor = await self.db.cursor()
        await cursor.execute(
            "INSERT INTO AnimeSeries (anime_name, anime_title_url, last_episode) VALUES (?, ?, ?)",
            (search_results["name"], search_results["url"], 0))

        await cursor.execute(
            "INSERT INTO Channel (channel_id, guild_id) VALUES (?, ?)",
            (channel_id, guild_id)
        )

        anime_id = cursor.lastrowid
        await cursor.execute(
            "INSERT INTO AnimeChannelLink (anime_id, channel_id) VALUES (?, ?)",
            (anime_id, channel_id)
        )

        await self.db.commit()


def setup(bot):
    bot.add_cog(DatabaseCog(bot))
