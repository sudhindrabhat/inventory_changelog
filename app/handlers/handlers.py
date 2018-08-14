import hashlib
import json
from random import randint
from time import sleep
import re
from tornado.web import HTTPError
from app.exception.customexceptions import InvalidInput, SessionExpired, InternalError
from app.handlers.base import BaseHandler, BaseAuthenticatedHandler, InternalAuthenticatedHandler
from app.model.inventory import InventoryModel
from app.model.user import UserModel
from app.view.templates.json.base import JsonView
from debug_config import Config
from app.common.constants import ChangeLogType
import decimal
import json


class GetApiAccessKeyHandler(BaseHandler):
    def get(self, *args, **kwargs):
        view = JsonView({'api_access_key': 'abcd'}).render()
        self.finish(view)


class HttpNotFoundHandler(BaseHandler):
    def prepare(self):
        raise HTTPError(404)


class CreateSessionHandler(BaseHandler):
    def post(self, *args, **kwargs):
        #todo: handle openid login passwordless
        email = self.get_argument('user_email', None)
        if not email:
            raise InvalidInput('user_email cannot be empty')
        password = self.get_argument('user_password', None)
        if not email:
            raise InvalidInput('user_password cannot be empty')

        is_sign_up = self.get_argument('is_sign_up', None)
        user_model = UserModel()

        user_id = user_model.get_user_id_from_email(email)
        if not user_id:
            if is_sign_up:
                #exception here is internal error... pretty serious
                user_id = user_model.create_user_in_db(email, password)
            else:
                #raise auth error
                raise InvalidInput('wrong username or password')
        else:
            user_id = user_model.get_user_id_from_login(email, password)
            if not user_id:
                #raise auth error
                raise InvalidInput('wrong username or password')

        session = user_model.create_session(user_id)
        view = JsonView({'session': session}).render()
        self.finish(view)


class CreateItemHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        #name, brand, category
        name = self.get_argument('name', None)
        if not name:
            raise InvalidInput('name cannot be empty')
        brand = self.get_argument('brand', None)
        if not brand:
            raise InvalidInput('brand cannot be empty')
        category = self.get_argument('category', None)
        if not category:
            raise InvalidInput('category cannot be empty')

        inventory_model = InventoryModel(self.current_user)
        item_id = inventory_model.create_item(name, brand, category)
        if item_id is not None:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)


class DeleteItemHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        item_id = self.get_argument('item_id', None)
        if not item_id:
            raise InvalidInput('item_id cannot be empty')

        inventory_model = InventoryModel(self.current_user)
        status = inventory_model.delete_item(item_id)
        if status is True:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)


class ModifyItemsHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        item_ids = self.get_argument('item_ids', None)
        if not item_ids:
            raise InvalidInput('item_ids cannot be empty')
        item_ids = json.loads(item_ids)
        name = self.get_argument('name', None)
        brand = self.get_argument('brand', None)
        category = self.get_argument('category', None)
        inventory_model = InventoryModel(self.current_user)
        status = inventory_model.modify_item(item_ids, name, brand, category)
        if status:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)



class CreateVariantHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        item_id = self.get_argument('item_id', None)
        if not item_id:
            raise InvalidInput('item_id cannot be empty')
        name = self.get_argument('name', None)
        if not name:
            raise InvalidInput('name cannot be empty')
        selling_price = self.get_argument('selling_price', None)
        if not selling_price:
            raise InvalidInput('selling_price cannot be empty')
        cost_price = self.get_argument('cost_price', None)
        if not cost_price:
            raise InvalidInput('cost_price cannot be empty')
        quantity = self.get_argument('quantity', None)
        if not quantity:
            raise InvalidInput('quantity cannot be empty')
        properties = self.get_argument('properties', None)
        if not properties:
            raise InvalidInput('properties cannot be empty')

        inventory_model = InventoryModel(self.current_user)
        variant_id = inventory_model.create_variant(item_id, name, selling_price, cost_price, quantity, properties)
        if variant_id is not None:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)




class DeleteVariantHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        variant_id = self.get_argument('variant_id', None)
        if not variant_id:
            raise InvalidInput('variant_id cannot be empty')

        inventory_model = InventoryModel(self.current_user)
        status = inventory_model.delete_variant(variant_id)
        if status is True:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)

class ModifyVariantsHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        variant_ids = self.get_argument('variant_ids', None)
        if not variant_ids:
            raise InvalidInput('variant_ids cannot be empty')
        variant_ids = json.loads(variant_ids)
        name = self.get_argument('name', None)
        selling_price = self.get_argument('selling_price', None)
        cost_price = self.get_argument('cost_price', None)
        quantity = self.get_argument('quantity', None)
        properties = self.get_argument('properties', None)

        inventory_model = InventoryModel(self.current_user)
        status = inventory_model.modify_variant(variant_ids, name, selling_price, cost_price, quantity, properties)
        if status:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)

class ActivityFeedHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        ts_start = self.get_argument('ts_start', None)
        if not ts_start:
            raise InvalidInput('ts_start cannot be empty')
        ts_end = self.get_argument('ts_end', None)
        if not ts_end:
            raise InvalidInput('ts_end cannot be empty')
        user_id = self.get_argument('user_id', None)
        offset = self.get_argument('offset', None)
        limit = 10
        inventory_model = InventoryModel(user_id)
        feed = inventory_model.get_logs(ts_start, ts_end, offset, limit, user_id)
        if feed:
            feed['status'] = 'success'
            view = JsonView().set_data(feed).render()
        else:
            view = JsonView().render()
        self.finish(view)





