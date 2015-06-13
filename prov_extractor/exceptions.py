class UnknownSource(Exception):
    def __init__(self, source):
        message = 'unknown source: {}'.format(source)
        super(UnknownSource, self).__init__(message)


class SourceNotSupported(Exception):
    def __init__(self, source):
        message = 'source not supported: {}'.format(source)
        super(SourceNotSupported, self).__init__(message)
