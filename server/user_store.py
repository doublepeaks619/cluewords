import json
import mysql.connector
import hashlib, uuid
from exceptiondef import AuthException

class UserStore(object):

    def __init__(self, db_config):
        self._db_config = db_config

    @staticmethod
    def _check_password(supplied_password, salt, actual_password_hash):
        hashed_password = hashlib.sha512(supplied_password + salt).hexdigest()
        return hashed_password == actual_password_hash

    @staticmethod
    def _hash_password(supplied_password, salt):
        return hashlib.sha512(supplied_password + salt).hexdigest()

    @staticmethod
    def _get_salt():
        return uuid.uuid4().hex

    def validate(self, player_id, supplied_password):
        result, psalt, phash = self._load(player_id)
        if result is None:
            raise AuthException('login failure: username or password incorrect')
        if not UserStore._check_password(supplied_password, psalt, phash):
            raise AuthException('login failure: username or password incorrect')
        return result

    def create(self, player_id, supplied_password):
        result, psalt, phash = self._load(player_id)
        if result is None:
            cnxn = mysql.connector.connect(**self._db_config)
            cursor = cnxn.cursor()
            add_user_query = ("INSERT INTO users VALUES (%s, %s, %s)")
            salt  = UserStore._get_salt()
            cursor.execute(add_user_query, (player_id, UserStore._hash_password(supplied_password, salt), salt))
            cnxn.commit()
            cursor.close()
            cnxn.close()
        else:
             raise AuthException('login failure: username taken')

    def _load(self, player_id):
        cnxn = mysql.connector.connect(**self._db_config)
        cursor = cnxn.cursor()
        qry = "SELECT id, password_salt, password_hash FROM users WHERE id = '%s'" % player_id
        get_user_query = (qry)
        cursor.execute(get_user_query)
        result = None
        psalt = None
        phash = None
        for (username, password_salt, password_hash) in cursor:
            result = username
            psalt = password_salt
            phash = password_hash

        cnxn.close()
        return result, psalt, phash
