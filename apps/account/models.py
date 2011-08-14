import datetime
import logging

from tipfy.ext.auth.model import User

from google.appengine.ext import db


#===============================================================================
class Plan(db.Model):
    name = db.StringProperty(required=True)
    plan_key = db.StringProperty(required=True)
    is_active = db.BooleanProperty(default=True)
    created = db.DateTimeProperty(auto_now_add=True)
    default = db.BooleanProperty()

    #---------------------------------------------------------------------------
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.plan_key)

    #---------------------------------------------------------------------------
    def put(self):
        self.set_default()
        super(Plan, self).put()

    #---------------------------------------------------------------------------
    def set_default(self):
        # if default mark all others as not default
        if self.default:
            self.is_active = True
            plan_list = Plan.all().filter('plan_key !=', self.plan_key)
            for plan in plan_list.fetch(plan_list.count()):
                plan.default = False
                plan.put()


#===============================================================================
class Account(db.Model):
    user = db.ReferenceProperty(User, required=True)
    public_view = db.BooleanProperty(default=False)
    is_active = db.BooleanProperty(default=True)
    created = db.DateTimeProperty(auto_now_add=True)

    #---------------------------------------------------------------------------
    def __unicode__(self):
        return '%s (active: %s)' % (self.user, self.is_active)

    #---------------------------------------------------------------------------
    @staticmethod
    def get_or_insert_plan(user, plan=None):
        # if account not found, then add plan to the account
        account = Account.get_or_insert('user', user=user)
        account_plan = AccountPlan.get_or_insert_plan(account, plan)
        return account

    #---------------------------------------------------------------------------
    def current_plan(self):
        if AccountPlan.all().filter('account =', self).filter('ended =', None).count():
            return AccountPlan.all().filter(
                'account =', self
            ).filter('ended =', None).fetch(1)[0]
        return None

    #---------------------------------------------------------------------------
    def change_plan(self, plan):
        return AccountPlan.get_or_insert_plan(self, plan)

    #---------------------------------------------------------------------------
    def deactivate(self):
        self.is_active = False
        if not self.current_plan().ended:
            current_plan = self.current_plan()
            current_plan.ended = datetime.datetime.now()
            current_plan.put()
        self.put()

    #---------------------------------------------------------------------------
    def public_view_toggle(self):
        self.public_view = not self.public_view
        self.put()

        
#===============================================================================
class AccountPlan(db.Model):
    #TODO add plan_rate and plan_period data
    account = db.ReferenceProperty(Account, required=True)
    plan = db.ReferenceProperty(Plan, required=True)
    #plan_rate = db.FloatProperty(required=True)
    #plan_period = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    ended = db.DateTimeProperty()

    #---------------------------------------------------------------------------
    def __unicode__(self):
        return u'%s (%s)' % (self.account.user, self.plan)

    #---------------------------------------------------------------------------
    @staticmethod
    def get_or_insert_plan(account, plan=None):
        if not plan:
            plan = Plan.all().filter('default =', True).fetch(1)[0]
        account_plan = AccountPlan.get_or_insert(
            'account',
            account=account,
            plan=plan
        )
        # if plan is the same we're all set
        # otherwise need to create a new account plan
        if account_plan.plan.plan_key != plan.plan_key:
            account_plan.ended = datetime.datetime.now()
            account_plan.put()
            account_plan = AccountPlan(
                account=account,
                plan=plan
            )
            account_plan.put()
        return account_plan
        
    #---------------------------------------------------------------------------
    @property
    def plan_key(self):
        return self.plan.plan_key
