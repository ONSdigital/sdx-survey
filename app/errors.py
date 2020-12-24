
class QuarantinableError(Exception):
    pass


class RetryableError(Exception):
    pass


class ClientError(QuarantinableError):
    pass
