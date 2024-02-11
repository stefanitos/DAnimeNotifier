from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.database = bot.get_cog("DatabaseCog")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined {guild.name} with {guild.member_count} members!")

        await self.database.register_guild(guild.id, guild.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"Left {guild.name} with {guild.member_count} members!")


def setup(bot):
    bot.add_cog(Listeners(bot))
