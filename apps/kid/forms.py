import datetime
import logging

from tipfy.ext.wtforms import Form, fields

from apps.kid.models import Kid, Allowance, Transaction


#===============================================================================
class KidForm(Form):
    name = fields.TextField(u'Name')
    birthday = fields.DateField(u'Birthday', format="%m/%d/%Y")
    opening_balance = fields.FloatField()
    is_active = fields.BooleanField(u'Active')

    #---------------------------------------------------------------------------
    def save(self, account):
        kid = Kid(
            account=account,
            name=self.name.data,
            birthday=self.birthday.data,
            opening_balance=self.opening_balance.data,
            is_active=self.is_active.data
        )
        kid.put()


#===============================================================================
class AllowanceForm(Form):
    period = fields.SelectField(u'Period', choices=[
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly')
    ])
    period_day = fields.SelectField(
        u'Day',
        choices=[(i, i) for i in range(1, 32)],
        coerce=int
    )
    amount = fields.FloatField()
    is_active = fields.BooleanField('Active')

    #---------------------------------------------------------------------------
    def save(self, kid):
        allowance = Allowance(
            kid=kid,
            period=self.period.data,
            period_day=self.period_day.data,
            amount=self.amount.data,
            is_active=self.is_active.data
        )
        allowance.put()


#===============================================================================
class TransactionForm(Form):
    transaction_date = fields.DateField(u'Transaction Date', format='%m/%d/%Y')
    amount = fields.FloatField()
    category = fields.TextField(u'Category')
    description = fields.TextField(u'Description')

    #---------------------------------------------------------------------------
    def save(self, kid):
        trx = Transaction(
            kid=kid,
            transaction_date=self.transaction_date.data,
            amount=self.amount.data,
            category=self.category.data,
            description=self.description.data
        )
        trx.put()
