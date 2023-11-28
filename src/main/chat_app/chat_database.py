from datetime import datetime
from typing import List, Tuple

from .sqlite import BaseAdaptiveDatabase, Column, Dtype

_CHAT_TABLE_NAME = 'chat'


class ChatDatabase(BaseAdaptiveDatabase):
    def __init__(self, directory, name):
        super().__init__(directory, name)
        self._init_table()

    def _init_table(self):
        if not self.check_table(_CHAT_TABLE_NAME):
            self.table_init(
                table_name=_CHAT_TABLE_NAME,
                columns=[
                    Column(name='username', dtype=Dtype.TEXT),
                    Column(name='message', dtype=Dtype.TEXT),
                    Column(name='regdate', dtype=Dtype.TIMESTAMP),
                    Column(name='activated', dtype=Dtype.BOOLEAN)
                ]
            )

    def save_message(self, username, message) -> Tuple:
        regdate = datetime.now()
        def query(conn) -> int:
            cur = conn.cursor()
            res = cur.execute(f'INSERT INTO {_CHAT_TABLE_NAME}(username, message, regdate, activated) '
                              f'VALUES (?,?,?,?) '
                              f'RETURNING id, username, message, regdate, activated',
                              (username, message, regdate, True))
            return res.fetchone()
        return self.execute_sync(query)

    def message_disable(self, message_id):
        def query(conn) -> int:
            cur = conn.cursor()
            cur.execute(f'UPDATE {_CHAT_TABLE_NAME} SET activated=? WHERE id=?',
                        (False, message_id))
        self.execute_sync(query)

    def find_all_message(self) -> List[Tuple]:
        def query(conn):
            cur = conn.cursor()
            res = cur.execute(f'SELECT * FROM {_CHAT_TABLE_NAME}')
            return res.fetchall()
        return self.execute_sync(query)
