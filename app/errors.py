
class QuarantinableError(Exception):
    """
    Exception to be raised to indicate that the survey submission requires quarantining.
    This should be used when there is no chance of success e.g. the submission is missing a required field.
    """
    pass


class RetryableError(Exception):
    """
    Exception to be raised to indicate that the survey submission should be retried.
    This should be used when the failure was caused by circumstances outside of this services
    control that might change e.g. another service being down.
    """
    pass
