class OpenTypeLibError(Exception):
    def __init__(self, message, location):
        Exception.__init__(self, message)
        self.location = location

    def __str__(self):
        message = Exception.__str__(self)
        return f"{self.location}: {message}" if self.location else message
