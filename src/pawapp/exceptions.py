
class InvalidDataException(Exception):

    def __init__(self, errors):
        self.errors = errors


class WrongNumberToCalcException(Exception):
    pass


class RatesNotFoundToCalcException(Exception):
    pass
