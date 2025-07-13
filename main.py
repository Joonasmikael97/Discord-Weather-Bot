import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import webserver


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
weather_api_key = os.getenv('WEATHER_API_KEY')


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online.")

@bot.command()
async def weather(ctx, *, city: str = None):
    if city is None:
        await ctx.send("🌍 Please provide a city name. Example: !weather London")
        return

    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}"

    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"❌ Could not find weather for **{city}**.")
            return

        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        feels_like = data["current"]["feelslike_c"]
        condition = data["current"]["condition"]["text"]
        icon_url = f"https:{data['current']['condition']['icon']}"

        await ctx.send(
            f"🌤️ **Weather in {location}, {country}**\n"
            f"Condition: **{condition}**\n"
            f"Temperature: **{temp_c}°C**\n"
            f"Feels like: **{feels_like}°C**\n"
        )

    except Exception as e:
        await ctx.send("⚠️ Failed to fetch weather.")
        print(f"Error fetching weather: {e}")
        
        
webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
