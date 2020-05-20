import multiprocessing
import chess
import math

pawnWhiteValue = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                  1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0,
                  0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5,
                  0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0,
                  0.5,-0.5,-1.0, 0.0,0.0,-1.0, -0.5, 0.5,
  		  0.5, 1.0, 1.0,-2.5,-2.5,1.0, 1.0,  0.5,
		  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                ]
pawnBlackValue = pawnWhiteValue[::-1]
knightWhiteValue = [
		 -5.0,-4.0,-3.0,-3.0,-3.0,-3.0,-4.0,-5.0,
		 -4.0,-2.0, 0.0, 0.0, 0.0, 0.0,-2.0,-4.0,
		 -3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0,-3.0,
		 -3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5,-3.0,
		 -3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0,-3.0,
		 -3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5,-3.0,
		 -4.0,-2.0, 0.0, 0.5, 0.5, 0.0,-2.0,-4.0,
		 -5.0,-4.0,-2.0,-3.0,-3.0,-2.0,-4.0,-5.0
		]
knightBlackValue = knightWhiteValue[::-1]
bishopWhiteValue = [
                   -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
		   -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
		   -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0,
		   -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0,
		   -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0,
		   -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0,
		   -1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0,
		   -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0
		  ]
bishopBlackValue = bishopWhiteValue[::-1]
rookWhiteValue = [
		  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
		  0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5,
		  -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
		  -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
		  -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
		  -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
		  -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
		  0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0
		]
rookBlackValue = rookWhiteValue[::-1]
queenValue = [
	      -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
	      -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
	      -1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
	      -0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
	      0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
	      -1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
	      -1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
	      -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0
	    ]
kingWhiteValue = [
		  -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
		  -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
		  -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
		  -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
		  -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
		  -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
		  2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
		  2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0
		]
kingBlackValue = kingWhiteValue[::-1]

def alphaBetaRoot(depth, board, isMax):
    possibleMoves = board.legal_moves
    bestMove = -9950
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
            print("\nBest score :", str(bestMove))
            print("Best move: :", str(bestMoveFinal), "\n")
            bestMove = value
            bestMoveFinal = move
    
    print("\n[*] Best move is: ", str(bestMoveFinal))
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

"""
def evaluateBoard(board):
    totalEval = 0
    for i in range(0, 8):
        for j in range(0,8):
            totalEval += evaluatePiece()
"""
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
        evaluation = evaluation + getValue(str(board.piece_at(i)), i)
    return evaluation

def getValue(piece, i):
    global pawnWhiteValue
    global pawnBlackValue
    global kingWhiteValue
    global kingBlackValue
    global queenValue
    global bishopWhiteValue
    global bishopBlackValue
    global rookWhiteValue
    global rookBlackValue
    global knightWhiteValue
    global knightBlackValue

    if piece == None:
        return 0
    value = 0
    if piece == "p":
        value = 10 + pawnBlackValue[i]
    if piece == "P":
        vale = 10 + pawnWhiteValue[i]
    if piece == "n":
        value = 30 + knightBlackValue[i]
    if piece == "N":
        value = 30 + knightWhiteValue[i]
    if piece == "r":
        value = 50 + rookBlackValue[i]
    if piece == "R":
        value = 50 + rookWhiteValue[i]
    if piece == "q" or piece == "Q":
        value = 90 + queenValue[i]
    if piece == "K":
        value = 900 + kingWhiteValue[i]
    if piece == "k":
        value = 900 + kingBlackValue[i]
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
