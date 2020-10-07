import sqlite3


class ChatIdsStorage(object):
    def __init__(self, filename_db):
        self._filename_db = filename_db
        self.init_table()

    def init_table(self):
        with sqlite3.connect(self._filename_db) as conn:
              cursor = conn.cursor()
              cursor.execute('''CREATE TABLE IF NOT EXISTS chats
                   (chat_id integer primary key, type text, username text, first_name text, last_name text)''')
              cursor.close()
              conn.commit()

    def add(self, chat):
        row_to_insert = (chat.id, chat.type, chat.username, chat.first_name, chat.last_name)
        with sqlite3.connect(self._filename_db) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO chats VALUES (?,?,?,?,?)', row_to_insert)
            cursor.close()
            conn.commit()

    def remove(self, chat_id):
        with sqlite3.connect(self._filename_db) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chats WHERE chat_id=?', (chat_id,))
            cursor.close()
            conn.commit()

    def get_chat_ids(self):
        with sqlite3.connect(self._filename_db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id FROM chats')
            ids = list(map(lambda x: x[0], cursor.fetchall()))
            cursor.close()
            return ids
