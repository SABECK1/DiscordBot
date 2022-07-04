import discord
from discord.ext import commands


class HelpCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#OLD; NEEDS TO BE REMADE

    @commands.command(pass_context=True)
    async def helpmusic(self, ctx):
        embed = discord.Embed(title="Music Commands", color=0xa722f0, description='All commands can be used yet again '
                                                                                  'with the prefix "-"')
        embed.add_field(name="```play```",
                        value="Queries and plays a song")
        embed.add_field(name="```pause```", value="Pauses the player")
        embed.add_field(name="```resume```", value="Resumes the player")
        embed.add_field(name="```skip```", value="Skips the current song")
        embed.add_field(name="```queue```", value="Shows the whole queue")
        embed.add_field(name="```clearqueue```", value="Clears the queue of the player")
        embed.add_field(name="```loopqueue```", value="Loops the queue of the player")
        embed.add_field(name="```loop```", value="Loops the current song")
        embed.add_field(name="```volume X```", value="Sets the volume of the player \n"
                                                     "0 =< X =< 100")
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCmds(bot))
