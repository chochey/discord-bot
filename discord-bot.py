import discord
from discord.ext import commands
import bot_config
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Define your initial extensions as a list of strings
initial_extensions = [
    'cogs.palworld_commands',
    'cogs.satisfactory_commands',
]

# Inside your main bot script, when loading extensions
async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Successfully loaded {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}. Reason: {e}")


async def main():
    await load_extensions()
    await bot.start(bot_config.BOT_TOKEN)  # Start the bot with the token from your bot_config
print(f"Successfully loaded Bot Token")
if __name__ == '__main__':
    asyncio.run(main())
