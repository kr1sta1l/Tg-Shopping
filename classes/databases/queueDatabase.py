from classes.databases.database import Database
from classes.query import Query
import sqlite3


class QueueDatabase(Database):
    def __init__(self, path_to_db):
        super().__init__(path_to_db)
        execute_command = """CREATE TABLE IF NOT EXISTS {tb_name} (
            'id' INTEGER PRIMARY KEY,
            'user_id' INTEGER NOT NULL DEFAULT 0,
            'query' TEXT NOT NULL DEFAULT '',
            'message_id' INTEGER NOT NULL DEFAULT '',
            'banned_words' TEXT NOT NULL DEFAULT ''
            )"""
        Database.create_db_if_not_exists(self.path_to_db, execute_command.format(tb_name='common_users'))
        Database.create_db_if_not_exists(self.path_to_db, execute_command.format(tb_name='prime_users'))

    def add_to_queue(self, query: Query):
        """
        Add request to queue
        :param query: request to add
        :return: None
        """
        if query.user_status == 'prime':
            table_name = 'prime_users'
        else:
            table_name = 'common_users'

        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table_name} (user_id, query, message_id, banned_words) VALUES (?, ?, ?, ?)",
                       (query.user_id, query.query, query.message_id,
                        query.ban_words_list if query.ban_words_list is not None else ''))
        conn.commit()
        conn.close()

    def get_user_request(self, table_name: str):
        """
        Gets user request from queue
        :param table_name: table name to get request from
        :return: dict that contains all info about request from queue
        """
        # Возвращать словарь с ключами id, user_id, query, message_id
        conn = sqlite3.connect(self.path_to_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        prime_user = cursor.fetchone()
        conn.close()
        return prime_user

    def delete_user(self, table_name: str, user_id: int):
        """
        Deletes user from queue
        :param table_name: table name to delete user from
        :param user_id: user id to delete
        :return: None
        """
        conn = sqlite3.connect(self.path_to_db)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ? LIMIT 1", (user_id,))
        conn.commit()
        conn.close()
