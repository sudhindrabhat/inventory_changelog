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

#open id logins should not come here
#for this u need to be authenticated in first place, u enter old as well as new password
class ChangePasswordHandler(BaseAuthenticatedHandler):
    def post(self, *args, **kwargs):
        email = self.get_argument('user_email', None)
        if not email:
            raise InvalidInput('user email cannot be empty')
        old_password = self.get_argument('old_password', None)
        if not old_password:
            raise InvalidInput('old password cannot be empty')

        user_model = UserModel()
        user_id = user_model.get_user_id_from_login(email, old_password)
        if not user_id:
                #raise auth error
                raise InvalidInput('wrong old password')
        new_password = self.get_argument('new_password', None)
        if not new_password:
            raise InvalidInput('new password cannot be empty')

        status = user_model.change_password(user_id, new_password)
        if status:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()
        self.finish(view)

#handles get for /password/reset?key=uuid and gives a form for the page
#we can impement this in the webserver as well. the page takes uuid and creates a form with invisible uuid
#it also has password validation.
class ResetPasswordFormHandler(BaseHandler):
    def get(self, *args, **kwargs):
        pass

#from the page the post request comes with uuid and new password (client has to do password confirmation by having to dialogs)
class ResetPasswordHandler(BaseHandler):
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

#send a mail with this link: /password/reset?key=uuid
class ForgotPasswordHandler(BaseHandler):
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

class DestroySessionHandler(BaseAuthenticatedHandler):
    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        user_id = self.get_current_user()
        user_model = UserModel()
        destroy_all = self.get_argument('destroy_all', None)
        if destroy_all:
            session_hash=None
        else:
            session_hash = self.get_current_session()
        status = user_model.destroy_sessions(user_id, session_hash)
        if status is True:
            view = JsonView().set_data({'status': 'success'}).render()
        else:
            view = JsonView().render()

        self.finish(view)


