class Hook:
    def __init__(self, on_start: callable = None, on_stop: callable = None):
        self.on_start = on_start
        self.on_stop = on_stop


class Lifecycle:
    def __init__(self) -> None:
        self.hooks = []

    def append_hook(self, hook: Hook):
        self.hooks.append(hook)

    def start(self):
        for hook in self.hooks:
            try:
                if callable(hook.on_start):
                    hook.on_start()
            finally:
                if callable(hook.on_stop):
                    hook.on_stop()
