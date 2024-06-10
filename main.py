from dotenv import dotenv_values
from discord import Bot, Intents
import os

envs = dotenv_values(".env")
MODE = envs["MODE"]
TEST_GUILDS = [831193807734571029, 778250495038980137, 1204429451773878312]

if MODE == "PI":
    BOT_TOKEN = envs["BOT_TOKEN"]
else:
    BOT_TOKEN = envs["SECOND_TOKEN"]

bot = Bot(intents=Intents.all())

bot.load_extension("commands.database")

for filename in os.listdir("./commands"):
    if filename.endswith(".py") and not filename.startswith("_"):
        if not filename.startswith("database"):
            bot.load_extension(f"commands.{filename[:-3]}")


@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.slash_command(name="reload", description="Reload a cog", guild_ids=TEST_GUILDS)
async def reload(ctx, cog: str):
    bot.reload_extension(f"commands.{cog}")
    await ctx.respond(f"Reloaded {cog}")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
