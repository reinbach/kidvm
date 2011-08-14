import logging

from tipfy import Response, cached_property, redirect
from tipfy.ext.auth import user_required

from apps.base.handlers import BaseHandler

from apps.account import models, forms, account_required, admin_required


#===============================================================================
class AccountBaseHandler(BaseHandler):
    #---------------------------------------------------------------------------
    @cached_property
    def acct_session(self):
        if self.auth_current_user: 
            if self.auth_current_user.is_admin:
                return models.Account.all().filter(
                    'user =', self.auth_current_user
                ).fetch(1)[0]
            return models.Account.get_or_insert_plan(self.auth_current_user)
        return None
        
    #---------------------------------------------------------------------------
    def render_response(self, filename, **kwargs):
        self.request.context.update({
            'acct_session': self.acct_session,
        })
        if not self.request.context.get('page_id'):
            self.request.context.update({
                'page_id': 'account'
            })
        return super(AccountBaseHandler, self).render_response(filename, **kwargs)

    
#===============================================================================
class AccountHomeHandler(AccountBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, **kwargs):
        context = dict(
            account=self.acct_session
        )
        return self.render_response('account/home.html', **context)


#===============================================================================
class AccountPlanHandler(AccountBaseHandler):

    #---------------------------------------------------------------------------
    @admin_required
    def get(self, **kwargs):
        context = dict(
            plan_list=models.Plan.all()
        )
        return self.render_response('account/plan_list.html', **context)


#===============================================================================
class AccountPlanAddHandler(AccountBaseHandler):

    #---------------------------------------------------------------------------
    @admin_required
    def get(self, **kwargs):
        context = dict(
            form=self.form
        )
        return self.render_response('account/plan_crud.html', **context)

    #---------------------------------------------------------------------------
    @admin_required
    def post(self, **kwargs):
        if self.form.validate():
            self.form.save()
            return redirect(self.request.url_for('/account/plan'))
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.PlanForm(self.request)

#===============================================================================
class AccountPublicViewHandler(AccountBaseHandler):

    #---------------------------------------------------------------------------
    @account_required
    def get(self, **kwargs):
        self.acct_session.public_view_toggle()
        viewable = 'viewable' if self.acct_session.public_view else 'disabled'
        self.set_message('success', 'Pubic view of charts is now %s' % viewable, flash=True)
        return redirect(self.request.url_for('/account'))
