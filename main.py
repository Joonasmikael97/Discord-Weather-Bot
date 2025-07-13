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
        response.raise_for_status()
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

        print(f"DEBUG: Säätila API:sta: {condition}")  # Tulostetaan debugiksi

        weather_quotes = {
            "rain": "Vettä tulee kuin Esterin sieltä!",
            "light rain": "Kevyt sade, mutta muista silti sateenvarjo!",
            "moderate rain": "Sade hakkaa kuin syksyinen vastatuuli – pysy sisällä jos voit.",
            "heavy rain": "Rankka sade päällä, varo kastumista.",
            "shower": "Sateenkuuroja voi tulla yllättäen.",
            "sunny": "Aurinko paistaa ja linnut laulaa – ainakin vielä!",
            "partly cloudy": "Vähän pilvistä, mutta ei anneta sen haitata – melkein kuin lomakeli!",
            "cloudy": "Pilviä on kuin marraskuussa, mutta eipä sada.",
            "overcast": "Synkkää kuin maanantai-aamu – ota kahvia.",
            "snow": "Lunta tupaan! Muista pipot ja hanskat.",
            "light snow": "Kevyt lumipeite – juuri sopivaa lumienkeleihin.",
            "fog": "Niin sumuista, että hyvä kun näkee nenänsä.",
            "mist": "Sumua tai usvaa – aja varoen.",
            "thunderstorm": "Ukkosta ilmassa – nyt ei kannata mennä lennättämään leijaa."
        }

        condition_lower = condition.lower()
        quote = "Sää kuin sää – asenteella selviää!"
        for key, message in weather_quotes.items():
            if key in condition_lower:
                quote = message
                break

        embed = discord.Embed(
            title=f"Sää {location}, {country}",
            description=f"📌 {condition}\n🌡️ {temp_c}°C (Tuntuu kuin {feels_like}°C)\n\n _{quote}_",
            color=0x1abc9c
        )
        embed.set_thumbnail(url=icon_url)

        await ctx.send(embed=embed)

    except requests.exceptions.RequestException as e:
        await ctx.send("⚠️ Failed to fetch weather data.")
        print(f"Request error: {e}")
    except Exception as e:
        await ctx.send("⚠️ An unexpected error occurred.")
        print(f"Unexpected error: {e}")

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
