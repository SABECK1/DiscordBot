import os

import aiohttp
import discord
import numpy as np
import requests
from PIL import Image, ImageChops
from discord.ext import commands


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = None




    @commands.command()
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as CS:
            async with CS.get("http://aws.random.cat//meow") as r:
                File = await r.json()
                embed = discord.Embed(title="Random Cat Picture")

                embed.set_image(url=File['file'])
                embed.set_footer(text="Images/GIFS made possible by http://random.cat/")
                await ctx.send(embed=embed)

    @commands.command()
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as CS:
            async with CS.get("https://random.dog/woof.json") as r:
                File = await r.json()
                embed = discord.Embed(title="Random Dog Picture")

                embed.set_image(url=File['url'])
                embed.set_footer(text="Images/GIFS made possible by http://random.dog/")
                await ctx.send(embed=embed)

    @commands.command()
    async def diceify(self, ctx, member: discord.Member):

        url = member.avatar_url

        response = requests.get(url=url, stream=True).raw

        im = Image.open(response).convert("L")

        na = np.array(im)

        out = np.full(na.shape, 255, dtype=np.uint8)

        out[1::3, 0::3] = na[1::3, 0::3]
        out[3::3, 1::3] = na[3::3, 1::3]
        out[5::3, 2::3] = na[5::3, 2::3]


        Image.fromarray(out).save("DiceEdit.png")
        await ctx.channel.send(file=discord.File('DiceEdit.png'))
        os.remove("DiceEdit.png")

    @commands.command()
    async def invert(self, ctx, member: discord.Member):
        url = member.avatar_url
        response = requests.get(url=url, stream=True).raw
        im = Image.open(response).convert("RGB")
        inv_img = ImageChops.invert(im)


        inv_img.save("InvertEdit.png")
        await ctx.send(file=discord.File("InvertEdit.png"))



def setup(bot):
    bot.add_cog(Images(bot))
