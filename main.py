import typing


class PyDIException(Exception):
    pass


class TypeError(PyDIException, TypeError):
    pass


class MissingHintError(PyDIException):
    pass


class MissingDependencyError(PyDIException):
    pass


class DependencyTypeError(PyDIException):
    pass


class NamedProvider:
    def __init__(self, name: str, provider: object):
        self.name = name
        self.provider = provider


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
    _provides = {}
    _invokes = []

    def add_provides(self, targets: dict):
        for key, value in targets.items():
            if not isinstance(value, ProvideTarget):
                raise TypeError("Provide target must be of type ProvideTarget")
        self._provides = self._provides | targets

    def add_invokes(self, targets: [InvokeTarget]):
        self._invokes.extend(targets)


class Option:
    def apply(self, mod: Module):
        pass


class ProvideOption(Option):
    _targets = {}

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, NamedProvider):
                hints = typing.get_type_hints(arg.provider.__init__)
                self._targets[arg.name] = ProvideTarget(
                    callable=arg.provider,
                    provides=arg.name,
                    requires=get_requires_from_hints(hints))
                continue

            # check if it is a class of any type
            if isinstance(arg, type):
                hints = typing.get_type_hints(arg.__init__)
                self._targets[arg] = ProvideTarget(
                    callable=arg,
                    provides=arg,
                    requires=get_requires_from_hints(hints))
                continue

            if callable(arg):
                hints = typing.get_type_hints(arg)
                if "return" not in hints:
                    raise MissingHintError(
                        "Provide target must have a return type hint")
                self._targets[hints["return"]] = ProvideTarget(
                    callable=arg,
                    provides=hints["return"],
                    requires=get_requires_from_hints(hints))
                continue

            raise TypeError(
                "Provide target must be a callable constructor, a class or a NamedProvider")

    def apply(self, mod: Module):
        mod.add_provides(self._targets)


def get_requires_from_hints(hints) -> [str]:
    requires = []
    for key, value in hints.items():
        if key == "return":
            continue
        else:
            requires.append(value)
    return requires


class InvokeOption(Option):
    _targets = []

    def __init__(self, *args):
        for arg in args:
            if not callable(arg):
                raise TypeError("Provide target must be callable")

            hints = typing.get_type_hints(arg)

            self._targets.append(InvokeTarget(
                callable=arg,
                requires=get_requires_from_hints(hints)))

    def apply(self, mod: Module):
        mod.add_invokes(self._targets)


class Hook:
    def __init__(self, on_start: callable, on_stop: callable):
        self.on_start = on_start
        self.on_stop = on_stop


class Lifecycle:
    hooks = []

    def append_hook(self, hook: Hook):
        self.hooks.append(hook)

    def start(self):
        for hook in self.hooks:
            hook.on_start()
            hook.on_stop()


# Dependency injector
class App(Module):
    _provides: dict = {}
    _invokes: [InvokeTarget] = []
    provided: dict = {}
    lifecycle = Lifecycle()

    def __init__(self, *args):
        for option in args:
            if not isinstance(option, Option):
                raise TypeError(
                    "App constructor arguments must be of type Option")
            option.apply(self)

    def build_dependencies(self, target: ProvideTarget | InvokeTarget) -> []:
        inject = []
        for require in target.requires:
            if require == Lifecycle:
                inject.append(self.lifecycle)
                continue

            key = require
            if isinstance(require, NamedProvider):
                key = require.name

            if key not in self._provides:
                raise MissingDependencyError("Cannot find dependency", key)

            if key in self.provided:
                if isinstance(require, NamedProvider) and require.provider != self.provided[key].__class__:
                    raise DependencyTypeError("Dependency is of wrong type", key,
                                              self.provided[key].__class__, "but should be of type", require.provider)
                inject.append(self.provided[key])
            else:
                provider = self.build_provider(self._provides[key])
                if isinstance(require, NamedProvider) and require.provider != provider.__class__:
                    raise DependencyTypeError("Dependency is of wrong type", key,
                                              provider.__class__, "but should be of type", require.provider)
                self.provided[key] = provider
                inject.append(provider)

        return inject

    def build_provider(self, target: ProvideTarget) -> object:
        inject = self.build_dependencies(target)
        return target.callable(*inject)

    def run(self):
        for invoke in self._invokes:
            inject = self.build_dependencies(invoke)
            invoke.callable(*inject)
            self.lifecycle.start()


########################


class TestClass0:
    def __init__(self):
        print("init TestClass0")


class TestClass1:
    def __init__(self):
        print("init TestClass1")


class TestClass2:
    def __init__(self):
        print("init TestClass2")


class TestClass3:
    def __init__(self):
        print("init TestClass3")

    def run(self):
        print("Hello world")


def new_test_class_3(p: NamedProvider("t1", TestClass1), p2: NamedProvider("t2", TestClass1), r: TestClass2) -> TestClass3:
    return TestClass3()


def invoker(t: TestClass3, l: Lifecycle):
    l.append_hook(Hook(
        on_start=lambda: {
            print("starting"),
            t.run()
        },
        on_stop=lambda: print("Stopping")
    ))


app = App(
    ProvideOption(
        TestClass0,
        NamedProvider("t1", TestClass1),
        NamedProvider("t2", TestClass1),
        TestClass2,
        new_test_class_3,
    ),
    InvokeOption(
        invoker,
    ),
)
app.run()
