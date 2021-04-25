import chess.pgn
import chess
import time
import random
from sklearn.externals import joblib

pgn = open("games.pgn")
games=[]
while True:
    game = chess.pgn.read_game(pgn)
    ms = [] #move,fen,board object
    if game:
        board = game.board()
        for i in game.mainline_moves():
            t = {}
            t['move'] = i
            board.push(i)
            t['board'] = board.copy()
            t['fen'] = board.board_fen()
            ms.append(t)
        games.append(ms)
    else:
        break
print('done')
joblib.dump(games,'data.pickle')
