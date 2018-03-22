from restless.dj import DjangoResource
from restless.exceptions import BadRequest

from core.handlers import callevent_handler
from core.exceptions import InvalidDataException


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

        if not self.data:
            raise BadRequest('Body data is missing')

        try:
            handler = callevent_handler()
            handler.handle(self.data)
        except InvalidDataException as ide:
            raise BadRequest(ide.errors)
