import base64
from debug_config import Config
from sqlalchemy import create_engine
from sqlalchemy.sql import text

#todo:
class InventoryModel:
    def __init__(self):
        # conn_str = 'mysql://%s:%s@%s/%s' % (Config.user, Config.password, Config.host, Config.db)
        conn_str = 'mysql://%s:%s@%s/%s' % ('', '', '', '')
        eng = create_engine(conn_str)
        # eng = create_engine("mysql://testuser:test623@localhost/testdb")
        self.db = eng.connect()
        # self.db = torndb.Connection(Config.host, Config.db, user=Config.user, password=Config.password, connect_timeout=5)

    def create_item(self, name, brand, category):
        pass

    #handle multiple ids
    def modify_item(self, id, name=None, brand=None, category=None):
        pass

    def delete_item(self, id):
        pass

    def create_variant(self, id, properties):
        pass

    #handle multiple ids
    def modify_variant(self, id, properties):
        pass

    def delete_variant(self, id, properties):
        pass

    #item_add,item_delete, items_mod, variant_add, variant_delete, variants_mod
    def add_log(self, user_id, log_type):
        pass

    def get_logs(self, ts_start, ts_end, page, limit, user_id=None):
        pass




if __name__ == '__main__':
    inv = InventoryModel()