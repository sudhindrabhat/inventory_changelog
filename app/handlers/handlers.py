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



class DeleteItemHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        item_id = self.get_argument('item_id', None)
        if not item_id:
            raise InvalidInput('item_id cannot be empty')



class ModifyItemsHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        pass

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
        



class DeleteVariantHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        variant_id = self.get_argument('variant_id', None)
        if not item_id:
            raise InvalidInput('variant_id cannot be empty')

class ModifyVariantsHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        pass

class ActivityFeedHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        pass




