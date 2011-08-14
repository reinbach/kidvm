from apps.account.tests.test_base import TestBaseModel
from apps.account import models

        
#===============================================================================
class TestPlanModel(TestBaseModel):

    #---------------------------------------------------------------------------
    def test_unicode(self):
        self.assertEqual(unicode(self.plan_active), u'Plan Active (ACTIVE)')
        
    #---------------------------------------------------------------------------
    def test_create_default(self):
        # test that when creating an account it is active
        # and that if marked as default it is the only default account
        plan = models.Plan(
            name='Plan 1',
            plan_key='PLAN_1',
            default=True
        )
        plan.put()
        self.assertTrue(plan.default)
        self.assertTrue(plan.is_active)
        self.assertEqual(models.Plan.all().count(), 4)
        self.assertEqual(
            plan.plan_key,
            models.Plan.all().filter('default =', True).fetch(1)[0].plan_key
        )

    #---------------------------------------------------------------------------
    def test_create_nondefault(self):
        # test that when creating a nondefault account that it is not the default
        # and the default account does not change
        plan = models.Plan(
            name='Plan 1',
            plan_key='PLAN_1',
            default=False
        )
        plan.put()
        self.assertFalse(plan.default)
        self.assertNotEqual(
            models.Plan.all().filter('default =', True).fetch(1)[0].plan_key,
            plan.plan_key
        )
        self.assertEqual(
            models.Plan.all().filter('default =', True).fetch(1)[0].plan_key,
            self.plan_default.plan_key
        )

    #---------------------------------------------------------------------------
    def test_set_default(self):
        # test that when setting a default account all others are marked
        # as non default
        self.plan_active.default = True
        self.plan_active.put()
        self.assertTrue(
            models.Plan.all().filter('name =', 'Plan Active').fetch(1)[0].default
        )
        self.assertEqual(
            models.Plan.all().filter('default =', True).count(),
            1
        )

    #---------------------------------------------------------------------------
    def test_default_not_inactive(self):
        # test that inactive accounts become active when made a default account
        self.plan_inactive.default = True
        self.plan_inactive.put()
        self.assertTrue(
            models.Plan.all().filter('plan_key =', 'INACTIVE').fetch(1)[0].default
        )
        self.assertTrue(self.plan_inactive.is_active)

    
#===============================================================================
class TestAccountModel(TestBaseModel):

    #---------------------------------------------------------------------------
    def test_unicode(self):
        self.assertEqual(unicode(self.account_active), u'user_1 (active: True)')

    #---------------------------------------------------------------------------
    def test_current_plan(self):
        # test that current plan function works
        current_plan = self.account_active.current_plan()
        self.assertTrue(current_plan)
        self.assertEqual(
            current_plan.plan_key,
            self.plan_default.plan_key
        )

    #---------------------------------------------------------------------------
    def test_create_active(self):
        # test that accounts default to active when created
        account = models.Account(user=self.user_2)
        account.put()
        self.assertTrue(
            models.Account.all().filter('user =', self.user_2).fetch(1)[0].is_active
        )

    #---------------------------------------------------------------------------
    def test_create_noplan(self):
        # test creating an account with out providing a plan, that the default
        # plan is linked
        account = models.Account.get_or_insert_plan(self.user_2)
        plan = models.Plan.all().filter('plan_key =', 'DEFAULT').fetch(1)[0]
        account_plan = models.AccountPlan.all().filter('account =', account).fetch(1)[0]
        self.assertEqual(account_plan.plan.plan_key, plan.plan_key)
        self.assertEqual(account_plan.ended, None)

    #---------------------------------------------------------------------------
    def test_create_plan(self):
        # test creating an account with a plan that the correct plan is linked
        account = models.Account.get_or_insert_plan(
            user=self.user_2,
            plan=self.plan_active
        )
        account_plan = models.AccountPlan.all().filter('account =', account).fetch(1)[0]
        self.assertEqual(account_plan.plan.plan_key, self.plan_active.plan_key)
        self.assertEqual(account_plan.ended, None)

    #---------------------------------------------------------------------------
    def test_create_user_exists_noplan(self):
        # test creating an account with an existing user account without providing
        # a plan
        account = models.Account.get_or_insert_plan(
            user=self.user_1
        )
        self.assertEqual(account.key(), self.account_active.key())

    #---------------------------------------------------------------------------
    def test_create_user_exists_plan(self):
        # test creating an account with an existing user account with plan provided
        account = models.Account.get_or_insert_plan(
            user=self.user_1,
            plan=self.plan_active
        )
        self.assertEqual(account.current_plan().ended, None)
        self.assertEqual(models.AccountPlan.all().filter('account =', account).count(), 2)
        self.assertEqual(account.current_plan().plan_key, self.plan_active.plan_key)

    #---------------------------------------------------------------------------
    def test_create_user_plan_exists(self):
        # test creating an account with an existing user account and plan
        account = models.Account.get_or_insert_plan(
            user=self.user_1,
            plan=self.plan_default
        )
        self.assertEqual(models.AccountPlan.all().filter('account =', account).count(), 1)
        self.assertEqual(account.current_plan().plan_key, self.plan_default.plan_key)

    #---------------------------------------------------------------------------
    def test_create_user_plan_default_exists(self):
        # test creating an account with an existing user account, plan and plan is
        # default
        account = models.Account.get_or_insert_plan(
            user=self.user_1
        )
        self.assertEqual(models.AccountPlan.all().filter('account =', account).count(), 1)
        self.assertEqual(account.current_plan().plan_key, self.plan_default.plan_key)

    #---------------------------------------------------------------------------
    def test_change_account(self):
        # test changing account info, does not create a new plan link
        self.account_active.is_active = False
        self.account_active.put()
        self.assertEqual(
            models.AccountPlan.all().filter('account =', self.account_active).count(),
            1
        )
        self.assertEqual(
            self.account_active.current_plan().plan_key,
            self.plan_default.plan_key
        )
        
    #---------------------------------------------------------------------------
    def test_change_plan(self):
        # test changing plans, the old account plan is closed
        prev_account_plan = self.account_active.current_plan()
        self.account_active.change_plan(self.plan_active)
        self.assertEqual(
            models.AccountPlan.all().filter('account =', self.account_active).count(),
            2
        )
        self.assertNotEqual(
            self.account_active.current_plan().plan_key,
            prev_account_plan.plan_key
        )
        prev_account_plan = models.AccountPlan.get(prev_account_plan.key())
        self.assertTrue(prev_account_plan.ended)

    #---------------------------------------------------------------------------
    def test_change_plan_same_plan(self):
        # test attempt to change plan to the same plan
        self.account_active.change_plan(self.plan_default)
        self.assertEqual(
            models.AccountPlan.all().filter('account =', self.account_active).count(),
            1
        )
        self.assertEqual(
            self.account_active.current_plan().plan_key,
            self.plan_default.plan_key
        )
        self.assertFalse(self.account_active.current_plan().ended)

    #---------------------------------------------------------------------------
    def test_deactivate_account(self):
        # test that when deactivating account, the account plan is closed
        self.account_active.deactivate()
        self.assertFalse(self.account_active.is_active)
        account = models.Account.all().filter('user =', self.user_1).fetch(1)[0]
        self.assertEqual(account.current_plan(), None)

