class PyDIException(Exception):
    pass


class PyDITypeError(PyDIException, TypeError):
    pass


class MissingHintError(PyDIException):
    pass


class MissingDependencyError(PyDIException):
    pass


class DependencyTypeError(PyDIException):
    pass
