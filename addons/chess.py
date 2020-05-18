import chess
import chess.svg
import cairosvg
import discord
import random
import asyncio
from discord.ext import commands


class Player:
    def __init__(self, color, username):
        self.color = color
        self.username = username
        self.turn = False

class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = chess.Board()
        self.white = None
        self.black = None
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def assignColors(self, author, opponent):
        rand = random.randrange(0,2)
        self.white = Player('white', author) if rand == 0 else Player('white', opponent)
        self.black = Player('black', author) if rand == 1 else Player('black', opponent)
        self.white.turn = True

    def genBoardImg(self):
        with open("board.svg", "w") as img:
            img.write(chess.svg.board(board=self.board))
        cairosvg.svg2png(url="board.svg", write_to="board.png")        

    def swapTurns(self):
        self.white.turn = not self.white.turn
        self.black.turn = not self.black.turn

    @commands.command(pass_context=True)
    async def challenge(self, ctx, username):
        author = ctx.message.author
        opponent = ctx.message.mentions[0]
        self.assignColors(author, opponent)
        self.genBoardImg()
        print("{} vs {}".format(author, opponent))
        await ctx.message.channel.send(file=discord.File("board.png"))
        await ctx.message.channel.send("{} moves first.".format(self.white.username))

    @commands.command(pass_context=True)
    async def move(self, ctx, move = ''):
        player = self.white if self.white.turn == True else self.black
        print(player.username)
        print(ctx.message.author)
        if str(ctx.message.author) == str(player.username):
            try:
                move = ctx.message.content[9:]
                print(move)
                self.board.push_san(move)
                self.genBoardImg()
                await ctx.message.channel.send(file=discord.File("board.png"))
                self.swapTurns()

                if self.board.is_game_over() or self.board.is_checkmate():
                    await ctx.message.channel.send("[*] Game Over.")
                    self.white = None
                    self.black = None
                    self.board = chess.Board()

            except ValueError:
                await ctx.message.channel.send("[!] WARNING: Invalid move!")

        else:
            await ctx.message.channel.send("Not {}'s turn!".format(ctx.message.author))



def setup(bot):
    bot.add_cog(Chess(bot))

