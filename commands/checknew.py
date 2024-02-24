# noinspection PyUnresolvedReferences
from AnitakuWrapper import AnitakuWrapper
from discord.commands import ApplicationContext
from discord.ext import commands, tasks
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

    @tasks.loop(seconds=10000000)
    async def check_new(self):
        start = time.time()
        async with AnitakuWrapper() as anitaku:
            anim_list = await self.db.get_anime_list()  # [(7, 'Sousou no Frieren', 'sousou-no-frieren', 22, 'https://gogocdn.net/cover/sousou-no-frieren-1696000134.png'), (8, 'Ore dake Level Up na Ken', 'ore-dake-level-up-na-ken', 6, 'https://gogocdn.net/cover/ore-dake-level-up-na-ken-1704247746.png')]
            for anime in anim_list:
                anime_id, anime_name, anime_name_url, last_episode, _ = anime

                latest_episode = await anitaku.get_new_episode(anime_name_url)
                if latest_episode > last_episode:
                    print(f"{anime_name} has a new episode! {last_episode} -> {latest_episode}")
                    print(await self.db.get_guilds_with_anime_channel(anime_name_url))
                    await self.db.update_last_episode(anime_id, latest_episode)

            print(anim_list)
        print(time.time() - start)

    @check_new.before_loop
    async def before_check_new(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(CheckNew(bot))
