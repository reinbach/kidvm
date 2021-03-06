import logging

from tipfy import (
    Response,
    abort,
    cached_property,
    redirect,
    url_for
)
from tipfy.ext.auth import login_required
from tipfy.ext.auth.facebook import FacebookMixin
from tipfy.ext.auth.friendfeed import FriendFeedMixin
from tipfy.ext.auth.google import GoogleMixin
from tipfy.ext.auth.twitter import TwitterMixin

from apps.base.handlers import BaseHandler
import forms


#===============================================================================
class LoginHandler(BaseHandler):
    #---------------------------------------------------------------------------
    def get(self, **kwargs):
        redirect_url = self.redirect_path()

        if self.auth_current_user:
            # User is already registered, so don't display the signup form.
            return redirect(redirect_url)

        opts = {'continue': self.redirect_path()}
        context = {
            'form':                 self.form,
            'facebook_login_url':   url_for('auth/facebook', **opts),
            'friendfeed_login_url': url_for('auth/friendfeed', **opts),
            'google_login_url':     url_for('auth/google', **opts),
            'twitter_login_url':    url_for('auth/twitter', **opts),
            'yahoo_login_url':      url_for('auth/yahoo', **opts),
        }
        return self.render_response('auth/login.html', **context)

    #---------------------------------------------------------------------------
    def post(self, **kwargs):
        redirect_url = self.redirect_path()

        if self.auth_current_user:
            # User is already registered, so don't display the signup form.
            return redirect(redirect_url)

        if self.form.validate():
            username = self.form.username.data
            password = self.form.password.data
            remember = self.form.remember.data

            res = self.auth_login_with_form(username, password, remember)
            if res:
                return redirect(redirect_url)

        self.set_message(
            'error',
            'Authentication failed. Please try again.',
            life=None
        )
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.LoginForm(self.request)


#===============================================================================
class LogoutHandler(BaseHandler):
    #---------------------------------------------------------------------------
    def get(self, **kwargs):
        self.auth_logout()
        return redirect(self.redirect_path())


#===============================================================================
class SignupHandler(BaseHandler):
    #---------------------------------------------------------------------------
    @login_required
    def get(self, **kwargs):
        if self.auth_current_user:
            # User is already registered, so don't display the signup form.
            return redirect(self.redirect_path())

        return self.render_response('auth/signup.html', form=self.form)

    #---------------------------------------------------------------------------
    @login_required
    def post(self, **kwargs):
        redirect_url = self.redirect_path()

        if self.auth_current_user:
            # User is already registered, so don't process the signup form.
            return redirect(redirect_url)

        if self.form.validate():
            auth_id = self.auth_session.get('id')
            user = self.auth_create_user(self.form.nickname.data, auth_id)
            if user:
                self.auth_set_session(user.auth_id, user.session_id, '1')
                self.set_message('success', 'You are now registered. '
                    'Welcome!', flash=True, life=5)
                return redirect(redirect_url)
            else:
                self.set_message('error', 'This nickname is already '
                    'registered.', life=None)
                return self.get(**kwargs)

        self.set_message('error', 'A problem occurred. Please correct the '
            'errors listed in the form.', life=None)
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.SignupForm(self.request)


#===============================================================================
class RegisterHandler(BaseHandler):
    #---------------------------------------------------------------------------
    def get(self, **kwargs):
        redirect_url = self.redirect_path()

        if self.auth_current_user:
            # User is already registered, so don't display the registration form.
            return redirect(redirect_url)

        return self.render_response('auth/register.html', form=self.form)

    #---------------------------------------------------------------------------
    def post(self, **kwargs):
        redirect_url = self.redirect_path()

        if self.auth_current_user:
            # User is already registered, so don't process the signup form.
            return redirect(redirect_url)

        if self.form.validate():
            username = self.form.username.data
            password = self.form.password.data
            password_confirm = self.form.password_confirm.data

            if password != password_confirm:
                self.set_message('error', "Password confirmation didn't match.",
                    life=None)
                return self.get(**kwargs)

            auth_id = 'own|%s' % username
            user = self.auth_create_user(username, auth_id, password=password)
            if user:
                self.auth_set_session(user.auth_id, user.session_id, '1')
                self.set_message('success', 'You are now registered. '
                    'Welcome!', flash=True, life=5)
                return redirect(redirect_url)
            else:
                self.set_message('error', 'This nickname is already '
                    'registered.', life=None)
                return self.get(**kwargs)

        self.set_message('error', 'A problem occurred. Please correct the '
            'errors listed in the form.', life=None)
        return self.get(**kwargs)

    #---------------------------------------------------------------------------
    @cached_property
    def form(self):
        return forms.RegistrationForm(self.request)


#===============================================================================
class FacebookAuthHandler(BaseHandler, FacebookMixin):
    #---------------------------------------------------------------------------
    def head(self, **kwargs):
        """Facebook will make a HEAD request before returning a callback."""
        return Response('')

    #---------------------------------------------------------------------------
    def get(self):
        url = self.redirect_path()

        if 'id' in self.auth_session:
            # User is already signed in, so redirect back.
            return redirect(url)

        self.session['_continue'] = url

        if self.request.args.get('session', None):
            return self.get_authenticated_user(self._on_auth)

        return self.authenticate_redirect()

    #---------------------------------------------------------------------------
    def _on_auth(self, user):
        """
        """
        if not user:
            abort(403)

        # try user name, fallback to uid.
        username = user.pop('username', None)
        if not username:
            username = user.pop('uid', '')

        auth_id = 'facebook|%s' % username
        self.auth_login_with_third_party(auth_id, remember=True,
            session_key=user.get('session_key'))
        return self._on_auth_redirect()


#===============================================================================
class FriendFeedAuthHandler(BaseHandler, FriendFeedMixin):
    #---------------------------------------------------------------------------
    def get(self):
        url = self.redirect_path()

        if 'id' in self.auth_session:
            # User is already signed in, so redirect back.
            return redirect(url)

        self.session['_continue'] = url

        if self.request.args.get('oauth_token', None):
            return self.get_authenticated_user(self._on_auth)

        return self.authorize_redirect()

    #---------------------------------------------------------------------------
    def _on_auth(self, user):
        if not user:
            abort(403)

        auth_id = 'friendfeed|%s' % user.pop('username', '')
        self.auth_login_with_third_party(auth_id, remember=True,
            access_token=user.get('access_token'))
        return self._on_auth_redirect()


#===============================================================================
class TwitterAuthHandler(BaseHandler, TwitterMixin):
    #---------------------------------------------------------------------------
    def get(self):
        url = self.redirect_path()

        if 'id' in self.auth_session:
            # User is already signed in, so redirect back.
            return redirect(url)

        self.session['_continue'] = url

        if self.request.args.get('oauth_token', None):
            return self.get_authenticated_user(self._on_auth)

        return self.authorize_redirect()

    #---------------------------------------------------------------------------
    def _on_auth(self, user):
        if not user:
            abort(403)

        auth_id = 'twitter|%s' % user.pop('username', '')
        self.auth_login_with_third_party(auth_id, remember=True,
            access_token=user.get('access_token'))
        return self._on_auth_redirect()


#===============================================================================
class GoogleAuthHandler(BaseHandler, GoogleMixin):
    #---------------------------------------------------------------------------
    def get(self):
        url = self.redirect_path()

        if 'id' in self.auth_session:
            # User is already signed in, so redirect back.
            return redirect(url)

        self.session['_continue'] = url

        if self.request.args.get('openid.mode', None):
            return self.get_authenticated_user(self._on_auth)

        return self.authenticate_redirect()

    #---------------------------------------------------------------------------
    def _on_auth(self, user):
        if not user:
            abort(403)

        auth_id = 'google|%s' % user.pop('email', '')
        self.auth_login_with_third_party(auth_id, remember=True)
        return self._on_auth_redirect()
