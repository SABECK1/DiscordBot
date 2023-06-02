import asyncio
import discord
from discord.ext import commands


class Serveradministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @commands.command(pass_context=True)
    async def createInvite(self, ctx):
        invitelink = await discord.abc.GuildChannel.create_invite(ctx.message.channel, reason="Temporary Invite",
                                                                  temporary=True)
        await ctx.send(invitelink)

    @commands.command(pass_context=True)
    async def clearchat(self, ctx):
        if ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
            args = ctx.message.content.split(' ')
            if len(args) == 2:
                if args[1].isdigit():
                    deleted = await ctx.message.channel.purge(limit=int(args[1]) + 1)
                    await ctx.message.channel.send('{} Messages deleted.'.format(len(deleted) - 1))
        else:
            await ctx.send("You don't have permission to do that!")

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f'{member} has been kicked!')

        except:
            await ctx.send("You don't have the permission to do that!")

    @commands.command(pass_context=True)
    async def msg(self, ctx):
        await ctx.message.channel.purge(limit=1)

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member} has been banned!')
        except:
            await ctx.send("You don't have the permission to do that!")

    @commands.command(pass_context=True, aliases=["CREATEVOICE"])
    async def createvoice(self, ctx):
        await ctx.message.channel.purge(limit=1)
        args = ctx.message.content.split(" ")
        VoiceChannelCategory = discord.utils.get(ctx.message.guild.categories, name="Custom Voicechannels")

        if VoiceChannelCategory is None:
            await ctx.guild.create_category("Custom Voicechannels")
            VoiceChannelCategory = discord.utils.get(ctx.message.guild.categories, name="Custom Voicechannels")
        if len(args) == 1:
            await ctx.message.guild.create_voice_channel("{}".format(ctx.message.author.name),
                                                         category=VoiceChannelCategory)
            await ctx.send("Your voicechannel \"{}\" has been created".format(ctx.message.author.name),
                           delete_after=20.0)
        elif len(args) == 2 and args[1].isnumeric():
            await ctx.message.guild.create_voice_channel("{}".format(ctx.message.author.name),
                                                         category=VoiceChannelCategory, user_limit=args[1])
            await ctx.send("Your voicechannel \"{}\" has been created".format(ctx.message.author.name),
                           delete_after=20.0)
        else:
            if not args[1].isnumeric():
                await ctx.send("\"{}\" is not an integer".format(args[1]))
        if len(args) > 2:
            await ctx.send("Dude not so much")
        VoiceChannelCategory = discord.utils.get(ctx.message.guild.categories, name="Custom Voicechannels")
        channels = discord.utils.get(ctx.message.guild.voice_channels, category=VoiceChannelCategory,
                                     name=ctx.message.author.name)
        members = discord.utils.get(channels.members)
        inactivechannelsearch = True
        while inactivechannelsearch:
            await asyncio.sleep(10)
            if not members:
                deletechannels = discord.utils.get(ctx.guild.voice_channels, category=VoiceChannelCategory)

                await deletechannels.delete()

    @commands.command(pass_context=True)
    async def deletevoice(self, ctx):
        VoiceChannelCategory = discord.utils.get(ctx.message.guild.categories, name="Custom Voicechannels")
        channels = discord.utils.get(ctx.message.guild.voice_channels, category=VoiceChannelCategory,
                                     name=ctx.message.author.name)
        if not channels:
            await ctx.send("You don't own a voicechannel!", delete_after=20.0)
        else:
            await channels.delete()
            await ctx.send("Your channel has been deleted", delete_after=20.0)

    @commands.command(pass_context=True)
    async def clearall(self, ctx):
        if ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
            await ctx.message.channel.clone(reason="BotCommand")
            await ctx.message.channel.delete()
        else:
            await ctx.send("You don't have permissions to delete the whole channel")

    @commands.command(pass_context=True)
    async def slowmode(self, ctx):
        args = ctx.message.content.split(" ")
        if len(args) == 2:
            if args[1].isdigit():
                await ctx.message.channel.edit(slowmode_delay=args[1])
                await ctx.send("Slowmode Delay has been set to {}".format(args[1]))

    @commands.command(pass_context=True)
    async def createInvite(self, ctx):
        invitelink = await discord.abc.GuildChannel.create_invite(ctx.message.channel, max_age=300, max_uses=5)
        await ctx.message.channel.purge(limit=1)
        await ctx.send(invitelink)

    @commands.command(pass_context=True)
    async def createtempinvite(self, ctx):
        invitelink = await discord.abc.GuildChannel.create_invite(ctx.message.channel, max_age=300, max_uses=5,
                                                                  reason="Temporary", temporary=True)
        await ctx.message.channel.purge(limit=1)
        await ctx.send(invitelink)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member: discord.Member):

        mutedrole = discord.utils.get(ctx.guild.roles, name="muted")
        if member:
            await member.add_roles(mutedrole)
            await ctx.send(f'{member.mention} has been muted!')
        else:
            await ctx.send("Did you even mention a member?")

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedrole = discord.utils.get(ctx.guild.roles, name="muted")
        if member:
            await member.remove_roles(mutedrole)
            await ctx.send(f'{member.mention} has been unmuted!')

    @commands.command(pass_context=True)
    async def check(self, ctx):
        member: discord.Member
        for counter, member in enumerate(ctx.message.guild.members):
            print(counter, member)
            print(member.joined_at)
            print(member.activity)


async def setup(bot):
    await bot.add_cog(Serveradministration(bot))
