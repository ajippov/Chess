# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 15:28:51 2022

@author: ajipp, cingebrigtsen
"""

## Importing Packages

import chess
import chess.pgn
import chess.engine
from stockfish import Stockfish
import time
import pandas as pd
from datetime import datetime
import concurrent.futures
import os

# Quickly count games for this player
def count_games(directory, player):
    file = open(directory + player + ".txt", "r")
    data = file.read()
    occurrences = data.count("[Event ")
    file.close()
    return occurrences


# Use this method as an intro point for a concurrent game
# It will process the game, launch stockfish, and save the results.
def process_game(index, game, player, save_directory, count, threads = 1, hash_size = 1024, depth = 30):
    event_name = "(" + str(index) + "/" + str(count) + ") " + game.headers["Event"] + " (" + game.headers["EventDate"] + ")" + " White: " + game.headers["White"] + " vs " + "Black: " + game.headers["Black"]
    start_game = start_profile("game: " + event_name, wrapping_characters = "##")

    parameters = {
        "Threads": threads,
        "Hash": hash_size
    }

    stockfish = Stockfish(depth = depth, parameters = parameters)

    board = game.board()
    typeList = []
    evaluationList = []
    topThree = []
    current_move = 0
    total_moves = 0
    for move in game.mainline_moves():
        total_moves += 1

    for move in game.mainline_moves():
        current_move+=1
        start_move = start_profile("move ("+ str(current_move) + "/" + str(total_moves) + ")" + event_name)

        pos = board.fen()
        stockfish.set_fen_position(pos)

        evaluation = stockfish.get_evaluation()

        typeList.append(evaluation.get('type'))
        evaluationList.append(evaluation.get('value'))

        topThree.append(stockfish.get_top_moves(3))

        board.push(move)
        end_profile("move ("+ str(current_move) + "/" + str(total_moves) + ")" + event_name, start_move)


    numMoves = len(evaluationList)
    event = [game.headers["Event"]] * numMoves
    site = [game.headers["Site"]] * numMoves
    date = [game.headers['Date']] * numMoves
    gameRound = [game.headers["Round"]] * numMoves
    white = [game.headers["White"]] * numMoves
    black = [game.headers["Black"]] * numMoves
    result = [game.headers["Result"]] * numMoves
    end_now = datetime.now()

    tuples = list(zip(event, site, date, gameRound, white, black, typeList, evaluationList, topThree, result))
    gameData = pd.DataFrame(tuples, columns = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Type', 'Value', 'Top Three', 'Result'])

    file_name = save_directory + player.replace(" ", "") + "_" + str(index) + "_depth_" + str(depth) + ".csv"
    print("Writing File: ", file_name)
    gameData.to_csv(file_name) ## saves every game played in a separate file

    end_profile("game: " + event_name, start_game, wrapping_characters = "##")
    print("Total moves for ", event_name, " is ", total_moves)
    stockfish = None # Cleanup Stockfish before the thread finishes.

# Read all the games in, and setup the flow in which they will execute
# Either through concurrent games or one by one.
def run_games(count, directory, save_directory, player, should_thread = True, concurrent_games = 10, starting_game = 0) :
    game_file = open( directory + player + ".txt")
    games = []
    finished_games =[]
    for i in range(count):
        if starting_game > i:
            continue

        games.append(chess.pgn.read_game(game_file))

    game_file.close()

    all_games_start = start_profile("all games for: " + player, wrapping_characters = "**")

    if should_thread:
        with concurrent.futures.ThreadPoolExecutor(max_workers = concurrent_games) as executor:
            futures = [executor.submit(process_game, index, game, player, save_directory, len(games)) for index, game in enumerate(games)]

            for future in concurrent.futures.as_completed(futures):
                print("Game Cleaned up")
    else:
        for index, game in enumerate(games):
            process_game(index, game, player, save_directory, games.count())

    end_profile("all games for: " + player, all_games_start, wrapping_characters = "**")

    return finished_games

def start_profile(event, wrapping_characters = ""):
    start = datetime.now()
    print(wrapping_characters, "Starting: ", event, " Current Time:", start.strftime("%H:%M:%S"), wrapping_characters)
    return start

def end_profile(event, start, wrapping_characters = ""):
    end = datetime.now()
    print(wrapping_characters, "Ending: ", event, " Current Time: ", end.strftime("%H:%M:%S"), "Elappsed time: ", (end - start).total_seconds(), wrapping_characters)

def main():
    directory = "/home/cingebrigtsen/projects/Chess/Games/"
    save_directory = "/home/cingebrigtsen/projects/Chess/data/"
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    # players = ["Alexander Grischuk.txt", "Alexander Morozevich.txt", "Alexei Shirov.txt",
        # "Alireza Firouzja.txt", "Anatoly Karpov.txt", "Arjun Erigaisi.txt",
        # "Boris Gelfand.txt", "Daniil Dubov.txt", "Ding Liren.txt", "Dommaraju Gukesh.txt",
        # "Etienne Bacrot.txt", "Evgeny Bareev.txt", "Fabiano Caruana.txt", "Garry Kasparov.txt",
        # "Hikaru Nakamura.txt", "Ian Nepomniachtchi.txt", "Jan-Krzysztof Duda.txt",
        # "Levon Aronian.txt", "Magnus Carlsen.txt", "Michael Adams.txt",
        # "Nigel Short.txt", "Nikita Vitiugov.txt", "Nodirbek Abdusattorov.txt",
        # "Peter Leko.txt", "Peter Svidler.txt", "Richard Rapport.txt", "Robert James Fischer.txt",
        # "Shakhriyar Mamedyarov.txt", "Teimour Radjabov.txt", "Vassily Ivanchuk.txt",
        # "Veselin Topalov.txt", "Vincent Keymer.txt", "Viswanathan Anand.txt", "Vladimir Kramnik.txt",
        # "Vladimir Malakhov.txt", "Vladislav Artemiev.txt", "Wei Yi.txt", "Wesley So.txt"]
    players = ["Arjun Erigaisi", "Alexander Grischuk", "Alexander Morozevich"]

    for player in players:
        total_games = count_games(directory, player)
        run_games(total_games, directory, save_directory, player)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(end-start)

