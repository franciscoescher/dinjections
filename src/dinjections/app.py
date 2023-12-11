from .exceptions import *
from .options import *
from .module import *
from .lifecycle import *


class App(Module):
    def __init__(self, *args):
        self._provides: dict = {}
        self._invokes: [InvokeTarget] = []
        self.provided: dict = {}
        self.lifecycle = Lifecycle()

        for option in args:
            if not isinstance(option, Option):
                raise PyDITypeError(
                    "App constructor arguments must be of type Option")
            option.apply(self)

    def build_dependencies(self, target: ProvideTarget | InvokeTarget) -> []:
        inject = []
        for require in target.requires:
            if require == Lifecycle:
                inject.append(self.lifecycle)
                continue

            key = require
            if isinstance(require, Provider):
                key = require.name

            if key not in self._provides:
                raise MissingDependencyError("Cannot find dependency", key)

            if key in self.provided:
                if isinstance(require, Provider) and require.provider != self.provided[key].__class__:
                    raise DependencyTypeError("Dependency is of wrong type", key,
                                              self.provided[key].__class__, "but should be of type", require.provider)
                inject.append(self.provided[key])
            else:
                provider = self.build_provider(self._provides[key])
                if isinstance(require, Provider):
                    if not require.group and require.provider != provider.__class__:
                        raise DependencyTypeError("Dependency is of wrong type", key,
                                                  provider.__class__, "but should be of type", require.provider)
                    if require.group and require.provider != provider[0].__class__:
                        raise DependencyTypeError("Dependency is of wrong type", key,
                                                  provider[0].__class__, "but should be of type", require.group)
                self.provided[key] = provider
                inject.append(provider)

        return inject

    def build_provider(self, target: ProvideTarget | list[ProvideTarget]) -> object | list[object]:
        if isinstance(target, ProvideTarget):
            inject = self.build_dependencies(target)
            try:
                return target.callable(*inject)
            except TypeError as e:
                if "missing" in str(e):
                    raise MissingHintError(
                        str(e), "verify if all hints are set")
                raise e

        elements = []
        for element in target:
            if not isinstance(element, ProvideTarget):
                raise PyDITypeError(
                    "Provide target list element must be of type ProvideTarget")
            inject = self.build_dependencies(element)
            try:
                elements.append(element.callable(*inject))
            except TypeError as e:
                if "missing" in str(e):
                    raise MissingHintError(
                        str(e), "verify if all hints are set")
                raise e
        return elements

    def run(self):
        for invoke in self._invokes:
            inject = self.build_dependencies(invoke)
            try:
                invoke.callable(*inject)
            except TypeError as e:
                if "missing" in str(e):
                    raise MissingHintError(
                        str(e), "verify if all hints are set")
                raise e
            self.lifecycle.start()
