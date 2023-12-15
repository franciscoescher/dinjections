from .exceptions import *
from .lifecycle import *


class ProvideTarget:
    # This is a class to store the dependencies definitions within a module.
    def __init__(self, callable: callable, provides: str, requires: [str]):
        self.callable = callable
        self.provides = provides
        self.requires = requires


class InvokeTarget:
    # This is a class to store the invoke definitions within a module.
    def __init__(self, callable: callable, requires: [str]):
        self.callable = callable
        self.requires = requires


class Provider:
    # This is a class that is used to build advanced dependencies definitions.
    def __init__(self, provider: object, name: str = None, group: bool = False):
        self.provider = provider
        if name is None:
            self.name = provider
        self.name = name
        self.group = group


class Option:
    # This is the base class for the functional options pattern.
    def apply(self, mod):
        pass


class Module(Option):
    # This is a class that is used to store all the dependencies and invoke targets,
    # and also holds the lifecycle object and the built dependencies.
    def __init__(self, *args):
        self.lifecycle = Lifecycle()
        self._provides: dict = {}
        self._invokes: [InvokeTarget] = []

        for option in args:
            if not isinstance(option, Option):
                raise PyDITypeError(
                    "App constructor arguments must be of type Option")
            option.apply(self)

    def apply(self, mod):
        mod.add_provides(self._provides)
        mod.add_invokes(self._invokes)

    def register_container(self, container: dict) -> None:
        self.container = container

    def set_provides(self, provides: dict) -> None:
        self._provides = provides

    def get_provides(self) -> dict:
        return self._provides

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

            if key in self.container:
                if isinstance(require, Provider) and not issubclass(self.container[key].__class__, require.provider):
                    raise DependencyTypeError("Dependency is of wrong type", key,
                                              self.container[key].__class__, "but should be of type", require.provider)
                inject.append(self.container[key])
            else:
                provider = self.build_provider(self._provides[key])
                if isinstance(require, Provider):
                    if not require.group and not issubclass(provider.__class__, require.provider):
                        raise DependencyTypeError("Dependency is of wrong type", key,
                                                  provider.__class__, "but should be of type", require.provider)
                    if require.group and not issubclass(provider[0].__class__, require.provider):
                        raise DependencyTypeError("Dependency is of wrong type", key,
                                                  provider[0].__class__, "but should be of type", require.group)
                self.container[key] = provider
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

    def add_provides(self, targets: dict):
        if not isinstance(targets, dict):
            raise PyDITypeError("Provide targets must be a dict")
        for key, value in targets.items():
            if not isinstance(value, ProvideTarget) and not isinstance(value, list):
                raise PyDITypeError(
                    "Provide target must be of type ProvideTarget or list of ProvideTarget")
            if isinstance(value, list):
                for target in value:
                    if not isinstance(target, ProvideTarget):
                        raise PyDITypeError(
                            "Provide target list element must be of type ProvideTarget")

        self._provides = self._provides | targets

    def add_invokes(self, targets: [InvokeTarget]):
        for target in targets:
            if not isinstance(target, InvokeTarget):
                raise PyDITypeError(
                    "Invoke target must be of type InvokeTarget")
        self._invokes.extend(targets)
