import random

import praw
from discord.ext import commands
from settings import *

class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if REDDIT_APP_ID and REDDIT_APP_SECRET:
            self.reddit = praw.Reddit(client_id=REDDIT_APP_ID, client_secret=REDDIT_APP_SECRET,
                                      user_agent=user_agent % REDDIT_APP_ID)

        @commands.command()
        async def reddit(self, ctx, subreddit: str = ""):
            async with ctx.channel.typing():
                if self.reddit:
                    chosen_subreddit = REDDIT_SUBS[0]
                    if subreddit:
                        if ctx.channel.is_nsfw() and subreddit in REDDIT_NSFW_SUBS:
                            chosen_subreddit = subreddit
                        elif ctx.channel.is_nsfw() == False and subreddit in REDDIT_NSFW_SUBS:
                            await ctx.send("The channel is not set for NSFW, CHILDREN ARE WATCHING", delete_after=20)
                            return

                    if subreddit:
                        if subreddit in REDDIT_SUBS:
                            chosen_subreddit = subreddit
                    posts = self.reddit.subreddit(chosen_subreddit).hot()
                    picked_post = random.randint(1, 100)
                    for item in range(0, picked_post):
                        post = next(x for x in posts if not x.stickied)
                    await ctx.send(post.url)
                else:
                    await ctx.send("An Error has occured")


def setup(bot):
    bot.add_cog(Reddit(bot))