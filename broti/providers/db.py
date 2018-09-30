import sqlite3


class Provider(object):
    def __init__(self, bot):
        try:
            self.connstring = bot.config['db']
        except ValueError:
            return None

    def get_conn(self):
        return sqlite3.connect(self.connstring)

    def cursor(self):
        # For backwards compability
        return self.get_conn().cursor()
