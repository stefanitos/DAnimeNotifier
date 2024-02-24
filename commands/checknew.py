# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands, tasks
import asyncio
import time

from main import TEST_GUILDS


class CheckNew(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.db = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.db = self.bot.get_cog("DatabaseCog")
        if self.db is not None:
            self.check_new.start()
        else:
            print("Couldn't find DatabaseCog!")

    @tasks.loop(seconds=10)
    async def check_new(self):
        start = time.time()
        async with AnitakuWrapper() as anitaku:
            anime_list = await self.db.get_anime_list()
            print(anime_list)

            # latest episode for each anime
            latest_episodes = {}

            for anime in anime_list:
                anime_id, anime_name, anime_name_url, last_episode, image_url = anime
                latest_episode = await anitaku.get_new_episode(anime_name_url)
                latest_episodes[anime_name_url] = latest_episode

                print(f"{anime_name} - {last_episode} => {latest_episode}")

                if latest_episode > last_episode:
                    await self.db.update_last_episode(anime_name_url, latest_episode)


                    message = f"New episode for {anime_name} is available!"


                    notification_data = await self.db.get_anime_notification_data()
                    relevant_channels = [item for item in notification_data if item[0] == anime_name_url]

                    await asyncio.gather(*[self.send_message(channel[1], channel[2], message) for channel in relevant_channels])

        print(time.time() - start)

    async def send_message(self, guild_id, channel_id, message):
        guild = self.bot.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.send(message)

    @check_new.before_loop
    async def before_check_new(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(CheckNew(bot))
