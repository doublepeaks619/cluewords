import json
import card_value
import mysql.connector
from storage import Storage

class StorageMySql(Storage):

    def create_game(self, name, player1a, player1b, player2a, player2b, board):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        add_game_query = ("INSERT INTO games (name, player1a, player1b, player2a, player2b, board, ended) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(add_game_query, (name, player1a, player1b, player2a, player2b, board, False))
        game_id = cursor.lastrowid
        cnxn.commit()
        cursor.close()
        cnxn.close()
        return game_id

    def end_game(self, game_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        end_game_query = ("UPDATE games SET ended = True WHERE id = %s" % game_id)
        cursor.execute(end_game_query)
        delete_turns_query = ("DELETE FROM turns WHERE game_id = %s" % game_id)
        cursor.execute(delete_turns_query)
        cnxn.commit()
        cursor.close()
        cnxn.close()

    def get_game(self, game_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        get_game_query = ("SELECT name, player1a, player1b, player2a, player2b, ended FROM games WHERE id = %s" % game_id)
        cursor.execute(get_game_query)
        result = None
        for (name, player1a, player1b, player2a, player2b, ended) in cursor:
            result = {}
            result['name'] = name
            result['player1a'] = player1a
            result['player1b'] = player1b
            result['player2a'] = player2a
            result['player2b'] = player2b
            result['guessers'] = [player1b, player2b]
            result['cluers'] = [player1a, player2a]
            result['ended'] = ended
        cursor.close()
        cnxn.close()
        return result

    def get_last_turn(self, game_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        get_last_turn = ("SELECT CASE WHEN turns.board IS NULL THEN games.board ELSE turns.board END AS board, turns.next_player, turns.next_team, turns.guess, turns.guess_remaining, games.player1b, games.player2b, games.player1a, games.player2a, turns.clue, turns.clue_number, games.ended FROM turns RIGHT OUTER JOIN games ON turns.game_id = games.id  WHERE games.id = %s ORDER BY turns.id desc LIMIT 1" % game_id)
        cursor.execute(get_last_turn)
        result = None
        for (last_turn_board, current_player, current_team, word, word_number, guesser1, guesser2, cluer1, cluer2, clue, clue_number, ended) in cursor:
            result = {}
            result['board'] = json.loads(last_turn_board)
            result['expected_player'] = cluer1 if current_player is None else current_player
            result['expected_team'] = card_value.BLUE if current_team is None else current_team
            result['guessers'] = [guesser1, guesser2]
            result['cluers'] = [cluer1, cluer2]
            result['guess'] = word
            result['guess_remaining'] = word_number
            result['clue'] = clue
            result['clue_number'] = clue_number
            result['ended'] = ended
        cursor.close()
        cnxn.close()
        return result

    def add_new_turn(self, game_id, expected_player, expected_team, next_player, next_team, guess, guess_remaining, clue, clue_number, board):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        add_turn = ("INSERT INTO turns (game_id, current_player, current_team, next_player, next_team, guess, guess_remaining, clue, clue_number, board) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(add_turn, (game_id, expected_player, expected_team, next_player, next_team, guess, guess_remaining, clue, clue_number, board))
        turn_id = cursor.lastrowid
        cnxn.commit()
        cursor.close()
        cnxn.close()
        return turn_id


    def get_player_games(self, player_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        get_game = ("SELECT id FROM games WHERE player1a = '%s' or player1b = '%s' or player2a = '%s' or player2b = '%s'" % (player_id, player_id, player_id, player_id))
        cursor.execute(get_game)
        detail = []
        for games_id in cursor:
            detail.append(games_id[0])
        cursor.close()
        cnxn.close()
        return detail

    def get_player_game_names(self, player_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        get_game = ("SELECT id, name FROM games WHERE player1a = '%s' or player1b = '%s' or player2a = '%s' or player2b = '%s'" % (player_id, player_id, player_id, player_id))
        cursor.execute(get_game)
        detail = []
        for (game_id, game_name) in cursor:
            detail.append({"id":game_id, "name":game_name})
        cursor.close()
        cnxn.close()
        return detail

