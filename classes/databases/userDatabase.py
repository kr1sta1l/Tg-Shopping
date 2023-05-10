import sqlite3
from classes.databases.database import Database
from classes.constants import botConstants
from classes.telegramBot.user import User


class UserDatabase(Database):
    def __init__(self, path_to_db):
        super().__init__(path_to_db)
        execute_command = f"""CREATE TABLE IF NOT EXISTS users (
            'id' INTEGER PRIMARY KEY,
            'user_id' INTEGER UNIQUE,
            'status' TEXT NOT NULL DEFAULT 'common',
            'lang' TEXT NOT NULL DEFAULT {botConstants.DEFAULT_LANGUAGE},
            'is_admin' INTEGER NOT NULL DEFAULT 0
        )"""
        self.create_db_if_not_exists(self.path_to_db, execute_command)

    def get_user(self, user_id: int) -> User:
        """
        Gets user from database
        :param user_id: user id to get
        :return: User object or None if user doesn't exist
        """
        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        conn.close()
        if user_info is None:
            return None
        return User(user_info[1], user_info[2], user_info[3], user_info[4])

    def add_user(self, user: User):
        """
        Sets user in database
        :param user: user to set
        :return: None
        """
        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()

        db_user = self.get_user(user.tg_id)
        if db_user is None:
            cursor.execute("INSERT INTO users (user_id, status, lang, is_admin) VALUES (?, ?, ?, ?)",
                           (user.tg_id, user.status, user.language, user.is_admin))
        else:
            cursor.execute("UPDATE users SET status = ?, lang = ?, is_admin = ? WHERE user_id = ?",
                           (user.status, user.language, user.is_admin, user.tg_id))
        conn.commit()
        conn.close()
