import pandas as pd
pd.options.mode.chained_assignment = None
import time
import random
from os import system
import os
import pygame
import pickle
from copy import deepcopy

pygame.init()
screen = pygame.display.set_mode([1024, 1024])
display_width = 1024
display_height = 1024

gameDisplay = pygame.display.set_mode((display_width,display_height))
boardpng = pygame.image.load('pngs\Board.png')

def display(board):
    pngs = {}
    for i in board:
        for j in board[i]:
            if j != 0:
                pngs[f'{j.id}'] = pygame.image.load(f'pngs\{j.id[0:2].upper()}.png')
    Boardpng = pygame.image.load('pngs\Board.png')
    #1024 width, 128 per square, 19 pixel deficit to get peices into middle of square
    row = [0 for i in range(8)]
    pnum = 0
    board_ = pd.DataFrame({'a':row,'b':row,'c':row,'d':row,'e':row,'f':row,'g':row,'h':row})
    board_.index +=1
    gameDisplay.blit(Boardpng, (0,0))
    for x in board:
        for y in range(1,9):
            if board[x][y] != 0:
                p = board[x][y]
                board_[x][y] = p.id
                p.calcPixel()
                if p.taken == False:
                    gameDisplay.blit(pngs[p.id], (p.pixelpos[0],p.pixelpos[1]))
                pnum += 1
    pygame.display.update()
    gameDisplay.fill((0,0,0))
    #time.sleep(.3)

class piece:
    def __init__(self,side,id,position):
        self.side = side
        self.id = id
        self.position = position
        self.first = True
        self.attacking = []
        self.pixelpos = [100,100]
        self.taken = False

    def move(self,board,position):
        self.calcPixel()
        #gameDisplay.blit(self.highlight, (self.pixelpos[0]-19,self.pixelpos[1]-19))
        board[self.position[0]][int(self.position[1])] = 0
        self.position = position
        if board[self.position[0]][int(self.position[1])] != 0:
            board[self.position[0]][int(self.position[1])].taken = True
        board[self.position[0]][int(self.position[1])] = self
        self.calcPixel()
        #gameDisplay.blit(self.highlight, (self.pixelpos[0]-19,self.pixelpos[1]-19))
        self.first = False
        return self,board
    def promote(self,pieces):
        self.id = f'{self.side}Q_{self.id[3]}'
        pieces[f'{self.id}'] = self
        return pieces
    def calcXmove(self,x,movement):
        xs = [0,'a','b','c','d','e','f','g','h',0]
        for i in range(1,9):
            if xs[i] == x:
                pos = i
                break
        distance = 7
        while True:
            try:
                if xs[i+distance]!=0:
                    break
                distance-=1
            except:
                distance-=1
        leftdistance = 7-distance
        if i+movement > 8:
            return xs[9],distance,i+movement
        if i+movement < 1:
            return xs[0],distance,i+movement
        else:
            return xs[i+movement],distance,i+movement

    def checkpiece(self,board,position):
        return board[position[0]][int(position[1])]

    def calcPixel(self):
        dist = self.calcXmove(self.position[0],0)
        self.distance = dist[1]
        self.pixelpos[0] = (dist[2]*128)-109
        self.pixelpos[1] = (int(self.position[1])*128)-109
    def calcSquaresBetween(self,board,pos,move):
        vert = False
        horizontal = False
        diagonal = False
        if move[5] == pos[0]:
            vert = True
        elif move[6] == pos[1]:
            horizontal = True
        else:
            diagonal = True
        finalmoves = []
        if vert == True:
            if int(move[6]) > int(pos[1]):
                possible = [f'{pos[0]}{x}' for x in range(int(pos[1])+1,int(move[6])+1)]
            if int(move[6]) < int(pos[1]):
                possible = [f'{pos[0]}{x}' for x in reversed(range(int(move[6]),int(pos[1])))]
            try:
                for i in possible:
                    if int(i[1])<=8 and int(i[1])>=1:
                        p = self.checkpiece(board,i)
                        if p == 0:
                            finalmoves.append(f'{move[0:5]}{i}')
                        else:
                            if self.id[1] != 'P' and p.side != self.side:
                                finalmoves.append(f'{move[0:5]}{i}_take')
                            break
            except:
                pass
        if horizontal == True:
            if self.calcXmove(move[5],0)[2] > self.calcXmove(pos[0],0)[2]: #moving right
                possible = [f'{self.calcXmove(pos[0],x)[0]}{pos[1]}' for x in range(1,self.calcXmove(pos[0],0)[1]+1)]
            if self.calcXmove(move[5],0)[2] < self.calcXmove(pos[0],0)[2]: #moving left
                possible = [f'{self.calcXmove(pos[0],-x)[0]}{pos[1]}' for x in range(1,self.calcXmove(pos[0],0)[1]+1)]
            for i in possible:
                try:
                    p = self.checkpiece(board,i)
                    if p == 0:
                        finalmoves.append(f'{move[0:5]}{i}')
                    else:
                        if p.side != self.side:
                            finalmoves.append(f'{move[0:5]}{i}_take')
                        break
                except:
                    pass
        return finalmoves

    def legalmoves(self,board):
        moves = []
        intpos = int(self.position[1])
        xpos = self.position[0]
        if self.id[1] == 'P' and self.taken == False:
            potential = []
            if self.id[0] == 'W':
                if self.checkpiece(board, f'{xpos}{intpos+1}') == 0:
                    moves.append(f'WP_{self.id[3]}_{xpos}{intpos+1}')
                if self.first==True and self.checkpiece(board, f'{xpos}{intpos+2}') == 0 and self.checkpiece(board, f'{xpos}{intpos+1}') == 0:
                    moves.append(f'WP_{self.id[3]}_{xpos}{intpos+2}')
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(xpos,1)[0]}{intpos+1}')
                    if p != 0:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'WP_{self.id[3]}_{self.calcXmove(xpos,1)[0]}{intpos+1}_check')
                            else:
                                moves.append(f'WP_{self.id[3]}_{self.calcXmove(xpos,1)[0]}{intpos+1}_take')
                except:
                    pass
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(xpos,-1)[0]}{intpos+1}')
                    if p != 0:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'WP_{self.id[3]}_{self.calcXmove(xpos,-1)[0]}{intpos+1}_check')
                            else:
                                moves.append(f'WP_{self.id[3]}_{self.calcXmove(xpos,-1)[0]}{intpos+1}_take')
                except:
                    pass
            else:
                if self.checkpiece(board, f'{xpos}{intpos-1}') == 0:
                    moves.append(f'BP_{self.id[3]}_{xpos}{intpos-1}')
                if self.first==True and self.checkpiece(board, f'{xpos}{intpos-2}') == 0 and self.checkpiece(board, f'{xpos}{intpos-1}') == 0:
                    moves.append(f'BP_{self.id[3]}_{xpos}{intpos-2}')
                try:
                    p = self.checkpiece(f'{self.calcXmove(xpos,1)[0]}{intpos-1}')
                    if p != 0:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'BP_{self.id[3]}_{self.calcXmove(xpos,1)[0]}{intpos-1}_check')
                            else:
                                moves.append(f'BP_{self.id[3]}_{self.calcXmove(xpos,1)[0]}{intpos-1}_take')
                except:
                    pass
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(xpos,-1)[0]}{intpos-1}')
                    if p != 0:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'BP_{self.id[3]}_{self.calcXmove(xpos,-1)[0]}{intpos-1}_check')
                            else:
                                moves.append(f'BP_{self.id[3]}_{self.calcXmove(xpos,-1)[0]}{intpos-1}_take')
                except:
                    pass
            return moves
        if self.id[1] == 'R' and self.taken == False:
            potential = []
            #create 4 potential move sets, up down left right and then check how far u can go in each
            rdistance = self.calcXmove(self.position[0],0)[1]
            ldistance = 7-rdistance
            updistance = 8-int(self.position[1])
            downdistance = 7-updistance
            for i in range(1,updistance+1): #moving up
                try:
                    p = self.checkpiece(board,f'{self.position[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}_check')
                            else:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}_take')
                        break
                except:
                    break
            for i in range(1,downdistance+1): #moving down
                try:
                    p = self.checkpiece(board,f'{self.position[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}_check')
                            else:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}_take')
                        break
                except:
                    break
            for i in range(1,rdistance+1): #moving right
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{self.position[1]}')
                    if p == 0:
                        moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}_check')
                            else:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}_take')
                        break
                except:
                    break
            for i in range(1,ldistance+1): #moving left
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}')
                    if p == 0:
                        moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}_check')
                            else:
                                moves.append(f'{self.side}R_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}_take')
                        break
                except:
                    break
            return moves
        if self.id[1] == 'H' and self.taken == False:
            potential = []
            for i in [[1,2],[2,1],[2,-1],[1,-2],[-1,-2],[-2,-1],[-2,1],[-1,2]]:
                potential.append(f'{self.side}H_{self.id[3]}_{self.calcXmove(self.position[0],i[0])[0]}{int(self.position[1])+i[1]}')
            for i in potential:
                try:
                    if i[5] != 0 and int(i[6:]) <=8 and int(i[6:]) >=1:
                        p = self.checkpiece(board,i[5:7])
                        if p == 0:
                            moves.append(i)
                        elif p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{i}_check')
                            else:
                                moves.append(f'{i}_take')
                except:
                    continue
            return moves
        if self.id[1] == 'B' and self.taken == False:
            distance = self.calcXmove(self.position[0],0)[1]
            for i in range(1,distance+1): #moving right and up
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}_check')
                                break
                            else:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,distance+1): #moving right and down
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}_check')
                                break
                            else:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,(8-distance)): #moving left and up
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}_check')
                                break
                            else:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,(8-distance)): #moving left and down
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}_check')
                                break
                            else:
                                moves.append(f'{self.side}B_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}_take')
                                break
                        break
                except:
                    break
            return moves
        if self.id[1] == 'Q' and self.taken == False:
            distance = self.calcXmove(self.position[0],0)[1]
            rdistance = self.calcXmove(self.position[0],0)[1]
            ldistance = 7-rdistance
            updistance = 8-int(self.position[1])
            downdistance = 7-updistance
            for i in range(1,updistance+1): #moving up
                try:
                    p = self.checkpiece(board,f'{self.position[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])+i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,downdistance+1): #moving down
                try:
                    p = self.checkpiece(board,f'{self.position[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.position[0]}{int(self.position[1])-i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,rdistance+1): #moving right
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{self.position[1]}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{self.position[1]}_take')
                                break
                        break
                except:
                    break
            for i in range(1,ldistance+1): #moving left
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{self.position[1]}_take')
                                break
                        break
                except:
                    break
            for i in range(1,distance+1): #moving right and up
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])+i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,distance+1): #moving right and down
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],i)[0]}{int(self.position[1])-i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,(8-distance)): #moving left and up
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])+i}_take')
                                break
                        break
                except:
                    break
            for i in range(1,(8-distance)): #moving left and down
                try:
                    p = self.checkpiece(board,f'{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}')
                    if p == 0:
                        moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}')
                    else:
                        if p.side != self.side:
                            if 'K' in p.id:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}_check')
                                break
                            else:
                                moves.append(f'{self.side}Q_{self.id[3]}_{self.calcXmove(self.position[0],-i)[0]}{int(self.position[1])-i}_take')
                                break
                        break
                except:
                    break
            return moves
        if self.id[1] == 'K':
            potential = []
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],1)[0]}{int(self.position[1])+0}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],1)[0]}{int(self.position[1])+1}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],1)[0]}{int(self.position[1])-1}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],0)[0]}{int(self.position[1])+1}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],0)[0]}{int(self.position[1])-1}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],-1)[0]}{int(self.position[1])+1}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],-1)[0]}{int(self.position[1])+0}')
            potential.append(f'{self.side}K_0_{self.calcXmove(self.position[0],-1)[0]}{int(self.position[1])-1}')
            for i in potential:
                try:
                    p = self.checkpiece(board,i[5:7])
                    if p == 0:
                        moves.append(i)
                    else:
                        if p.side != self.side:
                            moves.append(f'{i}_take')
                except:
                    continue
            return moves
class _board:
    def __init__(self,check,turn,board,pieces):
        self.check = {'W':False,'B':False}
        self.turn = 'W'
        self.board = board
        self.pieces = pieces
    def checkcheck(self):
        for j in [['W','B'],['B','W']]:
            for i in self.pieces:
                if self.pieces[i].side == j[0] and self.pieces[i].taken == False:
                    for m in self.pieces[i].legalmoves(self.board):
                        if 'check' in m:
                            self.check[j[1]] = True
                            #print('check')
                            #print(self.pieces[i].legalmoves(self.board))
                            #self.display()
                            return
            self.check[j[1]] = False
    def allmoves(self):
        moves = []
        for i in self.pieces:
            if self.pieces[i].taken == False:
                for j in self.pieces[i].legalmoves(self.board):
                    moves.append(j)
        return moves
    def allboards(self):
        moves = []
        for i in self.pieces:
            if i[0] == self.turn and self.pieces[i].taken == False:
                for j in self.pieces[i].legalmoves(self.board):
                    moves.append(j)
        boards = []
        boards.append(deepcopy(self))
        for i in moves:
            boards.append(deepcopy(boards[0]))
            new = boards[-1].pieces[i[0:4]].move(boards[-1].board,i[5:7])
            boards[-1].pieces[i[0:4]] = new[0]
            boards[-1].board = new[1]
            boards[-1].checkpromo()
            boards[-1].checkcheck()
            if boards[-1].check[boards[-1].turn] == True:
                boards.pop(-1)
            elif boards[-1].turn == 'W':
                boards[-1].turn = 'B'
            else:
                boards[-1].turn = 'W'
        if len(boards) == 0:
            if self.check[self.turn] == True:
                print("checkmate")
            else:
                print('stalemate!')
            return []
        return boards
    def checkpromo(self):
        promod = False
        for i in self.pieces:
            if 'P' in self.pieces[i].id:
                if self.pieces[i].position[1] == '1' or self.pieces[i].position[1] == '8':
                    new = self.pieces[i].promote(self.pieces)
                    #print('promoted!')
                    promod = True
                    break
        if promod == True:
            self.pieces = new
    def calcScore(self):
        return
    def display(self):
        row = [0 for i in range(8)]
        pnum = 0
        board_ = pd.DataFrame({'a':row,'b':row,'c':row,'d':row,'e':row,'f':row,'g':row,'h':row})
        board_.index +=1
        for x in self.board:
            for y in range(1,9):
                if self.board[x][y] != 0:
                    p = self.board[x][y]
                    board_[x][y] = p.id[0:2]
                    #p.calcPixel()
                    #gameDisplay.blit(p.png, (p.pixelpos[0],p.pixelpos[1]))
                    pnum += 1
        #print(pnum)
        print(board_)
class _game:
    def __init__(self):
        self.check = False
        self.turn = 'W'
        self.canmove = True
    def initboard(self):
        row = [0 for i in range(8)]
        board = pd.DataFrame({'a':row,'b':row,'c':row,'d':row,'e':row,'f':row,'g':row,'h':row})
        board.index +=1
        pieces={}
        # piece naming: SIDETYPE_ID
        for p in [[2,'W'],[7,'B']]:
            n=0
            for i in board:
                n+=1
                pieces[f'{p[1]}P_{n}'] = piece(side=p[1],id=f'{p[1]}P_{n}',position=f'{i}{p[0]}')
                board[i][p[0]] = pieces[f'{p[1]}P_{n}']
        for p in [[1,'W'],[8,'B']]:
            pieces[f'{p[1]}R_1'] = piece(side=p[1],id=f'{p[1]}R_1',position=f'a{p[0]}')
            pieces[f'{p[1]}H_1'] = piece(side=p[1],id=f'{p[1]}H_1',position=f'b{p[0]}')
            pieces[f'{p[1]}B_1'] = piece(side=p[1],id=f'{p[1]}B_1',position=f'c{p[0]}')
            pieces[f'{p[1]}Q_0'] = piece(side=p[1],id=f'{p[1]}Q_0',position=f'd{p[0]}')
            pieces[f'{p[1]}K_0'] = piece(side=p[1],id=f'{p[1]}K_0',position=f'e{p[0]}')
            pieces[f'{p[1]}B_2'] = piece(side=p[1],id=f'{p[1]}B_2',position=f'f{p[0]}')
            pieces[f'{p[1]}H_2'] = piece(side=p[1],id=f'{p[1]}H_2',position=f'g{p[0]}')
            pieces[f'{p[1]}R_2'] = piece(side=p[1],id=f'{p[1]}R_2',position=f'h{p[0]}')
            board['a'][p[0]] = pieces[f'{p[1]}R_1']
            board['b'][p[0]] = pieces[f'{p[1]}H_1']
            board['c'][p[0]] = pieces[f'{p[1]}B_1']
            board['d'][p[0]] = pieces[f'{p[1]}Q_0']
            board['e'][p[0]] = pieces[f'{p[1]}K_0']
            board['f'][p[0]] = pieces[f'{p[1]}B_2']
            board['g'][p[0]] = pieces[f'{p[1]}H_2']
            board['h'][p[0]] = pieces[f'{p[1]}R_2']
        return _board(self.check,self.turn,board,pieces)
    def play(self):
        start = time.perf_counter()
        boards = self.board.allboards()
        end = time.perf_counter()
        print(f"time: {end-start}")

    def test(self):
        going = True
        moveds = []
        while going:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    going = False
            pots = self.board.allboards()
            for j in self.board.pieces:
                print([self.board.pieces[j].id,self.board.pieces[j].taken])
            if len(pots) != 0:
                self.board = random.choice(pots)
                #self.board.display()
            else:
                print(f'checkmate! {self.board.turn} Loses!')
                #self.board.display()
                input()
                break
            #print(self.board)
            if self.board.check == True:
                print('checked')
            display(self.board.board)
            print(self.board.allmoves())
            print(self.board.check)
            input()
        '''
        finboard = self.initboard()
        start = time.perf_counter()
        for i in moveds:
            #print(i)
            finboard.pieces[i[0:4]].move(finboard.board,i[5:7])
            finboard.checkpromo()
            finboard.checkcheck()
            #finboard.display()
        end = time.perf_counter()
        print(f"time: {end-start}")
        '''
        #input()

#completely redo checks or FIRST FIGURE OUT IF IT RECGNIZES IT IS IN CHECK
game = _game()
game.board = game.initboard()
print(game.board.board)
game.test()
