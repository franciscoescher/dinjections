import typing


from .app import *
from .module import *



class NamedProvider:
    def __init__(self, name: str, provider: object):
        self.name = name
        self.provider = provider



class Option:
    def apply(self, mod: Module):
        pass


class ProvideOption(Option):
    def __init__(self, *args):
        self._targets = {}
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

            raise PyDITypeError(
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
    def __init__(self, *args):
        self._targets = []
        for arg in args:
            if not callable(arg):
                raise PyDITypeError("Provide target must be callable")

            hints = typing.get_type_hints(arg)

            self._targets.append(InvokeTarget(
                callable=arg,
                requires=get_requires_from_hints(hints)))

    def apply(self, mod: Module):
        mod.add_invokes(self._targets)
