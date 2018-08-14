import base64
from debug_config import Config
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class UserModel:
    def __init__(self):
        #eng = create_engine("mysql://testuser:test623@localhost/testdb")
        conn_str = 'mysql://%s:%s@%s/%s' % (Config.user, Config.password, Config.host, Config.db)
        #conn_str = 'mysql://%s:%s@%s/%s' % ('', '', '', '')
        eng = create_engine(conn_str)
        self.db = eng.connect()

    def get_user_id_from_session(self, session):
        query = 'SELECT _user_id from ic_user_session WHERE _session_hash = MD5(%s)' % session
        res = self.db.execute(query)
        if not res:
            return None

        return res.fetchone()[0]

    def get_user_id_from_email(self, email):
        query = 'SELECT _id from ic_user WHERE _unique_id = :email'
        res = self.db.execute(text(str(query)), email=email)
        if not res:
            return None

        res = res.fetchone()
        if not res:
            return None

        return res[0]

    def get_user_id_from_login(self, email, password):
        query = 'SELECT _id from ic_user WHERE _unique_id = :email and _password_hash = MD5(:password)'
        res = self.db.execute(text(str(query)), email=email, password_hash=password)
        if not res:
            return None

        res = res.fetchone()
        if not res:
            return None

        return res[0]

    def create_user_in_db(self, user_email, password, is_open_id=False):
        res = self.db.execute(text('INSERT INTO ic_user (_unique_id, _password_hash, _is_openid, _ts_created) '
                                            'VALUES (:user_email, MD5(:password), :is_open_id, NOW())'),
                                            user_email=user_email, password=password, is_open_id=is_open_id)
        user_id = res.lastrowid
        return user_id

    def create_session(self, user_id):
        user_id = int(user_id)
        session = self.generate_session_id()
        self.db.execute(text('INSERT INTO ic_user_session(_user_id, _session_hash, _ts_created) '
                                  'VALUES (:user_id, MD5(:session), NOW())'), user_id=user_id, session=session)
        return session


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
