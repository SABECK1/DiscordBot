import asyncio
import json
import re
import random

import lavalink
from discord import Embed
from discord import utils
from discord.ext import commands
from youtube_search import YoutubeSearch
import datetime

url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(726549842695815230)

        self.bot.music.add_node('localhost', 7000, 'youshallnotpass', 'eu', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.game_ids = []



    @commands.command(aliases=["j"])
    async def join(self, ctx):
        print('Joined a Channel')
        member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(vc.id))
                print("hello")
        else:
            print(f"{member} was not in a Voicechannel at the time")
            await ctx.send("You have to be in a Voicechannel to do that!")
            raise Exception

    @commands.command(aliases=["pl","p"])
    async def play(self, ctx, *, query):

        try:
            await self.join(ctx)
        except:
            print("Something went wrong")
            return

        player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        player.store('channel', ctx.channel.id)

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)
        tracks = results["tracks"]

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

        '''if not results or not results["tracks"]:
            # YoutubeSearch is sometimes more reliable for some reason
            results = YoutubeSearch(str(query), max_results=1).to_json()
            results_dict = json.loads(results)
            url = 'https://www.youtube.com' + results_dict["videos"][0]["url_suffix"]
            # Try once again to get tracks as a failsafe
            results = await player.node.get_tracks(url)
            if not results or not results["tracks"]:
                return await ctx.send('Nothing found or an Error has occured!')
                # Seems like nothing has worked so I guess there is nothing!'''



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

    @commands.command(aliases=["s","sk"])
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        await player.skip()

    @commands.command()
    async def pause(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.set_pause(True)

    @commands.command(aliases=["r"])
    async def resume(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.set_pause(False)

    @commands.command(aliases=["disconnect", "dc"])
    async def stop(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("Player is not connected!")
        # Check if Author is not in Voice or he doesn't share a Voicechannel with the Bot!
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send("You are not in a Voicechannel with me!")
        # Else just completely shut down the player
        player.queue.clear()

        self.guild_remove(player.guild_id)

        await player.stop()
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send("The player has disconnected!")

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
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

    async def track_hook(self, event):
        def channel_check(event):
            channel = event.player.fetch("channel")

            if channel:
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
            print(event.track.title)
            if not event.player.guild_id in self.game_ids:
                channel = channel_check(event)
                await channel.send(
                    "**:headphones: Now playing {} :headphones:**\r▶️ {}".format(event.track.title,
                                                                                     event.track.uri))
            else:
                await event.player.set_pause(True)
                await asyncio.sleep(10)
                await event.player.set_pause(False)
                print("A new track has started on a guild that already plays!")


        # When playing the game players should be notified what Song it was even when they didn't skip it
        elif isinstance(event, lavalink.events.TrackEndEvent) and event.player.guild_id in self.game_ids:
            channel = channel_check(event)
            await channel.send(f"The song was: {event.track.title}\n{event.track.uri}")

    async def connect_to(self, guild_id: int, channel_id: str):
        websocket = self.bot._connection._get_websocket(guild_id)
        await websocket.voice_state(str(guild_id), channel_id)

    def guild_remove(self, guild_id):
        try:
            self.game_ids.remove(guild_id)
        except:
            print("Guild didnt play the game")


def setup(bot):
    bot.add_cog(MusicCog(bot))
