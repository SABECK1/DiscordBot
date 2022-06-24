import discord
from discord.ext import commands


class HelpCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#OLD; NEEDS TO BE REMADE

    @commands.command(pass_context=True)
    async def helpmusic(self, ctx):
        embed = discord.Embed(title="Music Commands", color=0xa722f0, description='All commands can be used yet again '
                                                                                  'with the prefix "-"\n\r Queues not yet working')
        embed.add_field(name="```play```",
                        value="plays a song if no url given it will search for the most viewed video")
        embed.add_field(name="```pause/resume```", value="pauses and resumes the player")
        embed.add_field(name="```skip```", value="skips the current song")
        embed.add_field(name="```queue```", value="shows the whole queue")
        embed.add_field(name="```plist```", value="Under development")
        embed.add_field(name="```clearQ```", value="Clears the Queue of the player")
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCmds(bot))
