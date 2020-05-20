"""TODO:
ADD EVALUATION TO PIECES BASED ON THEIR POSITION

"""

import chess
import math

def alphaBetaRoot(depth, board, isMax):
    possibleMoves = board.legal_moves
    bestMove = -9999
    bestMoveFinal = None
    
    for i in possibleMoves:
        move = chess.Move.from_uci(str(i))
        board.push(move)
        
        """calling minimax instead of max """
        value = minimax(depth - 1, board, -10000, 10000, not isMax)
        #value = max(bestMove, minimax(depth - 1, board, -10000, 10000, not isMax))
        #print(value)
        board.pop()
       
        if value > bestMove:
            print("Best score :", str(bestMove))
            print("Best move: :", str(bestMoveFinal))
            bestMove = value
            bestMoveFinal = move
    
    return bestMoveFinal
    

def minimax(depth, board, alpha, beta, isMax):
    if depth == 0:
        return -evaluate(board)

    possibleMoves = board.legal_moves
    
    if isMax:
        bestMove = -9999
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            bestMove = max(bestMove, minimax(depth - 1, board, alpha, beta, not isMax))
            board.pop()
            alpha = max(alpha, bestMove)
            if beta <= alpha:
                return bestMove
        return bestMove
    else:
        bestMove = 9999
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            bestMove = min(bestMove, minimax(depth - 1, board, alpha, beta, not isMax))
            board.pop()
            """if any problem switch to max"""
            beta = min(beta, bestMove)
            if beta <= alpha:
                return bestMove
        return bestMove


def evaluate(board):
    i = 0
    evaluation = 0
    j = True

    try:
        j = bool(board.piece_at(i).color)
    except AttributeError:
        j = j
    while i < 63:
        i += 1
        evaluation = evaluation + (getValue(str(board.piece_at(i)))) if j else -getValue(str(board.piece_at(i)))
    return evaluation


def getValue(piece):
    if piece == None:
        return 0
    value = 0
    if piece == "p" or piece == "P":
        value = 10
    if piece == "n" or piece == "N" or piece == "b" or piece == "B":
        value = 30
    if piece == "r" or piece == "R":
        value = 50
    if piece == "q" or piece == "Q":
        value = 90
    if piece == "K" or piece == "k":
        value = 900
    return value



def main():
    board = chess.Board()
    o = 0
    try:
        while o < 1000:
            if o % 2 == 0:
                move = input("> ")
                board.push_san(move)
            else:
                move = alphaBetaRoot(4, board, True)
                print(move)
                move = chess.Move.from_uci(str(move))
                board.push(move)
            print(board)
            o += 1
    except KeyboardInterrupt:
        print("")
        exit()

if __name__ == "__main__":
    main()
