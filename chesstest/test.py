import chess
import chess.svg
import sys

board = chess.Board()


while True:
    move = input("> ")
    board.push_san(move)
    with open("test.svg", "w") as f:
        f.write(chess.svg.board(board=board))
    if board.is_checkmate():
        print("mate")
        exit()
