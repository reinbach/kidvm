from tipfy import Rule

#---------------------------------------------------------------------------
def get_rules(app):
    rules = [
        Rule(
            '/',
            endpoint='home',
            handler='apps.base.handlers.HomeHandler'
        ),
    ]
    return rules
