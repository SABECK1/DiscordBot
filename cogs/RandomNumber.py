import random

from discord.ext import commands


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def rand(self,ctx):
        args = ctx.message.content.split(" ")
        print(args)

        if len(args) == 3:
            firstnumber = int(args[1])
            secondnumber = int(args[2]) + 1
            num = random.choice(range(firstnumber, secondnumber))
            await ctx.message.channel.send("Your number is {}".format(num))
        else: await ctx.send("You need to use two seperate numbers")

def setup(bot):
    bot.add_cog(Random(bot))