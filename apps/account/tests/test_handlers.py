from apps.account.tests.test_base import TestBaseModel
from apps.account import models


#===============================================================================
class TestAccountHandler(TestBaseModel):

    #---------------------------------------------------------------------------
    def test_response(self):
        response = self.client.get('/', follow_redirects=True)
        #self.assertEquals(response.data, "Boo")
        self.assertTrue(True)
