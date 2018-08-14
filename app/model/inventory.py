import base64
from debug_config import Config
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from app.common.constants import ChangeLogType

#todo:
class InventoryModel:
    def __init__(self, user_id=None):
        self.user_id=user_id
        # conn_str = 'mysql://%s:%s@%s/%s' % (Config.user, Config.password, Config.host, Config.db)
        conn_str = 'mysql://%s:%s@%s/%s' % ('', '', '', '')
        eng = create_engine(conn_str)
        # eng = create_engine("mysql://testuser:test623@localhost/testdb")
        self.db = eng.connect()
        # self.db = torndb.Connection(Config.host, Config.db, user=Config.user, password=Config.password, connect_timeout=5)

    def create_item(self, name, brand, category):
        #todo: insert within a transaction
        res = self.db.execute(text('INSERT INTO ic_item (_name, _brand, _category) '
                                   'VALUES (:name, :brand, :category)'),
                              name=name, brand=brand, category=category)
        
        item_id = res.lastrowid

        item_info = {'item_id':item_id, 'name':name}
        self.add_log(ChangeLogType.ITEM_ADD, item_info)

        return item_id

    #handle multiple ids
    def modify_item(self, ids, name=None, brand=None, category=None):
        substr = ''
        item_info = {'item_ids':ids}
        if name:
            substr = 'name=:name,'
            item_info['name'] = name
        if brand:
            substr = substr + 'brand=:brand,'
            item_info['brand'] = brand
        if category:
            substr = substr + 'category=:category,'
            item_info['category'] = category
        substr.rstrip(",")
        if len(ids) == 1:
            query = 'UPDATE ic_item SET %s WHERE _id=:item_id'

            query = query % substr
            res = self.db.execute(text(str(query)), name=name, brand=brand, category=category)
        else:
            pass

        self.add_log(ChangeLogType.ITEM_MOD, item_info)


    def delete_item(self, id):
        query = 'DELETE from ic_item WHERE _id = :item_id'
        self.db.execute(text(str(query)), item_id=id)
        item_info = {'item_id': id}
        self.add_log(ChangeLogType.ITEM_DEL, item_info)

        return True

    def create_variant(self, item_id, name, selling_price, cost_price, quantity, properties):
        res = self.db.execute(text('INSERT INTO ic_variant (_item_id, _name, _selling_price, _cost_price, _quantity, _properties) '
                                   'VALUES (:item_id, :name, :selling_price, :cost_price, :quantity, :properties)'),
                              item_id=item_id, name=name, selling_price=selling_price, cost_price=cost_price, quantity=quantity, properties=properties)
        variant_id = res.lastrowid

        item_info = {'item_id': item_id, 'variant_id':variant_id, 'variant_name': name}
        self.add_log(ChangeLogType.VARIANT_ADD, item_info)

        return item_id

    #handle multiple ids
    def modify_variant(self, ids, name=None, selling_price=None, cost_price=None, quantity=None, properties=None):
        substr = ''
        item_info = {'variant_ids': ids}
        if name:
            substr = 'name=:name,'
            item_info['name'] = name
        if selling_price:
            substr = substr + 'selling_price=:selling_price,'
            item_info['selling_price'] = selling_price
        if cost_price:
            substr = substr + 'cost_price=:cost_price,'
            item_info['cost_price'] = cost_price
        if quantity:
            substr = substr + 'quantity=:quantity,'
            item_info['quantity'] = quantity
        if properties:
            substr = substr + 'properties=:properties,'
            item_info['properties'] = properties
        substr.rstrip(",")
        if len(ids) == 1:
            pass
        else:
            pass

        self.add_log(ChangeLogType.VARIANT_MOD, item_info)

    def delete_variant(self, id):
        query = 'DELETE from ic_variant WHERE _variant_id = :variant_id'
        self.db.execute(text(str(query)), variant_id=id)

        item_info = {'item_id': id}
        self.add_log(ChangeLogType.VARIANT_DEL, item_info)

        return True

    #item_add,item_delete, items_mod, variant_add, variant_delete, variants_mod
    def add_log(self, change_type, info={}):
        res = self.db.execute(text('INSERT INTO ic_log (_user_id, _ts_created, _change_type, _change_info) '
                                   'VALUES (:user_id, NOW(), :change_type, :change_info)'),
                              user_id=self.user_id, change_type=change_type, change_info=info)


    def get_logs(self, ts_start, ts_end, page, limit, user_id=None):
        pass




if __name__ == '__main__':
    inv = InventoryModel()