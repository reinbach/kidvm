from tipfy import Rule, import_string

#---------------------------------------------------------------------------
def get_rules(app):
    rules = [
        Rule(
            '/auth/login',
            endpoint='auth/login',
            handler='apps.auth.handlers.LoginHandler'
        ),
        Rule(
            '/auth/logout',
            endpoint='auth/logout',
            handler='apps.auth.handlers.LogoutHandler'
        ),
        Rule(
            '/auth/signup',
            endpoint='auth/signup',
            handler='apps.auth.handlers.SignupHandler'
        ),
        Rule(
            '/auth/register',
            endpoint='auth/register',
            handler='apps.auth.handlers.RegisterHandler'
        ),
        
        # specific 3rd party authentication
        Rule(
            '/auth/facebook/',
            endpoint='auth/facebook',
            handler='apps.auth.handlers.FacebookAuthHandler'
        ),
        Rule(
            '/auth/friendfeed/',
            endpoint='auth/friendfeed',
            handler='apps.auth.handlers.FriendFeedAuthHandler'
        ),
        Rule(
            '/auth/google/',
            endpoint='auth/google',
            handler='apps.auth.handlers.GoogleAuthHandler'
        ),
        Rule(
            '/auth/twitter/',
            endpoint='auth/twitter',
            handler='apps.auth.handlers.TwitterAuthHandler'
        ),
        Rule(
            '/auth/yahoo/',
            endpoint='auth/yahoo',
            handler='apps.auth.handlers.YahooAuthHandler'
        ),
    ]
    return rules
