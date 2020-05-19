import threading
import chess
import chess.svg
from chess.polyglot import open_reader
import time
import cairosvg
import discord
import random
import asyncio
import chessai
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
    async def engine(self, ctx):
        author = ctx.message.author
        opponent = "engine"
        self.white = Player('white', author)
        self.white.turn = True
        self.black = Player('black', "engine")
        self.board = chess.Board()
        self.genBoardImg()
        await ctx.message.channel.send(file=discord.File("board.png"))
    
        """
        o = 0
        while o < 1000:
            if o % 2 == 0:
                await ctx.message.channel.send("Your turn. use the enginemove command")
                move = await 
            else:
                move = chessai.alphaBetaRoot(4, self.board, True)
                move = chess.Move.from_uci(str(move))
                self.board.push(move)
            o += 1
        """
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
        if str(ctx.message.author) == str(player.username):
            try:
                move = ctx.message.content[9:]
                self.board.push_san(move)
                self.genBoardImg()
                await ctx.message.channel.send(file=discord.File("board.png"))
                self.swapTurns()
                if self.black.username == "engine":
                    with open_reader('gamebook/games.bin') as reader:
                        opening_moves = [str(entry.move) for entry in reader.find_all(self.board)]
                    if opening_moves:
                        choice = random.randint(0, len(opening_moves) // 2)
                        move = chess.Move.from_uci(opening_moves[choice])
                        move = chess.Move.from_uci(str(move))
                        self.board.push(move)
                        self.genBoardImg()
                        self.swapTurns()
                        await ctx.message.channel.send(file=discord.File("board.png"))
                    else:
                        print("Thinking...")
                        move = chessai.alphaBetaRoot(3,self.board,True)
                        move = chess.Move.from_uci(str(move))
                        self.board.push(move)
                        self.genBoardImg()
                        self.swapTurns()
                        await ctx.message.channel.send(file=discord.File("board.png"))


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

