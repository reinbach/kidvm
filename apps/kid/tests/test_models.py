import datetime
import unittest

from tipfy import RequestHandler, Tipfy
from tipfy.ext.auth.model import User

from google.appengine.api import apiproxy_stub_map, datastore_file_stub
from google.appengine.ext import db

from apps.account.models import Account
from apps.kid import models


#===============================================================================
class TestBaseModel(unittest.TestCase):
    #---------------------------------------------------------------------------
    def setUp(self):
        datastore_stub = apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map[
            'datastore_v3'
        ]
        datastore_stub.Clear()
        self.app = Tipfy()

        # accounts
        self.user_1 = User(
            username='user_1',
            password='pass',
            session_id='1',
            auth_id='own|user_1'
        )
        self.user_1.put()
        self.account_active = Account(
            user=self.user_1
        )
        self.account_active.put()

        # kids
        self.kid_active = models.Kid(
            account=self.account_active,
            name='Kid 1',
            opening_balance=10.00
        )
        self.kid_active.put()
        self.kid_new = models.Kid(
            account=self.account_active,
            name='Kid 2',
            opening_balance=20.00
        )
        self.kid_new.put()
        self.kid_old = models.Kid(
            account=self.account_active,
            name='Kid 3',
            opening_balance=35.00
        )
        self.kid_old.put()

        # allowance
        self.allowance_active = models.Allowance(
            kid=self.kid_active,
            period='Weekly',
            period_day=5,
            amount=1.00,
            is_active=True
        )
        self.allowance_active.put()

        # transaction
        self.transaction_positive = models.Transaction(
            kid=self.kid_active,
            transaction_date=datetime.date(2010, 2, 12),
            amount=10.00,
            category='Birthday',
            description='Gift from Granny',
        )
        self.transaction_positive.put()
        self.transaction_negative = models.Transaction(
            kid=self.kid_active,
            transaction_date=datetime.date(2009, 2, 12),
            amount=-10.00,
            category='Game',
            description='Mario Bros',
        )
        self.transaction_negative.put()
        self.transaction_allowance = models.Transaction(
            kid=self.kid_active,
            transaction_date=datetime.date(2008, 2, 12),
            amount=1.00,
            category='Allowance',
            allowance=self.allowance_active
        )
        self.transaction_allowance.put()
        self.transaction_new_1 = models.Transaction(
            kid=self.kid_new,
            transaction_date=datetime.date.today() - datetime.timedelta(25),
            amount=10.00,
            category='Birthday',
            description='Gift'
        )
        self.transaction_new_1.put()
        self.transaction_new_2 = models.Transaction(
            kid=self.kid_new,
            transaction_date=datetime.date.today() - datetime.timedelta(1),
            amount=-5.00,
            category='Game',
            description='Video Game'
        )
        self.transaction_new_2.put()
        self.transaction_old_1 = models.Transaction(
            kid=self.kid_old,
            transaction_date=datetime.date.today() - datetime.timedelta(100),
            amount=1.00,
            category='Allowance',
            description='Automatic'
        )
        self.transaction_old_1.put()
        self.transaction_old_2 = models.Transaction(
            kid=self.kid_old,
            transaction_date=datetime.date.today() - datetime.timedelta(60),
            amount=1.00,
            category='Allowance',
            description='Automatic'
        )
        self.transaction_old_2.put()
        self.transaction_old_3 = models.Transaction(
            kid=self.kid_old,
            transaction_date=datetime.date.today() - datetime.timedelta(20),
            amount=1.00,
            category='Allowance',
            description='Automatic'
        )
        self.transaction_old_3.put()


#===============================================================================
class TestKidModule(TestBaseModel):
    #---------------------------------------------------------------------------
    def test_unicode(self):
        self.assertEqual(unicode(self.kid_active), u'Kid 1')

    #---------------------------------------------------------------------------
    def test_opening_balance(self):
        self.assertEqual(self.kid_active.opening_balance, 10.00)


#===============================================================================
class TestAllowanceModule(TestBaseModel):
    #---------------------------------------------------------------------------
    def test_unicode(self):
        self.assertEqual(unicode(self.allowance_active), u'Weekly: $1.00')


    #---------------------------------------------------------------------------
    def test_create_weekly_default(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Weekly',
            period_day=5,
            amount=1.00,
            is_active=True
        ).create()
        self.assertTrue(created)
        self.assertTrue(allowance.is_active)
        self.assertEqual(models.Allowance.all().count(), 2)
        self.assertEqual(allowance.period, u'Weekly')

    #---------------------------------------------------------------------------
    def test_create_weekly_fail_above(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Weekly',
            period_day=10,
            amount=1.00,
            is_active=True
        ).create()
        self.assertFalse(created)
        self.assertEqual(models.Allowance.all().count(), 1)

    #---------------------------------------------------------------------------
    def test_create_weekly_fail_below(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Weekly',
            period_day=0,
            amount=1.00,
            is_active=True
        ).create()
        self.assertFalse(created)
        self.assertEqual(models.Allowance.all().count(), 1)

    #---------------------------------------------------------------------------
    def test_create_monthly_default(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Monthly',
            period_day=15,
            amount=1.00,
            is_active=True
        ).create()
        self.assertTrue(created)
        self.assertTrue(allowance.is_active)
        self.assertEqual(models.Allowance.all().count(), 2)
        self.assertEqual(allowance.period, u'Monthly')

    #---------------------------------------------------------------------------
    def test_create_monthly_fail_above(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Monthly',
            period_day=100,
            amount=1.00,
            is_active=True
        ).create()
        self.assertFalse(created)
        self.assertEqual(models.Allowance.all().count(), 1)


    #---------------------------------------------------------------------------
    def test_create_monthly_fail_below(self):
        allowance, created = models.Allowance(
            kid=self.kid_active,
            period=u'Monthly',
            period_day=-10,
            amount=1.00,
            is_active=True
        ).create()
        self.assertFalse(created)
        self.assertEqual(models.Allowance.all().count(), 1)



#---------------------------------------------------------------------------
def calc_month(month):
    return datetime.date(month.year, month.month, 1)

#===============================================================================
class TestTransactionModule(TestBaseModel):
    #---------------------------------------------------------------------------
    def test_unicode(self):
        self.assertEqual(unicode(self.transaction_positive), u'Birthday: $10.00')

    #---------------------------------------------------------------------------
    def test_balance(self):
        self.assertEqual(self.kid_active.balance, 11.00)

    #---------------------------------------------------------------------------
    def test_history_new(self):
        self.assertEqual(len(self.kid_new.history), 26)
        self.assertEqual(
            self.kid_new.history[0],
            (datetime.date.today() - datetime.timedelta(25), 30.00)
        )
        self.assertEqual(
            self.kid_new.history[24],
            (datetime.date.today() - datetime.timedelta(1), 25.00)
        )
        self.assertEqual(
            self.kid_new.history[25],
            (datetime.date.today(), 25.00)
        )

    #---------------------------------------------------------------------------
    def test_history_old(self):
        self.assertEqual(len(self.kid_old.history), 4)
        self.assertEqual(
            self.kid_old.history[0],
            (calc_month((datetime.date.today() - datetime.timedelta(100))), 36.00)
        )
        self.assertEqual(
            self.kid_old.history[1],
            (calc_month((datetime.date.today() - datetime.timedelta(60))), 37.00)
        )
        self.assertEqual(
            self.kid_old.history[2],
            (calc_month((datetime.date.today() - datetime.timedelta(20))), 38.00)
        )
