import chess
import chess.svg
import chess.pgn
import random
from cairosvg import svg2png
import pygame
import time
import math
import pickle
import threading
import cProfile
import berserk
#FvtFPdqVZXQB0KIt

global dep
dep = 3

pygame.init()
screen = pygame.display.set_mode([390, 390])
display_width = 390
display_height = 390

pygame.mixer.music.load('soundtrack.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.02)
print(f'Volume: {pygame.mixer.music.get_volume()*100}%')

#screen = pygame.display.set_mode((display_width,display_height))
board = chess.Board()

highpng = pygame.image.load('pngs/high.png')

def rand_move():
    move  = random.choice(list(board.legal_moves))
    board.push(move)

def display(board):
    svg2png(bytestring=chess.svg.board(chess.BaseBoard(board.board_fen())),write_to=f'temp.png')
    png = pygame.image.load('temp.png')
    screen.blit(png,[0,0])
    pygame.display.update()

def calcPixel(pos=None):
    #15 pixel ofset from end of board
    #each square is 45 pixels wide and long
    # 0,0 starts at top left square A8
    #square
    mousepos = pygame.mouse.get_pos()
    x = math.ceil((mousepos[0]-15)/45)
    y = math.ceil((mousepos[1]-15)/45)
    alph = [0,'a','b','c','d','e','f','g','h']
    xsquare = alph[x]
    ysquare = 9-y
    screen.fill((0,0,0))
    display(board)
    if pos:
        screen.blit(highpng,pos)
    p = [((x-1)*45)+15,((y-1)*45)+15]
    screen.blit(highpng,p)
    pygame.display.update()
    return f'{xsquare}{ysquare}',p

def all_boards(_board,s=False):
    boards = []
    for move in _board.legal_moves:
        boards.append([_board.copy(),move])
        boards[-1][0].push(move)
    if s == True:
        return sort_boards(boards)
    else:
        return boards

def pvalue(p):
    if p == 'P':
        return 100
    if p == 'N':
        return 320
    if p == 'B':
        return 330
    if p == 'R':
        return 500
    if p == 'Q':
        return 900
    if p == 'K':
        return 0

def srt(d):
    try:
        return d[2]
    except:
        return 0

def sort_boards(boards):
    for i in boards:
        z = iscapture(i[0])
        if z:
            guess = 10*z
        else:
            guess = 0
        if i[1].promotion:
            guess += 900
        i.append(guess)
    boards.sort(key=srt,reverse=True)
    return boards

def iscapture(b):
    m = b.pop()
    p = chess.BaseBoard(b.board_fen()).piece_map()
    b.push(m)
    try:
        return pvalue(p[m.to_square].symbol().upper()) - pvalue(p[m.from_square].symbol().upper())
    except:
        return

global table
table = {
'P':[
 0,  0,  0,  0,  0,  0,  0,  0,
 5,-20, 10,-20,-20, 10,-20,  5,
-5, 15,-10,  0,  0,-10, 15, -5,
10,  5,  5, 20, 20,  5,  5, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
10, 10, 20, 30, 30, 20, 10, 10,
50, 50, 50, 50, 50, 50, 50, 50,
 0,  0,  0,  0,  0,  0,  0,  0],
'N':[
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 20, 15, 15, 20,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50],
'B':[
-20,-10,-10,-10,-10,-10,-10,-20,
-10, 15,  0,  0,  0,  0, 15,-10,
 30, 10, 10, 10, 10, 10, 10, 30,
-10,  0, 10, 10, 10, 10,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10,-10,-10,-10,-10,-20],
'R':[
 20,-10,  0,  5,  5,  0,-10, 20,
 -5,  0,  0,  0,  0,  0,  0, -5,
 15,  0,  0,  0,  0,  0,  0, 15,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  5, 10, 10, 10, 10, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0],
'Q':[
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  5,  5,  5,  5,  5,  0,-10,
  0,  0,  5,  5,  5,  5,  0, -5,
 -5,  0,  5,  5,  5,  5,  0, -5,
-10,  0,  5,  5,  5,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20],
'K':[
 20, 30,-10,-30,  0, -10, 30, 20,
 20, 20,  0,  0,  0,  0, 20, 20,
-10,-20,-20,-20,-20,-20,-20,-10,
-20,-30,-30,-40,-40,-30,-30,-20,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30]}

def value(_board):
    global table
    pss = chess.BaseBoard(_board.board_fen()).piece_map()
    score=[0,0]
    if _board.ply() >= 5:
        if _board.turn:
            score[0]+=len(list(_board.legal_moves))*10
        try:
            m = _board.pop()
            score[1] = len(list(_board.legal_moves))*10
            _board.push(m)
        except:
            return 0
        else:
            score[1]+=len(list(_board.legal_moves))*10
        try:
            m = _board.pop()
            score[0] = len(list(_board.legal_moves))*10
            _board.push(m)
        except:
            return 0
    wbnum = 0
    bbnum = 0
    for i in pss:
        #white == true
        p = pss[i]
        ps = p.symbol().upper()
        if p.color == chess.WHITE:
            n = 0
        if p.color == chess.BLACK:
            n = 1
        if n == 0:
            score[n]+=pvalue(ps)+table[ps][i]
        else:
            score[n]+=pvalue(ps)+table[ps][chess.square_mirror(i)]
        if ps == 'B' and n == 0:
            wbnum += 1
        if ps == 'B' and n == 1:
            bbnum += 1
    if wbnum == 2:
        score[0]+=200
    if bbnum == 2:
        score[1]+=200

    if _board.is_checkmate():
        if _board.turn:
            score[1] = math.inf
        else:
            score[0] = math.inf
    if _board.can_claim_threefold_repetition():
        score[0] = 0
        score[1] = 0
    if _board.result() == '1/2-1/2':
        score[0] = 0
        score[1] = 0

    return score[0]-score[1] #add pawn structure, king protection value, check how many positions evaluated, control of opponent squares
global poss
poss = 0

def quiesce(_board,alpha,beta,depth):
    global poss
    val = value(_board)
    if depth >= -3:
        if val >= beta:
            return beta
        if alpha < val:
            alpha = val
        for i in all_boards(_board):
            c = i[0].is_check()
            i[0].pop()
            if i[0].is_capture(i[1]) or c:
                i[0].push(i[1])
                eval = -quiesce(i[0],-beta,-alpha,depth-1)
                if eval >= beta:
                    poss += 1
                    return beta
                if eval > alpha:
                    alpha = eval
    return alpha

def minmax(_board,depth,alpha,beta):
    global poss
    global dep
    best = -math.inf
    if depth == 0 or _board.outcome():
        return quiesce(_board,alpha,beta,0)
    for i in all_boards(_board):
        eval = -minmax(i[0],depth-1,-beta,-alpha)
        if eval >= beta:
            poss += 1
            return eval
        if eval > best:
            best = eval
            if depth == dep:
                finalmove = i[1]
        alpha = max(alpha,eval)
    if depth == dep:
        print(poss)
        return finalmove
    else:
        return best

def s(d):
    return d[0]

pgn = open("short.pgn")
games=[]
while True:
    game = chess.pgn.read_game(pgn)
    ms = [] #move,fen,board object
    if game:
        bo = game.board()
        for i in game.mainline_moves():
            t = {}
            t['move'] = i
            bo.push(i)
            t['board'] = bo.copy()
            t['fen'] = bo.board_fen()
            ms.append(t)
        games.append(ms)
    else:
        print('Database Ready')
        break

def promove(board):
    responses = []
    for g in games:
        for i in range(len(g)):
            if g[i]['fen'] == board.board_fen() and g[i]['board'].turn == board.turn:
                try:
                    responses.append(g[i+1]['move'])
                except:
                    pass
    return responses

def play_live():
    class Game(threading.Thread):
        def __init__(self, client, game_id, **kwargs):
            super().__init__(**kwargs)
            self.game_id = game_id
            self.client = client
            self.stream = client.bots.stream_game_state(game_id)
            self.current_state = next(self.stream)
            self.lastmove = chess.Move.null() #store movestack after best mvioe for acces later, add speed effceincy by not recalcuting, ADD Delta pruning/ stop quescice if the capture is doggywater
            self.scores = []
            self.run()

        def run(self):
            for event in self.stream:
                if event['type'] == 'gameState':
                    self.handle_state_change(event)
                if event['type'] == 'gameFinish':
                    matches-=1 #get white side games working
                    self.exit()
                elif event['type'] == 'chatLine':
                    self.handle_chat_line(event)

        def handle_state_change(self, game_state):
            #client.bots.post_message(self.game_id, f"Board Score: {value(ble)/100}")
            #print(game_state['moves'])
            trying = True
            l = 4
            while trying:
                try:
                    omove = chess.Move.from_uci(game_state['moves'][-l:])
                    trying = False
                except:
                    l+=1
            if omove != self.lastmove:
                ble.push(omove)
                print(f'Board Value: {value(ble)}')
                self.scores.append(value(ble))
                movs = promove(ble)
                if len(movs) != 0:
                    finalmove = random.choice(movs)
                else:
                    s = time.perf_counter()
                    finalmove = minmax(ble,dep,-math.inf,math.inf)
                    print(f"Move Time: {round(time.perf_counter()-s,2)} Sec")
                try:
                    ble.push(finalmove)
                    self.lastmove = finalmove
                    client.bots.make_move(self.game_id, finalmove)
                    print(f'Board Value: {value(ble)}')
                    self.scores.append(value(ble))
                except Exception as e:
                    print(e)
                    #client.bots.post_message(self.game_id, f"{e}")
                    #client.bots.resign_game(self.game_id) #resign errors

        def handle_chat_line(self, chat_line):
            if chat_line['username'] != client.account.get()['username']:
                client.bots.post_message(self.game_id, "Pls wait I don't have chat replys yet")

    matches = 0
    ble = chess.Board()
    session = berserk.TokenSession("FvtFPdqVZXQB0KIt")
    client = berserk.Client(session=session)
    print(client.account.get())
    for event in client.bots.stream_incoming_events():
        print(event)
        if event['type'] == 'challenge':
            if matches <=4:
                if event['challenge']['challenger']['name'] != client.account.get()['username']:
                    client.bots.accept_challenge(event[event['type']]['id'])
                    matches +=1
            else:
                client.bots.decline_challenge(event[event['type']]['id'])
        elif event['type'] == 'gameStart':
            game = Game(client,event['game']['id'])
            game.start()

def play():
    global finalmove
    global finscore
    global poss
    global strt
    global start
    move = 1
    run = 1
    display(board)
    running = True
    while running:
        for event in pygame.event.get():
            ev = pygame.event.event_name(event.type)
            if event.type == 1025:
                try:
                    if run == 1:
                        c = calcPixel()
                        sel1 = chess.parse_square(c[0])
                        for i in board.legal_moves:
                            if c[0] in i.uci()[0:2]:
                                run = 2
                    else:
                        c = calcPixel(c[1])
                        sel2 = chess.parse_square(c[0])
                        m = board.find_move(sel1,sel2)
                        board.push(m)
                        move = 2
                        run = 1
                        display(board)
                        continue
                except Exception as e:
                    print('Invalid Move')
                    print(e)
                    screen.fill((0,0,0))
                    display(board)
                    run = 1
                    pass
            if event.type == pygame.QUIT:
                running = False

        if board.outcome():
            print(f'Game Over! {board.outcome()}')
            time.sleep(5)
            running = False

        if move == 2 and not board.outcome():
            start = time.perf_counter()
            movs = promove(board)
            if len(movs) != 0:
                finalmove = random.choice(movs)
                print(finalmove)
            else:
                print('started MiniMax')
                poss = 0
                finalmove = minmax(board,dep,-math.inf,math.inf)
                print(finalmove)
            end = time.perf_counter()
            print(f'Time: {end-start} Final Move: {finalmove}')
            try:
                board.push(finalmove)
                strt = time.perf_counter()
            except Exception as e:
                print('FF15 Go Next!')
                print(e)
            move = 1

        screen.fill((0,0,0))
        display(board)
        time.sleep(.01)
play()
