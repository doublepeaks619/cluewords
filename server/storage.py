class Storage(object):

    def __init__(self, db_config):
        self._db_config = db_config

    def create_game(self, name, player1a, player1b, player2a, player2b, board):
        pass

    def end_game(self, game_id):
        pass

    def get_game(self, game_id):
        pass

    def get_last_turn(self, game_id):
        pass

    def add_new_turn(self, game_id, expected_player, expected_team, next_player, next_team, guess, guess_remaining, clue, clue_number, board):
        pass

    def get_player_games(self, player_id):
        pass

    def get_player_game_names(self, player_id):
        pass
