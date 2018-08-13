import base64
import M2Crypto
from debug_config import Config
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class UserModel:
    def __init__(self):
        #eng = create_engine("mysql://testuser:test623@localhost/testdb")
        #conn_str = 'mysql://%s:%s@%s/%s' % (Config.user, Config.password, Config.host, Config.db)
        conn_str = 'mysql://%s:%s@%s/%s' % ('', '', '', '')
        eng = create_engine(conn_str)
        #eng = create_engine("mysql://testuser:test623@localhost/testdb")
        self.db = eng.connect()
        #self.db = torndb.Connection(Config.host, Config.db, user=Config.user, password=Config.password, connect_timeout=5)

    def get_user_id_from_session(self, session):
        query = 'SELECT _user_id from ic_user_session WHERE _session_hash = MD5(%s)' % session
        res = self.db.execute(query)
        if not res:
            return None

        return res.fetchone()[0]

    def get_user_id_from_email(self, email):
        query = 'SELECT _id from ic_user WHERE _unique_id = %s', email
        res = self.db.execute(query)
        if not res:
            return None

        return res.fetchone()[0]

    def get_user_id_from_login(self, email, password_hash):
        query = 'SELECT _id from ic_user WHERE _unique_id = %s and _password_hash = MD5(%s)' % (email, password_hash)
        res = self.db.execute(query)
        if not res:
            return None

        return res.fetchone()[0]

    # def get_user_id_from_openid_login(self, email):
    #     res = self.db.get('SELECT _id from ic_user WHERE _unique_id = %s and _password_hash = MD5(%s)', email, password)
    #     if not res:
    #         return None
    #
    #     return res['_id']

    def create_user_in_db(self, user_email, password, is_open_id=False):
        user_id = self.db.execute_lastrowid('INSERT INTO ic_user (_unique_id, _password_hash, _is_openid, _ts_created) VALUES (%s, MD5(%s), %s, NOW())',
                                            user_email, password, is_open_id)
        return user_id

    def create_session(self, user_id):
        user_id = int(user_id)
        session = self.generate_session_id()
        self.db.execute_lastrowid('INSERT INTO ic_user_session(_user_id, _session_hash, _ts_created) '
                                  'VALUES (%s, MD5(%s), NOW())', user_id, session)
        return session

    def destroy_sessions(self, user_id, session_hash=None):
        query = 'DELETE from ic_user_session WHERE _user_id = %s'
        query_args = []
        query_args.append(user_id)
        if session_hash:
            query += ' and _session_hash = %s'
            query_args.append(session_hash)

        row_count = self.db.delete(query, *query_args)
        #todo:handle exception and return False
        if not row_count:
            return False
        return True

    def generate_session_id(self):
        return base64.b64encode(M2Crypto.m2.rand_bytes(16))

    def generate_reset_password_link_id(self):
        return base64.b64encode(M2Crypto.m2.rand_bytes(16))

    def create_reset_password_link_id(self, user_id):
        user_id = int(user_id)
        reset_id = self.generate_reset_password_link_id()
        self.db.execute_lastrowid('INSERT INTO ic_user_reset(_user_id, _unique_reset_id, _ts_created) '
                                  'VALUES (%s, %s, NOW())', user_id, reset_id)
        return reset_id

    def get_userid_from_reset_password_link_id(self, reset_id):
        res = self.db.get('SELECT _user_id from ic_user_reset WHERE _unique_reset_id = %s', reset_id)
        if not res:
            return None

        return res['_user_id']

    def change_password(self, user_id, password):
        ret = self.db.execute_lastrowid('UPDATE ic_user SET _password_hash = MD5(%s) where _user_id = %s',
                                            password, user_id)
        if not ret:
            return False
        else:
            return True

if __name__ == '__main__':
    user_model = UserModel()
    email= ''
    password = ''
    user_id = user_model.get_user_id_from_email(email)
    user_id = user_model.create_user_in_db(email, password)
    user_id = user_model.get_user_id_from_login(email, password)

    print(user_id)
    session = user_model.create_session(user_id)
    print(session)
