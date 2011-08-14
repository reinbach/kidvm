from tipfy.ext.wtforms import Form, fields

from apps.account.models import Plan

#===============================================================================
class PlanForm(Form):
    name = fields.TextField('Name')
    plan_key = fields.TextField('Key')
    is_active = fields.BooleanField('Active')
    default = fields.BooleanField('Default')

    #---------------------------------------------------------------------------
    def save(self):
        plan = Plan(
            name=self.name.data,
            plan_key=self.plan_key.data,
            is_active=self.is_active.data,
            default=self.default.data
        )
        plan.put()
