import random

import discord
from discord.ext import commands


league_champions = ("Aatrox", "Ahri", "Akali", "Alistar", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe",
                    "AurelionSol", "Azir", "Bard", "Blitzcrank", "Brand", "Braum", "Caitlyn", "Camille",
                    "Cassiopeia", "Cho'Gath", "Corki", "Darius", "Diana", "DrMundo", "Draven", "Ekko", "Elise",
                    "Evelynn", "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar",
                    "Gragas", "Graves", "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan,IV",
                    "Jax", "Jayce", "Jhin", "Jinx", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina",
                    "Kayle", "Kayn", "Kennen", "Kha'Zix",
                    "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee,Sin", "Leona", "Lissandra", "Lucian", "Lulu", "Lux",
                    "Malphite", "Malzahar", "Maokai", "MasterYi",
                    "MissFortune", "Mordekaiser", "Morgana", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee",
                    "Nocturne", "Nunu&Willump", "Olaf", "Orianna",
                    "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan", "Rammus", "Rek'Sai", "Renekton",
                    "Rengar", "Riven", "Rumble", "Ryze", "Sejuani",
                    "Senna", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner", "Sona", "Soraka",
                    "Swain", "Sylas", "Syndra", "TahmKench", "Taliyah", "Talon", "Taric", "Teemo",
                    "Thresh", "Tristana", "Trundle", "Tryndamere", "Twisted,Fate", "Twitch", "Udyr", "Urgot", "Varus",
                    "Vayne", "Veigar", "Vel'Koz", "Vi", "Viktor",
                    'Vladimir', "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "XinZhao", "Yasuo", "Yorick",
                    "Yuumi", "Zac", "Zed", "Ziggs",
                    "Zilean", "Zoe", "Zyra", "Urf")


class League(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Roles =  ("Top", "Jungle", "Mid", "ADC", "Support")

    @commands.command(pass_context=True, aliases=["rr"])
    async def RR(self, ctx):
        RolledRole = random.choice(self.Roles)

        await ctx.message.channel.send("Your role is: {}".format(RolledRole))

    @commands.command(pass_context=True)
    async def WQ(self, ctx):
        RolledChampion = random.choice(league_champions)


        Championpath = "./Championbanner/"
        Championfile = Championpath + RolledChampion + "Square.png.jpeg"
        RolledRole = random.choice(self.Roles)

        embed = discord.Embed(title="Your Champion is: {}".format(RolledChampion), color=0x00ff00,
                              description="You are playing {} {}".format(RolledChampion, RolledRole))  # creates embed
        file = discord.File(Championfile, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)




def setup(bot):
    bot.add_cog(League(bot))