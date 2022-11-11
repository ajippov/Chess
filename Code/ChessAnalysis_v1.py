# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 15:28:51 2022

@author: ajipp
"""

## Importing Packages

import chess
import chess.pgn
import chess.engine
from stockfish import Stockfish
import time
import pandas as pd

## Stockfish Setup

params = {"Hash": 20480, "Threads": 10} ## you can specify how many resources you want to throw at stockfish
## however, I have not included in the stockfish initialization, since it slows down my computer more than
## the added power helps the computation. If you were to add it, which hopefully I will eventually, you add 
## after "depth = depth", with the code "parameters = params".


depth = 15 ## Ideally this number is 30, I put it at 15 for testing purposes. This tells you how many plies 
## (half moves) the computer is calculating in advance.

## Stockfish can take parameters
stockfish = Stockfish(path = "D:\Research\Chess Research\Engines\stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe", depth = depth)
## This is an .exe that can be downloaded from the following site:
## https://stockfishchess.org/download/
## Clearly, a different version will be needed for Linux OS. If so, it needs to be "make build"-ed after downloaded and saved.


## Two Key Functions:
## The first, "countGames", counts the number of games in a particular .txt file.
## This integer is then plugged into "getData" as "count". This is because the
## chess package does not have any way of indexing games within a pgn file, so
## to get to the next game, you must call again on the package, and you cannot 
## skip between/over games.
## The code currently hard cores Magnus Carlsen's games, which again was done 
## for testing, but I will either 1. loop through all .txts, or, more likely,
## 2. run the code 38 times, one for each player, which allows me to "parallelize"
## it artificially.
## In the "Games" folder, you will find two versions of the same file: a .txt and
## a .pgn version. PGN = Portable Game Notation, and it's also used as a method of 
## saving games in ChessBase, the source of my data and the largest database of 
## chess games.

def countGames():
    file = open("D:\Research\Chess Research\Games\Magnus Carlsen.txt", "r")
    data = file.read()
    occurrences = data.count("[Event ")
    return occurrences

def getData(count):
    for i in range(count):
        test = open("D:\Research\Chess Research\Games\Magnus Carlsen.txt")
        game = chess.pgn.read_game(test)
        board = game.board()
        typeList = []
        evaluationList = []
        topThree = []
        
        for move in game.mainline_moves():
            pos = board.fen()
            stockfish.set_fen_position(pos)
            print(stockfish.get_evaluation())
            typeList.append(stockfish.get_evaluation().get('type'))
            evaluationList.append(stockfish.get_evaluation().get('value'))
            topThree.append(stockfish.get_top_moves(3))
            board.push(move)
             
        numMoves = len(evaluationList)    
        event = [game.headers["Event"]] * numMoves
        site = [game.headers["Site"]] * numMoves
        date = [game.headers['Date']] * numMoves
        gameRound = [game.headers["Round"]] * numMoves
        white = [game.headers["White"]] * numMoves
        black = [game.headers["Black"]] * numMoves
        result = [game.headers["Result"]] * numMoves
            
        tuples = list(zip(event, site, date, gameRound, white, black, typeList, evaluationList, topThree, result))
        gameData = pd.DataFrame(tuples, columns = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Type', 'Value', 'Top Three', 'Result'])
        
        gameData.to_csv("D:/Research/Chess Research/Data/Game Data/Magnus Carlsen" + str(i) + ".csv") ## saves every game played in a separate file
        
    return gameData
    

def main():
    c=countGames()
    getData(c)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(end-start)

