import asyncio
import datetime
import random
import re

import lavalink
from discord import Embed
from discord import utils
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(726549842695815230)

        self.bot.music.add_node('localhost', 7000, 'youshallnotpass', 'eu', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.game_ids = []

    async def ensure_voice(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player or not player.is_connected:
            await ctx.send("Player is not connected!")
            return
        # Check if Author is not in Voice or he doesn't share a Voicechannel with the Bot!
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            await ctx.send("You are not in a voicechannel with me!")
            return
        return player

    @commands.command(aliases=["j"])
    async def join(self, ctx):
        print('Joined a Channel')
        member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                player.store('guild', ctx.guild)
                await self.connect_to(ctx.guild.id, str(vc.id))
        else:
            await ctx.send("You have to be in a Voicechannel to do that!")
            raise Exception(f"{member} was not in a Voicechannel at the time")

    @commands.command(aliases=["pl", "p"])
    async def play(self, ctx, *, query):
        await self.join(ctx)
        await asyncio.sleep(.5)
        player = await self.ensure_voice(ctx)

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)
        tracks = results["tracks"]
        print(results)
        if results["loadType"] == "PLAYLIST_LOADED":
            i = 0
            for track in tracks:
                i += 1
                player.add(requester=ctx.author.id, track=track)
            await ctx.send(f"Enqueued Playlist with {i} songs!")
        else:
            track = tracks[0]
            await ctx.send(f"💽 Enqueued {track['info']['title']}")
            player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()

    @commands.command(name="game")
    async def game(self, ctx):

        # Music guessing game with userchosen Musicplaylist from Youtube
        def check(m):
            return m.author == ctx.message.author

        try:
            await self.join(ctx)
        except:
            print("Something went wrong")
            return
        player = self.bot.music.player_manager.get(ctx.guild.id)
        player.store('channel', ctx.channel.id)

        await ctx.send("Give me the URL of a Playlist you want to play the Game with!")
        query = await self.bot.wait_for("message", check=check)
        query = query.content.strip("<>")
        results = await player.node.get_tracks(query)

        # After getting the results for the Track, check if it is viable!
        while not url_rx.match(str(query)) or results["loadType"] != "PLAYLIST_LOADED":
            await ctx.send("That doesn't look like a playlist-url to me you know? Enter one!")
            query = await self.bot.wait_for("message", check=check)
            query = query.content.strip("<>")
            results = await player.node.get_tracks(query)

        # Load Playlist
        if results["loadType"] == "PLAYLIST_LOADED":
            i = 0
            playlist_duration = 0
            tracks = results["tracks"]

            for track in tracks:
                i += 1
                playlist_duration += int(track["info"]["length"])
                player.add(requester=ctx.author.id, track=track)

            # Append the guild id to a list to check if messages
            guild_id = player.guild_id
            self.game_ids.append(guild_id)

            # Shuffle it and give the player some time
            random.shuffle(player.queue)

            await player.play()
            embed = Embed(title="The game has started!", color=0x00aaff)
            embed.add_field(name=f"Playing with playlist: {results['playlistInfo']['name']}",
                            value=f"\u200B \n**Total Songs: {i}\n Total Duration: {datetime.timedelta(milliseconds=playlist_duration)}**\n\u200B\nTo control the game use the usual music-commands")
            embed.set_footer(text="The game will commence shortly...")

            await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player:
            return
        elif not player.is_playing:
            await ctx.send("There is nothing playing!")
        else:
            random.shuffle(player.queue)
            print("player shuffled")

    @commands.command()
    async def loop(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            if player.loop == 1:
                player.set_loop(0)
                await ctx.send("Current Track is no longer set to loop!")
            else:
                player.set_loop(1)  # single track
                await ctx.send("Current Track is set to loop!")

    @commands.command()
    async def loopqueue(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            if player.loop == 2:
                player.set_loop(0)
                await ctx.send("Current Queue is no longer set to loop!")
            else:
                player.set_loop(2)
                await ctx.send("Current Queue is set to loop!")

    @commands.command(aliases=["s", "sk"])
    async def skip(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            # Stop looping single track to make skipping it possible
            if player.loop == 1:
                player.set_loop(0)
            # If only one song is played the player should end without repeating the same song
            if player.loop == 2 and not player.queue:
                player.set_loop(0)
            await ctx.send("Song has been skipped!")
            await player.skip()

    @commands.command()
    async def pause(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            await player.set_pause(True)

    @commands.command(aliases=["r"])
    async def resume(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            await player.set_pause(False)

    @commands.command(aliases=["clearq"])
    async def clearqueue(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            player.queue.clear()
            await ctx.send("Queue cleared!")

    @commands.command(aliases=["disconnect", "dc"])
    async def stop(self, ctx):
        player = await self.ensure_voice(ctx)
        if player:
            player.queue.clear()
            self.guild_remove(player.guild_id)
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)
            await ctx.send("The player has stopped!")

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        player = await self.ensure_voice(ctx)
        embed = Embed()
        if not player.current:
            return await ctx.send("There is nothing playing on this server right now")
        else:
            embed.add_field(name="Currently playing",
                            value=f"[{player.current.title}]({player.current.uri}) {datetime.timedelta(milliseconds=player.current.duration)}")
            if player.queue:
                embed.add_field(name="Enqueued Tracks",
                                value='\n'.join(
                                    [f"[{track.title}]({track.uri}) {datetime.timedelta(milliseconds=track.duration)}"
                                     for track in player.queue[0:10]]),
                                inline=False)
            await ctx.send(embed=embed)

    async def calculate_pos(self, value):
        try:
            h, m, s = value.split(":")
        except ValueError:
            try:
                h = 0
                m, s = value.split(":")
            except ValueError:
                h, m = (0, 0)
                s = value
        milliseconds = int(h) * 3600000 + int(m) * 60000 + int(s) * 1000
        return milliseconds

    @commands.command(name="forward")
    async def jumpforward(self, ctx, value: str):
        player = await self.ensure_voice(ctx)
        if player and player.current.is_seekable:
            milliseconds = await self.calculate_pos(value)
            new_pos = milliseconds + player.current.position
            await player.seek(new_pos)
            await ctx.send(f"Player jumped forward to {lavalink.format_time(new_pos)}!")

    @commands.command(name="backward")
    async def jumpbackward(self, ctx, value: str):
        player = await self.ensure_voice(ctx)
        if player and player.current.is_seekable:
            milliseconds = await self.calculate_pos(value)
            new_pos = player.current.position - milliseconds
            if new_pos < 0:
                new_pos = 0
            await player.seek(new_pos)
            await ctx.send(f"Player jumped backward to {lavalink.format_time(new_pos)}!")

    @commands.command(name="jumpto")
    async def jump_to_pos(self, ctx, value: str):
        player = await self.ensure_voice(ctx)
        if player and player.current.is_seekable:
            milliseconds = await self.calculate_pos(value)
            await player.seek(milliseconds)
            await ctx.send(f"Player jumped to {lavalink.format_time(milliseconds)}!")

    @commands.command(name="volume")
    async def volume_command(self, ctx, value: int):
        if not 0 <= value <= 100:
            await ctx.send("Volume should be between 0 and 100!")
        player = await self.ensure_voice(ctx)
        if player:
            await player.set_volume(value)
            await ctx.send(f"Volume has been set to {value}!")

    async def track_hook(self, event):
        def channel_check(event):
            # gets channel id
            channel = event.player.fetch("channel")
            if channel:
                # returns channel object
                channel = self.bot.get_channel(channel)
                return channel

        if isinstance(event, lavalink.events.QueueEndEvent):
            channel = channel_check(event)
            await channel.send("The Queue has ended, player has stopped playing")
            guild_id = int(event.player.guild_id)
            # Remove guild id from games
            self.guild_remove(guild_id)
            await self.connect_to(guild_id, None)

        elif isinstance(event, lavalink.events.TrackStartEvent):
            if not event.player.guild_id in self.game_ids:
                channel = channel_check(event)
                await channel.send(
                    "**:headphones: Now playing {} :headphones:**\r▶️ {}".format(event.track.title,
                                                                                 event.track.uri))
            else:
                await event.player.set_pause(True)
                await asyncio.sleep(10)
                await event.player.set_pause(False)



        # When playing the game players should be notified what Song it was even when they didn't skip it
        elif isinstance(event, lavalink.events.TrackEndEvent):
            if event.player.guild_id in self.game_ids:
                channel = channel_check(event)
                await channel.send(f"The song was: {event.track.title}\n{event.track.uri}")
            else:
                # Gets guild and all its voicechannels to find the voicechannelobject with the event.player.channel_id
                guild = event.player.fetch('guild')
                voice_channel = utils.get(guild.voice_channels, id = event.player.channel_id)
                # If only the bot is in the call, stop the playback
                if len(voice_channel.members) == 1:
                    await event.player.stop()






    async def connect_to(self, guild_id: int, channel_id: str):
        websocket = self.bot._connection._get_websocket(guild_id)
        await websocket.voice_state(str(guild_id), channel_id)

    def guild_remove(self, guild_id):
        if guild_id in self.game_ids:
            self.game_ids.remove(guild_id)


def setup(bot):
    bot.add_cog(MusicCog(bot))
