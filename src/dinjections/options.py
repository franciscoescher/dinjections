from typing import get_type_hints, Annotated, get_origin, get_args, Generic, TypeVar

from .app import *
from .exceptions import *
from .module import *


T = TypeVar('T', bound='Parameter')


class Parameter(Generic[T]):
    def __call__(self) -> T:
        return self


class Provide(Option):
    def __init__(self, *args):
        self._targets = {}
        for arg in args:
            if isinstance(arg, Provider):
                hints = get_hints(arg.provider.__init__)
                self.init_provider(arg, hints, arg.provider)
                continue

            # check if it is a class of any type
            if isinstance(arg, type):
                hints = get_hints(arg.__init__)
                self._targets[arg] = ProvideTarget(
                    callable=arg, provides=arg, requires=get_requires_from_hints(
                        hints)
                )
                continue

            if callable(arg):
                hints = get_hints(arg)
                if "return" not in hints:
                    raise MissingHintError(
                        "Provide target must have a return type hint"
                    )

                if isinstance(hints["return"], Provider):
                    self.init_provider(hints["return"], hints, arg)
                    continue

                if isinstance(hints["return"], type):
                    self._targets[hints["return"]] = ProvideTarget(
                        callable=arg,
                        provides=hints["return"],
                        requires=get_requires_from_hints(hints),
                    )
                    continue

            raise PyDITypeError(
                "Provide target must be a callable constructor, a class or a Provider: ", arg)

    def init_provider(self, arg: Provider, hints: dict, call: callable):
        if not arg.group:
            self._targets[arg.name] = ProvideTarget(
                callable=call,
                provides=arg.name,
                requires=get_requires_from_hints(hints),
            )

        else:
            if arg.name not in self._targets:
                self._targets[arg.name] = []

            self._targets[arg.name].append(
                ProvideTarget(
                    callable=call,
                    provides=arg.name,
                    requires=get_requires_from_hints(hints),
                )
            )

    def apply(self, mod: Module):
        mod.add_provides(self._targets)


def get_hints(arg):
    # check if has annotations
    if issubclass(type(arg), Parameter):
        return {"return": type(arg)}
    if not hasattr(arg, "__annotations__"):
        return get_type_hints(arg)
    hints = arg.__annotations__
    for key, value in hints.items():
        if get_origin(value) == Annotated:
            for a in value.__metadata__:
                if isinstance(a, Annotations):
                    hints[key] = a.to_provider(get_args(value)[0])
                    break
    return hints


class Invoke(Option):
    def __init__(self, *args):
        self._targets = []
        for arg in args:
            if not callable(arg):
                raise PyDITypeError("Provide target must be callable")

            hints = get_hints(arg)

            self._targets.append(
                InvokeTarget(
                    callable=arg, requires=get_requires_from_hints(hints))
            )

    def apply(self, mod: Module):
        mod.add_invokes(self._targets)


def get_requires_from_hints(hints) -> List[str]:
    requires = []
    for key, value in hints.items():
        if key == "return":
            continue
        else:
            requires.append(value)
    return requires
