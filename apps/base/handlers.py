import logging

from django.utils import simplejson

from tipfy import RequestHandler, redirect, url_for
from tipfy.ext.auth import MultiAuthMixin
from tipfy.ext.jinja2 import Jinja2Mixin
from tipfy.ext.session import AllSessionMixins, SessionMiddleware


#===============================================================================
class BaseHandler(RequestHandler, MultiAuthMixin, Jinja2Mixin, AllSessionMixins):
    middleware = [SessionMiddleware]

    #---------------------------------------------------------------------------
    def render_response(self, filename, **kwargs):
        auth_session = None
        if 'id' in self.auth_session:
            auth_session = self.auth_session

        self.request.context.update({
            'auth_session': auth_session,
            'current_user': self.auth_current_user,
            'register_url': url_for('auth/register'),
            'login_url':    self.auth_login_url(),
            'logout_url':   self.auth_logout_url(),
            'current_url':  self.request.url,
        })
        self.request.context['messages'] = self.messages if self.messages else []

        return super(BaseHandler, self).render_response(filename, **kwargs)

    #---------------------------------------------------------------------------
    def redirect_path(self, default='/'):
        if '_continue' in self.session:
            url = self.session.pop('_continue')
        else:
            url = self.request.args.get('continue', '/account')

        if not url.startswith('/'):
            url = default

        return url

    #---------------------------------------------------------------------------
    def _on_auth_redirect(self):
        """Redirects after successful authentication using third party
        services.
        """
        if '_continue' in self.session:
            url = self.session.pop('_continue')
        else:
            url = '/account'

        if not self.auth_current_user:
            url = self.auth_signup_url()

        return redirect(url)
    
#===============================================================================
class HomeHandler(BaseHandler):
    #---------------------------------------------------------------------------
    def get(self, **kwargs):
        context = {}
        return self.render_response('base/home.html', **context)
