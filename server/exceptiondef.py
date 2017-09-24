class GameException(Exception):
    def __init__(self, arg):
        super(GameException, self).__init__(arg)
        self.msg = arg

    def __str__(self):
        return str(self.msg)

class AuthException(Exception):
    def __init__(self, arg):
        super(AuthException, self).__init__(arg)
        self.msg = arg

    def __str__(self):
        return str(self.msg)