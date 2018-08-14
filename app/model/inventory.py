import base64
from debug_config import Config
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from app.common.constants import ChangeLogType
import json
import time
import decimal


class InventoryModel:
    def __init__(self, user_id=None):
        self.user_id=user_id
        conn_str = 'mysql://%s:%s@%s/%s' % (Config.user, Config.password, Config.host, Config.db)
        #conn_str = 'mysql://%s:%s@%s/%s' % ('', '', '', '')
        eng = create_engine(conn_str)
        self.db = eng.connect()

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
            substr = '_name=:name,'
            item_info['name'] = name
        if brand:
            substr = substr + '_brand=:brand,'
            item_info['brand'] = brand
        if category:
            substr = substr + '_category=:category,'
            item_info['category'] = category
            substr = substr.rstrip(",")
        if len(ids) == 1:
            query = 'UPDATE ic_item SET %s WHERE _id=:item_id'

            query = query % substr
            res = self.db.execute(text(str(query)), item_id=ids[0], name=name, brand=brand, category=category)
        else:
            query = 'UPDATE ic_item SET %s WHERE _id in :item_ids'

            query = query % substr
            res = self.db.execute(text(str(query)), item_ids=ids, name=name, brand=brand, category=category)

        self.add_log(ChangeLogType.ITEM_MOD, item_info)


    def delete_item(self, id):
        #todo: create a trigger to cleanup variants
        query = 'DELETE from ic_item WHERE _id = :item_id'
        self.db.execute(text(str(query)), item_id=id)
        item_info = {'item_id': id}
        self.add_log(ChangeLogType.ITEM_DEL, item_info)

        return True

    def create_variant(self, item_id, name, selling_price, cost_price, quantity, properties):
        res = self.db.execute(text('INSERT INTO ic_variant (_item_id, _name, _selling_price, _cost_price, _quantity, _properties) '
                                   'VALUES (:item_id, :name, :selling_price, :cost_price, :quantity, :properties)'),
                              item_id=item_id, name=name, selling_price=selling_price, cost_price=cost_price,
                              quantity=quantity, properties=json.dumps(properties))
        variant_id = res.lastrowid

        item_info = {'item_id': item_id, 'variant_id':variant_id, 'variant_name': name}
        self.add_log(ChangeLogType.VARIANT_ADD, item_info)

        return item_id

    #handle multiple ids
    def modify_variant(self, ids, name=None, selling_price=None, cost_price=None, quantity=None, properties=None):
        substr = ''
        item_info = {'variant_ids': ids}
        if name:
            substr = '_name=:name,'
            item_info['name'] = name
        if selling_price:
            substr = substr + '_selling_price=:selling_price,'
            item_info['selling_price'] = selling_price
        if cost_price:
            substr = substr + '_cost_price=:cost_price,'
            item_info['cost_price'] = cost_price
        if quantity:
            substr = substr + '_quantity=:quantity,'
            item_info['quantity'] = quantity
        if properties:
            substr = substr + '_properties=:properties,'
            item_info['properties'] = properties
        substr = substr.rstrip(",")
        if len(ids) == 1:
            query = 'UPDATE ic_variant SET %s WHERE _variant_id=:variant_id'

            query = query % substr
            res = self.db.execute(text(str(query)), variant_id=ids[0], name=name, selling_price=selling_price,
                                  cost_price=cost_price, quantity=quantity, properties=json.dumps(properties))
        else:
            query = 'UPDATE ic_variant SET %s WHERE _variant_id in :variant_ids'

            query = query % substr
            res = self.db.execute(text(str(query)), variant_ids=ids, name=name, selling_price=selling_price,
                                  cost_price=cost_price, quantity=quantity, properties=json.dumps(properties))

        self.add_log(ChangeLogType.VARIANT_MOD, item_info)

    def delete_variant(self, id):
        #todo: handle non existing userid, item etc
        query = 'DELETE from ic_variant WHERE _variant_id = :variant_id'
        self.db.execute(text(str(query)), variant_id=id)

        item_info = {'variant_id': id}
        self.add_log(ChangeLogType.VARIANT_DEL, item_info)

        return True

    #item_add,item_delete, items_mod, variant_add, variant_delete, variants_mod
    def add_log(self, change_type, info={}):
        res = self.db.execute(text('INSERT INTO ic_log (_user_id, _ts_created, _change_type, _change_info) '
                                   'VALUES (:user_id, NOW(), :change_type, :change_info)'),
                              user_id=self.user_id, change_type=change_type, change_info=json.dumps(info))


    def get_logs(self, ts_start, ts_end, offset, limit=10, user_id=None):
        feed = {'activities':[]}
        if offset is None:
            offset = 0

        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts_start)))
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts_end)))
        query = 'SELECT _user_id, _ts_created, _change_type, _change_info FROM ic_log WHERE _ts_created > :start_time AND _ts_created < :end_time '
        if user_id:
            query = query + 'and _user_id = :user_id'
        query = query + ' limit :offset,:limit'

        res = self.db.execute(text(str(query)), user_id=user_id, start_time=start_time, end_time=end_time, offset=offset, limit=limit)
        if not res:
            return None

        for row in res:
            activity = {}
            activity['user_id'] = int(row[0])
            activity['ts_created'] = row[1].strftime('%Y-%m-%d %H:%M:%S')
            activity['change_type'] = ChangeLogType.Map[int(row[2])]
            activity['change_info'] = row[3]
            feed['activities'].append(activity)
            #print(activity)

        feed['offset'] = offset + limit
        return feed




if __name__ == '__main__':
    inv = InventoryModel(1)
    inv.create_item('apple', 'zzz', 'yyy')
    #inv.delete_item(3)

    #inv.create_variant(4, 'iphone', 5, 4, 7, {'color':'black'})
    #inv.delete_variant(4)
    ids = []
    ids.append(1)
    ids.append(2)
    inv.modify_item(ids=ids, brand='lg')
    inv.get_logs(1534242000, time.time(), 0, 2, 1)
