import unittest

from tipfy import RequestHandler, Tipfy
from tipfy.ext.auth.model import User
import urls

from google.appengine.api import apiproxy_stub_map, datastore_file_stub
from google.appengine.ext import db

from apps.account import models


#===============================================================================
class TestBaseModel(unittest.TestCase):
    #---------------------------------------------------------------------------
    def setUp(self):
        datastore_stub = apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map[
            'datastore_v3'
        ]
        datastore_stub.Clear()
        self.app = Tipfy()
        self.client = self.app.get_test_client()

        # plans
        self.plan_active = models.Plan(
            name='Plan Active',
            plan_key='ACTIVE',
            is_active=True,
            default=False
        )
        self.plan_active.put()
        self.plan_inactive = models.Plan(
            name='Plan InActive',
            plan_key='INACTIVE',
            is_active=False,
            default=False
        )
        self.plan_inactive.put()
        self.plan_default = models.Plan(
            name='Plan Default',
            plan_key='DEFAULT',
            is_active=True,
            default=True
        )
        self.plan_default.put()

        # accounts
        self.user_1 = User(
            username='user_1',
            password='pass',
            session_id='1',
            auth_id='own|user_1'
        )
        self.user_1.put()
        self.user_2 = User(
            username='user_2',
            password='pass',
            session_id='2',
            auth_id='own|user_2'
        )
        self.user_2.put()
        self.account_active = models.Account.get_or_insert_plan(user=self.user_1)
