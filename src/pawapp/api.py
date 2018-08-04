from restless.dj import DjangoResource
from restless.exceptions import BadRequest

from .handlers import callevent_handler, bill_handler
from .exceptions import InvalidDataException


class BaseResource(DjangoResource):

    def is_authenticated(self):
        # Open everything wide!
        # DANGEROUS, DO NOT DO IN PRODUCTION.
        return True

        # Alternatively, if the user is logged into the site...
        # return self.request.user.is_authenticated()

        # Alternatively, you could check an API key. (Need a model for this...)
        # from myapp.models import ApiKey
        # try:
        #     key = ApiKey.objects.get(key=self.request.GET.get('api_key'))
        #     return True
        # except ApiKey.DoesNotExist:
        #     return False


class CallEventResource(BaseResource):

    def create(self):

        try:
            handler = callevent_handler(self.data)
            handler.handle()
        except InvalidDataException as ide:
            raise BadRequest(ide.errors)


class BillResource(BaseResource):

    def detail(self, phone_number, month=None, year=None):

        data = {
            'phone_number': phone_number,
            'month': month,
            'year': year
        }

        try:
            handler = bill_handler(data)
            bill_data = handler.handle()
            return bill_data
        except InvalidDataException as ide:
            raise BadRequest(ide.errors)
