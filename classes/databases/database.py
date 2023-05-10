import sqlite3


class Database:
    def __init__(self, path_to_db):
        self.path_to_db = path_to_db

    @staticmethod
    def create_db_if_not_exists(path_to_db, execute_command):
        """
        Creates database if it doesn't exist
        :param execute_command:
        :param path_to_db: path to database
        :return: None
        """

        conn = sqlite3.connect(path_to_db)
        cursor = conn.cursor()
        cursor.execute(execute_command)
        conn.commit()
        conn.close()
