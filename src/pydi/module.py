from .exceptions import *


class ProvideTarget:
    def __init__(self, callable: callable, provides: str, requires: [str]):
        self.callable = callable
        self.provides = provides
        self.requires = requires


class InvokeTarget:
    def __init__(self, callable: callable, requires: [str]):
        self.callable = callable
        self.requires = requires


class Module:
    def __init__(self) -> None:
        self._provides = {}
        self._invokes = []

    def add_provides(self, targets: dict):
        if not isinstance(targets, dict):
            raise PyDITypeError("Provide targets must be a dict")
        for key, value in targets.items():
            if not isinstance(value, ProvideTarget):
                raise PyDITypeError(
                    "Provide target must be of type ProvideTarget")
        self._provides = self._provides | targets

    def add_invokes(self, targets: [InvokeTarget]):
        for target in targets:
            if not isinstance(target, InvokeTarget):
                raise PyDITypeError(
                    "Invoke target must be of type InvokeTarget")
        self._invokes.extend(targets)
