from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.get_cog("DatabaseCog")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined {guild.name} with {guild.member_count} members!")

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Hello! I am a bot created by Anitaku#0001. Use /help to see the commands I can do!")
                break

        await self.database.register_guild(guild.id, guild.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"Left {guild.name} with {guild.member_count} members!")


def setup(bot):
    bot.add_cog(Listeners(bot))
