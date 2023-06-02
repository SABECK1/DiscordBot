import asyncio
import os
import subprocess

import discord
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from YTDL import add_opts

intents = discord.Intents.all()
intents.members = True

load_dotenv()

client = commands.Bot(command_prefix=f"{os.getenv('COMMAND_PREFIX')}", intents=intents, help_command=None)




@client.event
async def on_ready():
    #subprocess.Popen(['java', '-jar', 'Lavalink.jar'])
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

    print('Logged in as {}'.format(client.user.name))
    client.loop.create_task(status_task())
    print("Version:", discord.__version__)
    global Voice
    Voice = []

    print(f"Joined Guilds{client.guilds}")



@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title='All commands', color=0xa722f0,
                          description='All Commands can be used with the prefix "-"')
    embed.add_field(name="```help```", value="Shows this help window", inline=False)

    embed.add_field(name="```helpmusic```", value="Lists all commands related to playing music", inline=False)
    embed.add_field(name="```helpServer```", value="Lists all commands used for moderation purposes", inline=False)
    embed.add_field(name="```helpRandom```", value="Lists all commands used for RNG", inline=False)

    await ctx.channel.send(embed=embed)


##################################SOUNDS############################################

@client.command(pass_context=True)
async def sounds(ctx):
    sound_list = []
    for file in os.listdir("sounds"):
        if file.endswith(".mp3") and file not in sound_list:
            sound_list.append(os.path.splitext(file)[0])

    await ctx.message.channel.purge(limit=1, check=is_not_pinned)
    await ctx.message.channel.send(
        "**All sounds of the bot listed below** :arrow_down:")
    sound_list.sort()

    firstlist = str(sound_list).replace("[", "```")
    secondlist = str(firstlist).replace("]", "```")

    await ctx.message.channel.send(str(secondlist))


@client.command(pass_context=True)
async def addsound(ctx):
    args = ctx.message.content.split(' ')

    url = args[1]

    if len(args) == 3:
        printname = args[
            2]
        newname = "./sounds/" + args[2] + ".mp3"

        with youtube_dl.YoutubeDL(add_opts) as ydl:
            ydl.download([url])
            file = "../sounds/newsound.mp3"

            if len(args) >= 1:
                os.rename(file, newname)

                await ctx.message.channel.send("Your sound has been named {}".format(printname))
                pass


    else:
        await ctx.message.channel.send("You have to provide a Youtubelink together with a name for your sound!")


@client.command(pass_context=True)
async def sound(ctx):
    if ctx.message.author.voice:

        voice = await ctx.message.author.voice.channel.connect()
        server = ctx.message.guild.voice_client
    else:
        embed = discord.Embed(title="```Could not perform this task.```",
                              description="You need to be in a voice channel")
        await ctx.channel.send(embed=embed)
    if not voice.is_playing():

        args = ctx.message.content.split(' ')
        if len(args) == 2:
            sound = args[1]

        else:
            ctx.message.channel.send("You have to name a sound")
        soundpath = "./sounds/"
        sound_there = os.path.isfile(soundpath + sound + ".mp3")

        if sound_there:
            voice.play(discord.FFmpegPCMAudio(soundpath + sound + ".mp3"))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.3
            playing = True
            while True:
                if not voice.is_playing():
                    await server.disconnect()
                    await ctx.message.channel.purge(limit=1)




        else:
            await ctx.message.channel.send("This sound is not available")
            server = ctx.message.guild.voice_client
            await server.disconnect()


def is_not_pinned(mess):
    return not mess.pinned


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    # if before.channel == after.channel:
    #     if after.self_stream:
    #         if member.id == 327478682144997376:
    #             await member.move_to(None)
    #             try:
    #                 if not member.dm_channel:
    #                     await member.create_dm()
    #                 await member.dm_channel.send("Julian hör auf zu streamen")
    #             except discord.errors.Forbidden:
    #                 print("DM couldn't be sent to {}".format(member.name))
    #     #VoiceStateUpdate = Mute/Deaf etc.
    #     return
    if not before.channel:
        print(f"{member.name} joined the channel {after.channel} on the Server {after.channel.guild}")

    if before.channel and not after.channel:
        print(f"{member.name} left the channel {before.channel} on the Server {before.channel.guild}")

    if before.channel != after.channel and after.channel is not None and before.channel is not None:
        print(f"{member.name} swapped channel to {after.channel} on the Server {after.channel.guild}")

    if after.channel and after.channel.name == "Create Voicechannel":
        Check_For_Voicechannel = discord.utils.get(member.guild.voice_channels, name=member.name)
        Check_For_VoiceCategory = discord.utils.get(member.guild.categories, name="Custom Voicechannels")



        # If Voicechannel exists, delete it
        if Check_For_Voicechannel:
            Voicechannel = Check_For_Voicechannel
            await Voicechannel.delete()
            Voice.remove(Voicechannel.id)
        # Whatever happens, create Voicechannel and append it to the list of Voicechannels
        await member.guild.create_voice_channel("{}".format(member.name), category=Check_For_VoiceCategory)
        Check_Voicechannel_Created = discord.utils.get(member.guild.voice_channels, name=member.name)
        if Check_Voicechannel_Created:
            New_Voicechannel = Check_Voicechannel_Created
            await member.move_to(New_Voicechannel)
            Voice.append(New_Voicechannel.id)

    if before.channel:
        if before.channel.name == "Create Voicechannel":
            return
        if len(before.channel.members) != 0:
           pass
        elif before.channel.id not in Voice:
            print("Voicechannel was not a bot created one!")

        else:
            print(Voice, "Deleted Channel")
            await before.channel.delete()
            Voice.remove(before.channel.id)



async def status_task():
    while True:
        await client.change_presence(activity=discord.Game(f"Fortnite"), status=discord.Status.online)
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Game(f'Fortnite'), status=discord.Status.online)
        await asyncio.sleep(10)


@client.command(pass_context=True)
async def leave(ctx):
    if ctx.message.author.voice:
        server = ctx.message.guild.voice_client
        await server.disconnect()
    else:
        embed = discord.Embed(title="```Could not perform this task.```",
                              description="You need to be in the same voice channel as the bot")
        await ctx.channel.send(embed=embed)


#################################messages#######################################


@client.command(pass_context=True)
async def userinfo(ctx, member: discord.Member):
    Userinfoembed = discord.Embed(title=f'Userinfo {member.display_name}', color=0xa722f0)
    Userinfoembed.add_field(name='Joined Server', value=member.joined_at.strftime('%d/%m/%Y'))

    Userinfoembed.add_field(name='Joined Discord', value=member.created_at.strftime('%d/%m/%Y'))
    roles = ''
    for role in member.roles:
        if not role.is_default():
            roles += f'{role.mention} \r\n'
    if roles:
        Userinfoembed.add_field(name='Roles', value=roles)
    Userinfoembed.set_thumbnail(url=member.avatar_url)
    await ctx.message.channel.send(f"Userinfo of {member.mention}")
    await ctx.message.channel.send(embed=Userinfoembed)


################SERVERADMINISTRATION#########################


@client.event
async def on_member_join(member):
    if not member.bot:
        embed = discord.Embed(title="Welcome to the Server, {}!".format(member.name),
                              description='For rules use -rules"')
        try:
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print("DM couldn't be sent to {}".format(member.name))


@client.event
async def on_guild_join(guild):
    print(f"Bot joined {guild}")

    VoiceChannelCategory = discord.utils.get(guild.categories, name="Custom Voicechannels")
    voicechannel = discord.utils.get(guild.voice_channels, name="Create Voicechannel")

    try:
        if voicechannel is None:
            if VoiceChannelCategory is None:
                await guild.create_category("Custom Voicechannels")
                await guild.create_voice_channel("Create Voicechannel", category=VoiceChannelCategory)
            else:
                await guild.create_voice_channel("Create Voicechannel", category=VoiceChannelCategory)
    except Exception:
        print("Something went wrong when creating Voicechannel or Category")

    mutedrole = discord.utils.get(guild.roles, name="muted")
    if mutedrole is None:
        await guild.create_role(name="muted", color=discord.Colour(0x2C2F33),
                                permissions=discord.Permissions(send_messages=False, read_messages=True))
    for channel in guild.channels:
        await channel.set_permissions(mutedrole, send_messages=False, send_tts_messages=False
                                      )




if __name__ == '__main__':

    client.run(f"{os.getenv('DISCORD_TOKEN')}")