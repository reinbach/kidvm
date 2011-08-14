from tipfy import Rule

#---------------------------------------------------------------------------
def get_rules(app):
    rules = [
        Rule(
            '/account',
            endpoint='/account',
            handler='apps.account.handlers.AccountHomeHandler'
        ),
        Rule(
            '/account/plan',
            endpoint='/account/plan',
            handler='apps.account.handlers.AccountPlanHandler'
        ),
        Rule(
            '/account/plan/add',
            endpoint='/account/plan/add',
            handler='apps.account.handlers.AccountPlanAddHandler'
        ),
        Rule(
            '/account/public/toggle',
            endpoint='/account/public/toggle',
            handler='apps.account.handlers.AccountPublicViewHandler'
        ),
    ]
    return rules
