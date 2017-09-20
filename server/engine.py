import json
import random
import card_value
from exceptiondef import GameException

class GameEngine(object):

    def __init__(self, GameStorage):
        self._storage = GameStorage
        with open("wordlist.txt") as word_file:
            self._words = []
            for line in word_file:
                self._words.append(line.strip())
        self._BLUE_CARD_STARTING_COUNT = 9
        self._RED_CARD_STARTING_COUNT = 8

    def create_new_game(self, name, player1a, player1b, player2a, player2b):
        board = [{"word": self._words[int(pos)], "guess": card_value.NONE, "actual": card_value.NONE} for pos in random.sample(range(len(self._words)), 25)]

        blue_to_place = self._BLUE_CARD_STARTING_COUNT
        while blue_to_place > 0:
            index = random.randint(0,24)
            if board[index]['actual'] == card_value.NONE:
                board[index]['actual'] = card_value.BLUE
                blue_to_place -= 1

        red_to_place = self._RED_CARD_STARTING_COUNT
        while red_to_place > 0:
            index = random.randint(0,24)
            if board[index]['actual'] == card_value.NONE:
                board[index]['actual'] = card_value.RED
                red_to_place -= 1

        assassin_to_place = 1
        while assassin_to_place > 0:
            index = random.randint(0,24)
            if board[index]['actual'] == card_value.NONE:
                board[index]['actual'] = card_value.ASSASSIN
                assassin_to_place -= 1

        game_id = self._storage.create_game(name, player1a, player1b, player2a, player2b, json.dumps(board))
        return { "game_id": game_id }

    def _check_valid_action(self, game_id, player_id):
        game_detail = self._storage.get_game(game_id)

        if game_detail['ended'] is True:
            raise GameException("Game '%s' has already ended" % game_detail['name'])

        if player_id not in [game_detail['player1a'], game_detail['player1b'], game_detail['player2a'], game_detail['player2b']]:
            raise GameException("%s is not part of game %s" % (player_id, game_detail['name']))

    def end_game(self, game_id, player_id):
        self._check_valid_action(game_id, player_id)
        self._storage.end_game(game_id)

    def get_game_detail(self, game_id):
        game_detail = self._storage.get_game(game_id)
        return game_detail

    def get_player_role(self, game_id, player_id):
        game_detail = self._storage.get_game(game_id)
        return 'guesser' if player_id in game_detail['guessers'] else 'cluer'

    def obscure_answers(self, gamestate):
        for card in gamestate['board']:
            if card['guess'] == card_value.NONE:
                card['actual'] = card_value.NONE

    def get_game_state(self, game_id):
        last_turn = self._storage.get_last_turn(game_id)
        found_blue, found_red = self._get_remaining_counts(last_turn['board'])
        last_turn['remaining_blue'] = self._BLUE_CARD_STARTING_COUNT - found_blue
        last_turn['remaining_red'] = self._RED_CARD_STARTING_COUNT - found_red
        return last_turn

    def _get_remaining_counts(self, board):
        found_red = 0
        found_blue = 0
        for card in board:
            if card['guess'] != card_value.NONE and card['actual'] == card_value.RED:
                found_red += 1
            elif card['guess'] != card_value.NONE and card['actual'] == card_value.BLUE:
                found_blue += 1
        return (found_blue, found_red)

    def _is_game_over(self, board):
        for card in board:
            if card['guess'] != card_value.NONE and card['actual'] == card_value.ASSASSIN:
                return True

        found_blue, found_red = self._get_remaining_counts(board)
        return found_blue >= self._BLUE_CARD_STARTING_COUNT or found_red >= self._RED_CARD_STARTING_COUNT

    def make_guess(self, game_id, player_id, guess_word):
        self._check_valid_action(game_id, player_id)

        last_turn = self._storage.get_last_turn(game_id)
        board = last_turn['board']
        expected_player = last_turn['expected_player']
        expected_team = last_turn['expected_team']
        guessers = last_turn['guessers']
        cluers = last_turn['cluers']
        clue = last_turn['clue']
        clue_number = last_turn['clue_number']
        guess_remaining = last_turn['guess_remaining']

        if player_id != expected_player:
            raise GameException("%s is next to act, not %s" % ('Nobody' if expected_player is None else expected_player, player_id))

        if player_id not in guessers:
            raise GameException("%s should be guessing, not giving a clue" % (expected_player))

        if guess_word is None:
            guess_remaining = 0
        else:
            for card in board:
                if card['word'] == guess_word:
                    card['guess'] = expected_team
                    if card['guess'] == card['actual']:
                        guess_remaining -= 1
                    else:
                        guess_remaining = 0

        if guess_remaining > 0:
            next_player = expected_player
            next_team = expected_team
        else:
            next_player = cluers[1] if player_id == guessers[0] else cluers[0]
            next_team = card_value.RED if player_id == guessers[0] else card_value.BLUE
            clue = None
            clue_number = 0

        if self._is_game_over(board):
            self._storage.end_game(game_id)
            expected_player = None

        turn_id = self._storage.add_new_turn(game_id, expected_player, expected_team, next_player, next_team, guess_word, guess_remaining, clue, clue_number, json.dumps(board))

        return {"turn_id": turn_id}

    def give_clue(self, game_id, player_id, clue_word, clue_number):
        self._check_valid_action(game_id, player_id)

        last_turn = self._storage.get_last_turn(game_id)

        board = last_turn['board']
        expected_player = last_turn['expected_player']
        expected_team = last_turn['expected_team']
        guessers = last_turn['guessers']
        cluers = last_turn['cluers']

        if clue_number < 1:
            raise GameException("Clue number must be >= 1, %s found" % (clue_number))

        if player_id != expected_player:
            raise GameException("%s is next to act, not %s" % (expected_player, player_id))

        if player_id not in cluers:
            raise GameException("%s should be giving a clue, not guessing" % (expected_player))

        next_player = guessers[0] if player_id == cluers[0] else guessers[1]
        next_team = expected_team

        turn_id = self._storage.add_new_turn(game_id, expected_player, expected_team, next_player, next_team, None, int(clue_number) + 1, clue_word, clue_number, json.dumps(board))
        return {"turn_id": turn_id}

    def get_player_games(self, player_id):
        return self._storage.get_player_games(player_id)

    def get_player_game_names(self, player_id):
        return self._storage.get_player_game_names(player_id)

if __name__ == '__main__':
    pass

