
class InvalidDataException(Exception):

    def __init__(self, errors):
        self.errors = errors


class InvalidCallPairException(Exception):
    pass


class RatesNotFoundException(Exception):
    pass


class InvalidCallIntervalException(Exception):
    pass
