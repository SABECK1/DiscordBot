import discord
from discord.ext import commands
from urllib.request import urlopen
from urllib import error
import time
import json
import ssl
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


class PriceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = 'f13f3940f6fb57888787ab0d96149830'
        self.coinkey = '4308f572-a714-4ecb-8bb9-62289b63aecb'
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.bal = None
        self.color = None
        self.website = None
        self.name = None
        self.symbol = None
        self.logo = None
        self.max_supply = None
        self.coinprice = None
        self.rank = None
        self.coin_perc = None
        self.mc = None
        self.p = []
        self.com = None

    @commands.command()
    async def price(self, ctx, *args):

        def get_jsonparsed_data(url):
            response = urlopen(url, context=self.ssl_context)
            data = response.read().decode("utf-8")
            return json.loads(data)

        try:
            nresponse = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/search?query={args[0]}'
                                            f'&limit=100&apikey={self.key}')

            for company in nresponse:
                if company["name"].lower().startswith(args[0].lower()):
                    self.com = company
                    break
                else:
                    continue

            fullresponse = get_jsonparsed_data(f'https://financialmodelingprep.com/api/v3/profile/'
                                               f'{self.com["symbol"]}?apikey={self.key}')

            perc = fullresponse[0]["changes"] / fullresponse[0]["price"] * 100

            if perc >= 0:
                self.bal = '⬆'
                self.color = discord.Color.from_rgb(0, 255, 0)
            else:
                self.bal = '⬇'
                self.color = discord.Color.from_rgb(255, 0, 0)

            embed = discord.Embed(title=f'{fullresponse[0]["companyName"]}',
                                  url=fullresponse[0]["website"],
                                  description=f'requested by {ctx.author}',
                                  color=self.color)
            embed.set_thumbnail(url=fullresponse[0]["image"])
            embed.add_field(name=f'Price of {fullresponse[0]["symbol"]} on the {fullresponse[0]["exchange"]}:',
                            value=f'{fullresponse[0]["price"]} {fullresponse[0]["currency"]} | '
                                  f'{round(perc, 2)}% {self.bal}'
                                  f' today')
            embed.add_field(name='Info', value=f'{fullresponse[0]["ceo"]} | {fullresponse[0]["sector"]} | '
                                               f'{fullresponse[0]["country"]}',
                            inline=False)
            embed.set_footer(text=f'requested at: {time.ctime(time.time())} CET')

            await ctx.send(embed=embed)
            self.com = None

        except (IndexError, TypeError, error.HTTPError) as e:
            await ctx.send('A problem occured regarding the given company name.')
            print(e)

    @commands.command()
    async def crypto(self, ctx, *args):

        if len(args) == 2:

            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
            parameters = {
                'symbol': args[0].upper()
            }
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.coinkey
            }

            session = Session()
            session.headers.update(headers)

            try:
                response = session.get(url, params=parameters)
                data = json.loads(response.text)
                self.website = data["data"][args[0].upper()]["urls"]["website"]
                self.name = data["data"][args[0].upper()]["name"]
                self.symbol = data["data"][args[0].upper()]["symbol"]
                self.logo = data["data"][args[0].upper()]["logo"]

                url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
                parameters2 = {
                    'symbol': self.symbol,
                    'convert': args[1].upper()
                }
                headers2 = {
                    'Accepts': 'application/json',
                    'X-CMC_PRO_API_KEY': self.coinkey,
                }

                session2 = Session()
                session2.headers.update(headers2)

                response2 = session2.get(url2, params=parameters2)
                data2 = json.loads(response2.text)
                self.max_supply = data2["data"][args[0].upper()]["max_supply"]
                self.rank = data2["data"][args[0].upper()]["cmc_rank"]
                self.coinprice = data2["data"][args[0].upper()]["quote"][args[1].upper()]["price"]
                self.coin_perc = data2["data"][args[0].upper()]["quote"][args[1].upper()]["percent_change_24h"]
                self.mc = data2["data"][args[0].upper()]["quote"][args[1].upper()]["market_cap"]

                if self.coin_perc >= 0:
                    self.bal = '⬆'
                    self.color = discord.Color.from_rgb(0, 255, 0)
                else:
                    self.bal = '⬇'
                    self.color = discord.Color.from_rgb(255, 0, 0)

                embed = discord.Embed(title=f'{self.name}',
                                      url=self.website[0],
                                      description=f'requested by {ctx.author}',
                                      color=self.color)
                embed.set_thumbnail(url=self.logo)
                embed.add_field(name=f'Price of {self.symbol}:',
                                value=f'{self.coinprice} {args[1].upper()} | {round(self.coin_perc, 2)}% {self.bal} today')
                embed.add_field(name='Metadata',
                                value=f'Marketcap: {int(self.mc)} {args[1].upper()}\n'
                                      f'Max Supply: {self.max_supply} {self.symbol}\n'
                                      f'#{self.rank} on Coinmarketcap',
                                inline=False)
                embed.set_footer(text=f'requested at: {time.ctime(time.time())} CET')

                await ctx.send(embed=embed)

            except (ConnectionError, Timeout, TooManyRedirects, KeyError) as e:
                print(e)
                await ctx.send("Coin not listed.")

        else:
            await ctx.send('Error. Required arguments: *coin* *currency*')

    @commands.command()
    async def coin_list(self, ctx):
        coins = {}

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
        parameters = {
            'listing_status': 'active',
            'limit': 400,
            'sort': 'cmc_rank'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '4308f572-a714-4ecb-8bb9-62289b63aecb'
        }

        session = Session()
        session.headers.update(headers)

        try:
            response2 = session.get(url, params=parameters)
            data = json.loads(response2.text)
            for block in data["data"]:
                coins[block["name"]] = block["symbol"]

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            await ctx.send("Coin not listed.")

        for coin in sorted(coins):
            self.p.append(f'{coin} - {coins[coin]}')

        x1 = '\n'.join(self.p[0:50])
        x2 = '\n'.join(self.p[50:100])
        x3 = '\n'.join(self.p[100:150])
        x4 = '\n'.join(self.p[150:200])
        x5 = '\n'.join(self.p[200:250])
        x6 = '\n'.join(self.p[250:300])

        embed = discord.Embed(title='List of the Top 300 Coins',
                              url='https://coinmarketcap.com/',
                              description=f'requested by {ctx.author}',
                              color=discord.Color.from_rgb(0, 0, 255))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/742440515576004769/916818660922908682/'
                                '3p4mU3qo9235Npfz3ufQ3fOUL5H9OVfluTp7xUAAAAABJRU5ErkJggg.png')
        embed.add_field(inline=True, name='#1-50', value=x1)
        embed.add_field(inline=True, name='#51-100', value=x2)
        embed.add_field(inline=True, name='#101-150', value=x3)
        embed.add_field(inline=True, name='#151-200', value=x4)
        embed.add_field(inline=True, name='#201-250', value=x5)
        embed.add_field(inline=True, name='#251-300', value=x6)

        await ctx.send(embed=embed)


# end

def setup(bot):
    bot.add_cog(PriceCommand(bot))
