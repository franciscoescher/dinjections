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
from dinjections import App, Provide, Invoke, Hook, Lifecycle, Provider


# Define a class that will be injected
class Dependency0:
  pass

# Define a class that will be injected and has dependencies of the same type
class Dependency1:
  def __init__(self, d0_1: Provider(Dependency0, name="d0_1"), d0_2: Provider(Dependency0, name="d0_2")):
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
def register_hooks(l: Lifecycle, d: Dependency2):
    l.append_hook(Hook(
        on_start=lambda: {
            d.run()
        },
    ))

app = App(
    Provide(
        # dependency can be initiliazed passing it's class
        Dependency1,
        # and also with a function that returns the object
        new_dep_2,
        # you can also define a name for the dependency, in case there is more than one dependency of the same type
        Provider(Dependency0, name="d0_1"),
        Provider(Dependency0, name="d0_2"),
    ),
    Invoke(
        register_hooks,
    ))

app.run()
```


## Dependencies of the same type

If you have dependencies of the same type, you can use the `Provider` class to define a name for the dependency with the name argument, and then use it to inject the dependency (as shown above).

If this is not done, a dependency will override the previous.

## Dependency inheritance

If you have a dependency that inherits from another, you can use the `Provider` class to define the dependency with a name argument, and then use it to inject the dependency (as shown below).

```python
# Define a class that will be injected
class TestClass4(TestClass3):
    pass

# expects a dependency of type TestClass3, but will accept TestClass4 named "t1"
def register_hooks(l: Lifecycle, t: TestClass3):
    l.append_hook(Hook(
        on_start=lambda: {
            t.run()
        },
    ))

app = App(
    Provide(
        # provides names dependency that inherites from expected class TestClass3
        Provider(TestClass4, name=TestClass3),
    ),
    Invoke(
        register_hooks,
    ))

app.run()
```


## Grouped dependencies

You can group dependencies setting the `group` parameters to `True` in a `Provider`. This will make the dependency be injected as a list of dependencies, with all the dependencies that were provided with the same name.

```python
class MyDependency:
    def __init__(self):

    def run(self):
        print("MyDependency running")

def register_hooks(l: Lifecycle, d: Provider(MyDependency, group=True)):
    # d is now a list of MyDependency, with all the dependencies named "md" that were provided
    for t in d:
        l.append_hook(Hook(
            on_start=lambda: {
                t.run()
            },
        ))

app = App(
    Provide(
        Provider(MyDependency, group=True),
        Provider(MyDependency, group=True),
    ),
    Invoke(
        register_hooks,
    ))
app.run()
```


## Lifecycle

You can define hooks to be executed on start and stop of the application.

Currently hooks are executed in the order they are defined, with no support for concurrency.

```python 
from dinjections import App, Hook, Lifecycle


def register_hooks(l: Lifecycle):
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
    Invoke(
        register_hooks,
    )
)
app.run()
```
