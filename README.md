# DInjections

This project implements a dependency injection framework in Python, based on uber's fx package.

It works as a modular dependency injection framework, where you can define provision of dependencies, using options pattern and hints to define which dependencies should be provided.

It also implements lifecycle management, where you can define hooks to be executed on start and stop.

Dependencies are only initialized when they are needed, even if provided.


## Installation

```bash
pip install dinjections
```

## Usage

```python
from dinjections import App, ProvideOption, InvokeOption, Hook, Lifecycle, NamedProvider


# Define a class that will be injected
class Dependency0:
  pass

# Define a class that will be injected and has dependencies of the same type
class Dependency1:
  def __init__(self, d0_1: NamedProvider("d0_1", Dependency0), d0_2: NamedProvider("d0_2", Dependency0)):
    self.d0_1 = d0_1
    self.d0_2 = d0_2

  def run(self):
    print("Dependency1 running")

# Define another class that will be injected
class Dependency2:
    def __init__(self, d1: Dependency1):
        self.d1 = d1

    def run(self):
        self.d1.run()

# Function that returns a dependency
def new_dep_2(d1: Dependency1) -> Dependency2:
    return Dependency2()

# function that will be invoked
def invoker(l: Lifecycle, d: Dependency2):
    l.append_hook(Hook(
        on_start=lambda: {
            d.run()
        },
    ))

app = App(
    ProvideOption(
        # dependency can be initiliazed passing it's class
        Dependency1,
        # and also with a function that returns the object
        new_dep_2,
        # you can also define a name for the dependency, in case there is more than one dependency of the same type
        NamedProvider("d0_1", Dependency0),
        NamedProvider("d0_2", Dependency0),
    ),
    InvokeOption(
        invoker,
    ))

app.run()
```


## Dependencies of the same type

If you have dependencies of the same type, you can use the `NamedProvider` class to define a name for the dependency, and then use it to inject the dependency (as shown above).

If this is not done, a dependency will override the previous.

## Lifecycle

You can define hooks to be executed on start and stop of the application.

Currently hooks are executed in the order they are defined, with no support for concurrency.

```python 
from dinjections import App, Hook, Lifecycle


def invoker(l: Lifecycle):
    l.append_hook(Hook(
        on_start=lambda: {
            print("Invoking 1")
        },
        on_stop=lambda: {
            print("Stopping 1")
        },
    ))
    l.append_hook(Hook(
        on_start=lambda: {
            print("Invoking 2")
        },
        on_stop=lambda: {
            print("Stopping 2")
        },
    ))

app = App(
  InvokeOption(
        invoker,
    )
)
app.run()
```
