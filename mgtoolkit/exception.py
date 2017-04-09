class ApplicationException(Exception):
    """ Application Exception base class"""
    # the following fails to populate exception.message
    def __init__(self, *args):
        # *args is used to get a list of the parameters passed in
        # noinspection PyPropertyAccess
        self.args = [a for a in args]
        # TODO: is there a better way to incorporate inner exception messages?
        message = ''
        for arg in self.args:
            if isinstance(arg, Exception):
                message = message + ': ' + arg.message
            else:
                message = message + ': ' + str(arg)
        self.message = message


class MetagraphException(ApplicationException):
    """ Exception occured in metagraph processing"""


# TODO: move this to the policy API
class PolicyException(ApplicationException):
    """ Exception occurres in policy processing """





