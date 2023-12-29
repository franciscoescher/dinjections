from typing import List

from .exceptions import *
from .lifecycle import *
from .module import *
from .options import *


class App:
    def __init__(self, *args: List[Module | Option]):
        # container and provides are shared between all modules
        self.container = {}
        self.provides: Dict[str, ProvideTarget] = {}
        # list of modules to be run
        self.modules: List[Module] = []

        options = []
        for arg in args:
            if isinstance(arg, Module):
                arg.register_container(self.container)
                self.provides.update(arg.get_provides())
                self.modules.append(arg)
            elif isinstance(arg, Option):
                options.append(arg)

        self.root = Module(*options)
        self.root.register_container(self.container)
        self.provides.update(self.root.get_provides())
        self.modules.append(self.root)

        for module in self.modules:
            module.set_provides(self.provides)

    def run(self):
        for module in self.modules:
            for invoke in module._invokes:
                inject = module.build_dependencies(invoke)
                try:
                    invoke.callable(*inject)
                except TypeError as e:
                    if "missing" in str(e):
                        raise MissingHintError(str(e), "verify if all hints are set")
                    raise e
                module.lifecycle.start()
