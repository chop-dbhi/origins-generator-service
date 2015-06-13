class OriginsError(Exception):
    pass


class UnknownSource(OriginsError):
    def __init__(self, source):
        message = 'unknown source: {}'.format(source)
        super(UnknownSource, self).__init__(message)


class SourceNotSupported(OriginsError):
    def __init__(self, source):
        message = 'source not supported: {}'.format(source)
        super(SourceNotSupported, self).__init__(message)
