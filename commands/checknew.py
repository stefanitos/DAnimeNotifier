# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands, tasks
from discord import Embed
import asyncio
import time
from discord import Colour
from datetime import datetime


class NewEpisodeEmbed(Embed):
    def __init__(self, anime_name: str, episode: int, image_url: str):
        super().__init__(
            title=anime_name,
            description=f"Episode {episode}",
            color=Colour.green(),  # Use Colour.green() instead of 0x00ff00 for better readability
            timestamp=datetime.utcnow()  # Add timestamp
        )
        self.set_image(url=image_url)
        self.set_footer(text="Anime Updates")  # Add a footer if you want


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

    @tasks.loop(minutes=1)
    async def check_new(self):
        start = time.time()
        async with AnitakuWrapper() as anitaku:
            anime_list = await self.db.get_anime_list()
            # print(anime_list) # [(13, 'Sousou no Frieren', 'sousou-no-frieren', 1, 'https://gogocdn.net/cover/sousou-no-frieren-1696000134.png')]

            for anime in anime_list:
                anime_id, anime_name, anime_name_url, last_episode, image_url = anime
                latest_episode = await anitaku.get_new_episode(anime_name_url)
                # print(f"{anime_name} - {last_episode} => {latest_episode}")

                if latest_episode > last_episode:
                    message = f"New episode for {anime_name} is available!"

                    channels = await self.db.get_channels_to_notify(anime_name_url)

                    # print(channels) # [(1211075970337865790,), (1211076012142624838,)]

                    # Send notifications to the channeks at the same time  
                    await asyncio.gather(
                        *[self.send_new_episode_notification(channel[0], anime_name, latest_episode, image_url) for
                          channel in channels])

                    await self.db.update_last_episode(anime_name_url, latest_episode)

        print(time.time() - start)

    async def send_new_episode_notification(self, channel_id, anime_name, episode, image_url):
        channel = self.bot.get_channel(channel_id)
        await channel.send(embed=NewEpisodeEmbed(anime_name, episode, image_url))

    @check_new.before_loop
    async def before_check_new(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(CheckNew(bot))
