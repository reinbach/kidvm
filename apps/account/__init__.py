import logging

from tipfy import redirect

#---------------------------------------------------------------------------
def account_required(func):
    """
    A RequestHandler method decorator to require the current user to have an
    account saved in datastore

    .. code-block:: python

        from apps.account import account_required

        class MyHandler(RequestHandler):
            @account_required
            def get(self, **kwargs):
                return 'Only account holders can see this.

    :param func:
        The handler method to be decorated.
    :returns:
        The decorated method.
    """
    #---------------------------------------------------------------------------
    def decorated(self, *args, **kwargs):
        return _account_required(self) or func(self, *args, **kwargs)
    return decorated


#---------------------------------------------------------------------------
def admin_required(func):
    #---------------------------------------------------------------------------
    def decorated(self, *args, **kwargs):
        return _admin_required(self) or func(self, *args, **kwargs)
    return decorated

#---------------------------------------------------------------------------
def _account_required(handler):
    if not handler.acct_session:
        return redirect(handler.auth_signup_url())

#---------------------------------------------------------------------------
def _admin_required(handler):
    if not handler.auth_current_user.is_admin:
        return redirect(handler.request.url_for('/account'))
