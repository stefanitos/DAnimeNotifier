import aiosqlite
from discord.ext import commands


class DatabaseCog(commands.Cog):
    """Database creation script:
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
            anime_title_url TEXT    not null,
            last_episode    INTEGER not null,
            image           TEXT default NULL
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
        await self.db.commit()

    async def execute_sql(self, sql, params=None):
        async with self.db.cursor() as cursor:
            await cursor.execute(sql, params)
            await self.db.commit()

    async def fetch_one(self, sql, params=None):
        async with self.db.cursor() as cursor:
            await cursor.execute(sql, params)
            return await cursor.fetchone()

    async def fetch_all(self, sql, params=None):
        async with self.db.cursor() as cursor:
            await cursor.execute(sql, params)
            return await cursor.fetchall()

    async def guild_has_anime(self, guild_id, anime_name_url) -> bool:
        select_exists_anime_in_guild_sql = """
        SELECT EXISTS(
            SELECT  1 FROM AnimeChannelLink
            INNER JOIN AnimeSeries ON AnimeSeries.anime_id = AnimeChannelLink.anime_id
            INNER JOIN Channel ON Channel.channel_id = AnimeChannelLink.channel_id
            WHERE AnimeSeries.anime_title_url = ? AND Channel.guild_id = ?
        );
        """
        return bool(await self.fetch_one(select_exists_anime_in_guild_sql, (anime_name_url, guild_id)))

    async def register_guild(self, guild_id, guild_name):
        insert_guild_sql = "INSERT INTO Guild (guild_id, guild_name) VALUES (?, ?)"
        await self.execute_sql(insert_guild_sql, (guild_id, guild_name))
        print(f"Registered {guild_name} with id {guild_id}")

    async def get_all_guild_anime(self, guild_id):
        select_all_anime_in_guild_sql = """
        SELECT AnimeSeries.anime_name, AnimeSeries.anime_title_url, AnimeSeries.last_episode
        FROM AnimeSeries
        INNER JOIN AnimeChannelLink ON AnimeSeries.anime_id = AnimeChannelLink.anime_id
        INNER JOIN Channel ON Channel.channel_id = AnimeChannelLink.channel_id
        WHERE Channel.guild_id = ?;
        """
        return await self.fetch_all(select_all_anime_in_guild_sql, (guild_id,))

    async def add_anime(self, guild_id, channel_id, search_results: dict, last_episode):
        # search_results =
        # {
        #     "name": "Sousou no Frieren",
        #     "url": "sousou-no-frieren",
        #     "full_url": f"https://anitaku.to//category/sousou-no-frieren",
        #     "href": "/category/sousou-no-frieren",
        #     "image": "https://gogocdn.net/cover/sousou-no-frieren-1696000134.png",
        # }
        select_anime_id_by_url_sql = "SELECT anime_id FROM AnimeSeries WHERE anime_title_url = ?"
        anime_id = await self.fetch_one(select_anime_id_by_url_sql, (search_results["url"],))
        if anime_id is None:
            insert_new_anime_sql = """
            INSERT INTO AnimeSeries (anime_name, anime_title_url, last_episode, image)
            VALUES (?, ?, ?, ?);
            """
            await self.execute_sql(insert_new_anime_sql, (
                search_results["name"], search_results["url"], last_episode, search_results["image"]))
            anime_id = await self.get_anime_id(search_results["url"])
        else:
            anime_id = anime_id[0]

        insert_or_ignore_channel_sql = "INSERT OR IGNORE INTO Channel (channel_id, guild_id) VALUES (?, ?)"
        await self.execute_sql(insert_or_ignore_channel_sql, (channel_id, guild_id))

        print(anime_id, channel_id)
        insert_or_ignore_anime_channel_link_sql = "INSERT OR IGNORE INTO AnimeChannelLink (anime_id, channel_id) VALUES (?, ?)"
        await self.execute_sql(insert_or_ignore_anime_channel_link_sql, (anime_id, channel_id))

    async def remove_anime(self, anime_name_url, guild_id):
        delete_anime_channel_link_sql = """
        DELETE FROM AnimeChannelLink
        WHERE anime_id = (SELECT anime_id FROM AnimeSeries WHERE anime_title_url = ?)
        AND channel_id IN (SELECT channel_id FROM Channel WHERE guild_id = ?);
        """
        await self.execute_sql(delete_anime_channel_link_sql, (anime_name_url, guild_id))

        delete_unused_channels_sql = "DELETE FROM Channel WHERE channel_id NOT IN (SELECT channel_id FROM AnimeChannelLink)"
        await self.execute_sql(delete_unused_channels_sql, ())

        delete_unused_anime_series_sql = "DELETE FROM AnimeSeries WHERE anime_id NOT IN (SELECT anime_id FROM AnimeChannelLink)"
        await self.execute_sql(delete_unused_anime_series_sql, ())

    async def get_anime_id(self, anime_name_url):
        select_anime_id_by_url_sql = "SELECT anime_id FROM AnimeSeries WHERE anime_title_url = ?"
        result = await self.fetch_one(select_anime_id_by_url_sql, (anime_name_url,))
        if result is not None:
            return result[0]  # Return the first element of the tuple
        return None  # Or handle the case where the anime_id is not found

    async def get_channel_id(self, anime_name_url, guild_id):
        select_channel_id_by_anime_and_guild_sql = """
        SELECT Channel.channel_id
        FROM AnimeChannelLink
        INNER JOIN AnimeSeries ON AnimeSeries.anime_id = AnimeChannelLink.anime_id
        INNER JOIN Channel ON Channel.channel_id = AnimeChannelLink.channel_id
        WHERE AnimeSeries.anime_title_url = ? AND Channel.guild_id = ?;
        """
        return await self.fetch_one(select_channel_id_by_anime_and_guild_sql, (anime_name_url, guild_id))


def setup(bot):
    bot.add_cog(DatabaseCog(bot))
