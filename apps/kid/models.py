import datetime
import logging

from google.appengine.ext import db

from apps.account.models import Account

#===============================================================================
class Kid(db.Model):
    account = db.ReferenceProperty(Account, required=True)
    name = db.StringProperty(required=True)
    birthday = db.DateProperty(required=False)
    opening_balance = db.FloatProperty(default=0.00)
    is_active = db.BooleanProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    #---------------------------------------------------------------------------
    def __unicode__(self):
        return u'%s' % self.name
    
    #---------------------------------------------------------------------------
    @property
    def balance(self):
        # calculate balance by adding opening balance to all transaction amounts
        balance = self.opening_balance
        for trx in Transaction.all().filter('kid =', self).fetch(1000):
            balance += trx.amount
        return balance

    #---------------------------------------------------------------------------
    @property
    def allowance_count(self):
        return Allowance.all().filter('kid =', self).count()

    #---------------------------------------------------------------------------
    @property
    def history(self):
        trxs = Transaction.all().filter('kid =', self).order('transaction_date').fetch(1000)
        if not trxs:
            return {}
        # if less than 60 days old go by days else by weeks
        days = abs(datetime.date.today() - trxs[0].transaction_date).days
        dataset = {}
        total = self.opening_balance
        if days <= 30:
            for trx in trxs:
                if dataset and not dataset.get(trx.transaction_date, False):
                    while prev != trx.transaction_date:
                        prev = prev + datetime.timedelta(1)
                        dataset[prev] = total
                dataset[trx.transaction_date] = total = total + trx.amount
                prev = trx.transaction_date
            if trx.transaction_date < datetime.date.today():
                cur = trx.transaction_date
                while cur < datetime.date.today():
                    cur = cur + datetime.timedelta(1)
                    dataset[cur] = total
        else:
            for trx in trxs:
                month = datetime.date(
                    trx.transaction_date.year,
                    trx.transaction_date.month,
                    1
                )
                if dataset and not dataset.get(month, False):
                    while prev != month:
                        if prev.month == 12:
                            new_year = prev.year + 1
                            new_month = 1
                        else:
                            new_year = prev.year
                            new_month = prev.month + 1
                        prev = datetime.date(new_year, new_month, 1)
                        dataset[prev] = total
                dataset[month] = total = total + trx.amount
                prev = month
            if trx.transaction_date < datetime.date.today():
                cur = datetime.date(trx.transaction_date.year, trx.transaction_date.month, 1)
                cur_month = datetime.date(
                    datetime.date.today().year,
                    datetime.date.today().month,
                    1
                )
                while cur < cur_month:
                    if cur.month == 12:
                        new_cur_year = cur.year + 1
                        new_cur_month = 1
                    else:
                        new_cur_year = cur.year
                        new_cur_month = cur.month + 1
                    cur = datetime.date(new_cur_year, new_cur_month, 1)
                    dataset[cur] = total
        sorted_list = dataset.items()
        sorted_list.sort()
        final_list = []
        for day, amount in sorted_list:
            final_list.append((day, amount))
        return final_list
        

#===============================================================================
class Allowance(db.Model):
    kid = db.ReferenceProperty(Kid)
    period = db.StringProperty(required=True)
    period_day = db.IntegerProperty(required=True)
    amount = db.FloatProperty(required=True)
    is_active = db.BooleanProperty(default=True)
    created = db.DateTimeProperty(auto_now_add=True)

    #---------------------------------------------------------------------------
    def __unicode__(self):
        return u'%s: $%.2f' % (self.period, self.amount)

    #---------------------------------------------------------------------------
    def create(self):
        """
        period options: Weekly, Monthly
        period day options: 1-31 day

        if perion option is Weekly then period day options can be 1 - 7 which
        represent days of the week (1 - Monday ... 7 - Sunday)

        if period option is Monthly then period day option can be 1 - 31 which
        represents days of the month. Obviously if 31 is selected, that means
        the end of the month
        """
        period_day = self.period_options(self.period)
        if self.period_day in period_day:
            self.put()
            return (self, True)
        return (self, False)

    #---------------------------------------------------------------------------
    def transactions(self):
        return Transaction.filter('allowance =', self)

    #---------------------------------------------------------------------------
    @staticmethod
    def period_options(period, list_format=False):
        period_options = [(u'Weekly', range(1, 8)), (u'Monthly', range(1, 32))]
        for p, d in period_options:
            if period == p:
                if list_format:
                    # if we are dealing with weekly, we want to tweak the display format
                    if period == u'Weekly':
                        d = [
                            (1, 'Mon'),
                            (2, 'Tue'),
                            (3, 'Wed'),
                            (4, 'Thu'),
                            (5, 'Fri'),
                            (6, 'Sat'),
                            (7, 'Sun')
                        ]
                    else:
                        d = [(x, x) for x in d]
                return d
        return None

#===============================================================================
class Transaction(db.Model):
    kid = db.ReferenceProperty(Kid)
    transaction_date = db.DateProperty()
    amount = db.FloatProperty(required=True)
    category = db.CategoryProperty(required=True)
    description = db.TextProperty()
    allowance = db.ReferenceProperty(Allowance, required=False)
    modified = db.DateTimeProperty(auto_now=True)
    created = db.DateTimeProperty(auto_now_add=True)
    
    #---------------------------------------------------------------------------
    def __unicode__(self):
        return u'%s: $%.2f' % (self.category, self.amount)


