from tipfy import Rule

#---------------------------------------------------------------------------
def get_rules(app):
    rules = [
        Rule(
            '/kid',
            endpoint='/kid',
            handler='apps.kid.handlers.KidHomeHandler'
        ),
        Rule(
            '/kid/add',
            endpoint='/kid/add',
            handler='apps.kid.handlers.KidAddHandler'
        ),
        Rule(
            '/kid/edit/<kid_key>',
            endpoint='/kid/edit',
            handler='apps.kid.handlers.KidEditHandler'
        ),
        Rule(
            '/kid/<kid_key>',
            endpoint='/kid/view',
            handler='apps.kid.handlers.KidViewHandler'
        ),

        # Allowance
        Rule(
            '/kid/allowance/add/<kid_key>',
            endpoint='/kid/allowance/add',
            handler='apps.kid.handlers.AllowanceAddHandler'
        ),
        Rule(
            '/kid/allowance/edit/<allowance_key>',
            endpoint='/kid/allowance/edit',
            handler='apps.kid.handlers.AllowanceEditHandler'
        ),
        Rule(
            '/kid/allowance/delete/<allowance_key>',
            endpoint='/kid/allowance/delete',
            handler='apps.kid.handlers.AllowanceDeleteHandler'
        ),
        Rule(
            '/kid/allowance/period',
            endpoint='/kid/allowance/period',
            handler='apps.kid.handlers.AllowancePeriodHandler'
        ),

        # Transactions
        Rule(
            '/kid/transaction/add/<kid_key>',
            endpoint='/kid/transaction/add',
            handler='apps.kid.handlers.TransactionAddHandler'
        ),
        Rule(
            '/kid/transaction/edit/<transaction_key>',
            endpoint='/kid/transaction/edit',
            handler='apps.kid.handlers.TransactionEditHandler'
        ),
        Rule(
            '/kid/transaction/delete/<transaction_key>',
            endpoint='/kid/transaction/delete',
            handler='apps.kid.handlers.TransactionDeleteHandler'
        ),

        # cron
        Rule(
            '/cron/allowance',
            endpoint='/cron/allowance',
            handler='apps.kid.handlers.CronAllowanceHandler'
        ),

        # public view
        Rule(
            '/a/<username>',
            endpoint='/public/view',
            handler='apps.kid.handlers.PublicViewHandler'
        ),
    ]
    return rules
