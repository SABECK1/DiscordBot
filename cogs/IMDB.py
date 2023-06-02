import csv
import logging
import multiprocessing
import random
import threading

import discord
import imdb
from discord.ext import commands

THREAD_COUNT = multiprocessing.cpu_count()

IMDb_Genres = ["Action", "Adult", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary",
               "Drama", "Family", "Fantasy", "Film-Noir", "Game-Show", "History", "Horror", "Musical", "Mystery",
               "News", "Reality-TV", "Romance", "Sci-Fi", "Short", "Sport", "Talk-Show", "Thriller", "War", "Western"]

class IMDBDATABASEPULL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ia = imdb.IMDb(reraiseExceptions=True)

    def check(self, embed, movie, *threads):

        directorList = []
        actorList = []
        genreList = []

        id = movie.movieID

        info = self.ia.get_movie(id)

        movie_url = self.ia.get_imdbURL(movie)

        if info["kind"] == "episode":
            print(info)

############ACTORS##############

        actors = info.get('cast', '')
        for actor in actors[:3]:
            if actor.currentRole:
                actorList.append(f"{actor['name']} as {actor.currentRole}\n")
            else:
                actorList.append(f"{actor['name']}\n")

############MOVIE INFORMATION###############

        if info["kind"] == "movie":
            directors = info['directors']
            for director in directors:
                directorList.append(f"{director['name']} \n")
            for genre in info.get('genres', ''):
                genreList.append(str(genre) + " |")
            embed.add_field(name=f"__Movie: {' '.join(genreList)}__",
                            value=f"[{movie.get('title', '')} ({movie.get('year', '')})]({movie_url}) | {info.get('rating', '')}☆ \n **Directed by:** \n {' '.join(directorList)} \n **Starring:** \n {' '.join(actorList)} ",
                            inline=False)

#########TV SERIES INFORMATION###########

        elif info["kind"] == "tv series":
            writers = info["writer"]
            for writer in writers:
                if writer["name"] not in directorList:
                    directorList.append(f"{writer.get('name', '')}")
                    directorList.append(
                        "\n")  # Extremely lazy way to ensure that the if statement above works \n destroys it otherwise

                else:
                    continue
            for genre in info["genres"]:
                genreList.append(str(genre) + " |")
            embed.add_field(name=f"__TV Series: {' '.join(genreList)}__",
                            value=f"[{movie.get('title', '')} ({movie.get('year', '')})]({movie_url}) | {info.get('rating', '')}☆ \n **Directed by:** \n {' '.join(directorList)} \n **Starring:** \n {' '.join(actorList)} ",
                            inline=False)

##########JOINING THREADS TO AVOID REPETITION WHEN SEARCHING FOR ONE RANDOM MOVIE##############

        if threads:
            for thread in threads:
                thread.join()

    @commands.command()
    # Searches Multiple Movies via Movie Name
    async def moviesearch(self, ctx, *msg):
        embed = discord.Embed(title="Movie Search Results")
        embed.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/IMDb_Logo_Square.svg/1200px-IMDb_Logo_Square.svg.png")

        if len(msg) < 1:
            await ctx.send("You have to name a TV Series or Movie you want to search for!")
            return

        movies = self.ia.search_movie(str(msg[0:]))

        threads = []
        for movie in movies[0:3]:
            t = threading.Thread(target=self.check, args=(embed, movie))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        await ctx.send(embed=embed)

    @commands.command()
    # Searches via movie name
    async def movie(self, ctx, *args):
        async with ctx.typing():
            if len(args) < 1:
                await ctx.send("You have to name a TV Series or Movie you want to search for!")
                return
            movies = self.ia.search_movie(str(args[0:]))
            movie = movies[0]
            movie_poster = movie.get_fullsizeURL()

            embed = discord.Embed(title="Movie Search Results")
            embed.set_image(
                url=f"{movie_poster}")

            self.check(embed, movie)

            await ctx.send(embed=embed)

    @commands.command()
    # Returns a random movie
    async def randommovie(self, ctx, *msg):
        embed = discord.Embed(title="Movie Search Results")

        async def userchoice(ctx, *msg):
            def check(m):
                return m.author == ctx.message.author

            choice_list = []
            if len(msg) < 1:
                await ctx.send("What kind of Genre do you want the Movie to have?")
                ans = await self.bot.wait_for("message", check=check)
                choices = ans.content.split()

                choice_list = [choice for choice in choices if choice in IMDb_Genres]

            else:
                choice_list = [msg[0]]
                print(choice_list)
            return choice_list

        choice_list = await userchoice(ctx, *msg)

        while not choice_list:
            await ctx.send("That is definitely not a Genre")
            await userchoice(ctx, *msg)

        ####################################

        async with ctx.typing():
            logger = logging.getLogger("imdbpy")
            logger.disabled = True

            threads = []
            while not self.found(embed, choice_list, threads):
                t = threading.Thread(target=self.found, args=(embed, choice_list, threads))
                t.start()
                threads.append(t)

            await ctx.send(embed=embed)

    def found(self, embed, choice_list, threads):
        with open('cogs/links.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            chosen_row = random.choice(list(csv_reader))

        movie = self.ia.get_movie(chosen_row['imdbId'])
        movie_genres = movie.get('genres', '')

        if set(choice_list).issubset(movie_genres):
            if movie.get('rating', 0) > 5:
                self.check(embed, movie, threads)

                return movie


async def setup(bot):
    await bot.add_cog(IMDBDATABASEPULL(bot))
