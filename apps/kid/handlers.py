import calendar
import datetime
import logging

from tipfy import cached_property, redirect, render_json_response
from tipfy.ext.auth.model import User

from apps.account import account_required
from apps.account.handlers import AccountBaseHandler

from apps.kid import forms, models


#===============================================================================
class KidBaseHandler(AccountBaseHandler):
    #---------------------------------------------------------------------------
    def render_response(self, filename, **kwargs):
        self.request.context.update({
            'page_id': 'kid',
            'kid_list': models.Kid.all().filter('account =', self.acct_session).fetch(1000)
        })
        return super(KidBaseHandler, self).render_response(filename, **kwargs)


#===============================================================================
class KidHomeHandler(KidBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, **kwargs):
        return self.render_response('kid/home.html')


#===============================================================================
class KidAddHandler(KidBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, **kwargs):
        context = dict(
            form=self.form
        )
        return self.render_response('kid/kid_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, **kwargs):
        if self.form.validate():
            self.form.save(self.acct_session)
            self.set_message('success', 'Added %s' % self.form.name.data, flash=True)
            return redirect(self.request.url_for('/kid'))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.KidForm(self.request)


#===============================================================================
class KidEditHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        context = dict(
            form=self.form
        )
        return self.render_response('kid/kid_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        if self.form.validate():
            self.form.populate_obj(self.kid)
            self.kid.put()
            self.set_message(
                'success',
                'Updated %s\'s information' % self.kid.name.data,
                flash=True
            )
            return redirect(self.request.url_for('/kid'))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.KidForm(self.request, obj=self.kid)


#===============================================================================
class KidViewHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        context = dict(
            kid=self.kid,
            allowance_list=models.Allowance.all().filter('kid =', self.kid).fetch(1000),
            transaction_list=models.Transaction.all().filter(
                'kid =', self.kid
            ).order('-transaction_date').fetch(1000)
        )
        return self.render_response('kid/kid.html', **context)


#===============================================================================
class AllowanceAddHandler(KidBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        context = dict(
            form=self.form,
            kid=self.kid
        )
        return self.render_response('kid/allowance_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        if self.form.validate():
            self.form.save(self.kid)
            self.set_message('success', 'Added %s' % self.form.period.data, flash=True)
            return redirect(self.request.url_for('/kid', kid_key=self.kid.key()))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.AllowanceForm(self.request)


#===============================================================================
class AllowanceEditHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, allowance_key, **kwargs):
        self.allowance = models.Allowance.get(allowance_key)
        context = dict(
            form=self.form,
            kid=self.allowance.kid
        )
        return self.render_response('kid/allowance_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, allowance_key, **kwargs):
        self.allowance = models.Allowance.get(allowance_key)
        if self.form.validate():
            self.form.populate_obj(self.allowance)
            self.allowance.put()
            self.set_message(
                'success',
                'Updated %s\'s allowance information' % self.allowance.period,
                flash=True
            )
            return redirect(self.request.url_for(
                '/kid/view',
                kid_key=self.allowance.kid.key()
            ))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.AllowanceForm(self.request, obj=self.allowance)


#===============================================================================
class AllowancePeriodHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, **kwargs):
        context = {'period': models.Allowance.period_options(
            self.request.args.get('period', ''),
            True
        )}
        return render_json_response(context)


#===============================================================================
class AllowanceDeleteHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, allowance_key, **kwargs):
        self.allowance = models.Allowance.get(allowance_key)
        kid_key = self.allowance.kid.key()
        self.allowance.delete()
        self.set_message('success', 'Deleted allowance', flash=True)
        return redirect(self.request.url_for('/kid/view', kid_key=kid_key))


#===============================================================================
class TransactionAddHandler(KidBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        context = dict(
            form=self.form,
            kid=self.kid
        )
        return self.render_response('kid/transaction_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, kid_key, **kwargs):
        self.kid = models.Kid.get(kid_key)
        if self.form.validate():
            self.form.save(self.kid)
            self.set_message(
                'success',
                'Added %s for $%.2f' % (self.form.category.data, self.form.amount.data),
                flash=True
            )
            return redirect(self.request.url_for('/kid/view', kid_key=self.kid.key()))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.TransactionForm(self.request)


#===============================================================================
class TransactionEditHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, transaction_key, **kwargs):
        self.transaction = models.Transaction.get(transaction_key)
        context = dict(
            form=self.form,
            kid=self.transaction.kid
        )
        return self.render_response('kid/transaction_crud.html', **context)

    #---------------------------------------------------------------------------
    @account_required
    def post(self, transaction_key, **kwargs):
        self.transaction = models.Transaction.get(transaction_key)
        if self.form.validate():
            self.form.populate_obj(self.transaction)
            self.transaction.put()
            self.set_message(
                'success',
                'Updated %s\'s transaction information' % self.transaction.category,
                flash=True
            )
            return redirect(self.request.url_for(
                '/kid/view',
                kid_key=self.transaction.kid.key()
            ))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.TransactionForm(self.request, obj=self.transaction)


#===============================================================================
class TransactionDeleteHandler(KidBaseHandler):
    #---------------------------------------------------------------------------
    @account_required
    def get(self, transaction_key, **kwargs):
        self.transaction = models.Transaction.get(transaction_key)
        kid_key = self.transaction.kid.key()
        self.transaction.delete()
        self.set_message(
            'success',
            'Deleted transaction %s' % self.transaction.category,
            flash=True
        )
        return redirect(self.request.url_for('/kid/view', kid_key=kid_key))


#===============================================================================
class CronAllowanceHandler(KidBaseHandler):
    # check if allowance needs to be transacted
    
    #---------------------------------------------------------------------------
    def get(self, **kwargs):
        # get current day of the week
        # get list of allowances that are weekly and match current day of the week
        # create transactions for each of them
        weekday = datetime.date.today().isoweekday()
        allowance_list = models.Allowance.all().filter(
            'period =',
            'Weekly'
        ).filter(
            'period_day =',
            weekday
        ).filter('is_active =', True).fetch(1000)
        for allowance in allowance_list:
            trx = models.Transaction(
                kid=allowance.kid,
                transaction_date=datetime.date.today(),
                amount=allowance.amount,
                category='Weekly Allowance',
                description='Automatic',
                allowance=allowance
            )
            trx.put()

        # get current day of the month
        # if last day of the month, then include all days from last day of the month
        # to 31
        # get list of allowances that are monthly and match current day of the month
        # create transactions for each of them
        day = int(datetime.date.today().strftime("%d"))
        month = int(datetime.date.today().strftime("%m"))
        year = int(datetime.date.today().strftime("%Y"))
        max_day = calendar.monthrange(year, month)[1]
        if day == max_day:
            days = range(max_day, 32)
        else:
            days = [day]
        allowance_list = models.Allowance.all().filter(
            'period =',
            'Monthly'
        ).filter(
            'period_day IN',
            days
        ).fetch(1000)
        for allowance in allowance_list:
            trx = models.Transaction(
                kid=allowance.kid,
                transaction_date=datetime.date.today(),
                amount=allowance.amount,
                category='Monthly Allowance',
                description='Automatic',
                allowance=allowance
            )
            trx.put()

        context = {'success': True}
        return render_json_response(context)


#===============================================================================
class PublicViewHandler(KidBaseHandler):
    
    #---------------------------------------------------------------------------
    def get(self, username, **kwargs):
        # find account that has matching username
        # check that account allows public view
        # if so, get chart combing kids history together
        #TODO finish this up
        user_list = User.all().filter('username =', username).fetch(1000)[0]
        logging.info(user_list)
        return self.render_response('kid/home.html')
