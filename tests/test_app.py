import unittest

from src.dinjections.app import *


class TestClass0:
    pass


class TestClass1:
    pass


class TestClass2:
    pass


class TestClass3:
    pass

    def run(self):
        pass


def new_test_class_3(p: NamedProvider("t1", TestClass1), p2: NamedProvider("t2", TestClass1), r: TestClass2) -> TestClass3:
    return TestClass3()


def new_test_class_3_no_hint(p: NamedProvider("t1", TestClass1), p2: NamedProvider("t2", TestClass1), r: TestClass2):
    return TestClass3()


def new_test_class_3_no_hint_input(p: NamedProvider("t1", TestClass1), p2: NamedProvider("t2", TestClass1), r) -> TestClass3:
    return TestClass3()


def invoker(l: Lifecycle, t: TestClass3):
    l.append_hook(Hook(
        on_start=lambda: {
            t.run()
        },
    ))

def invoker_no_hint(l: Lifecycle, t):
    l.append_hook(Hook(
        on_start=lambda: {
            t.run()
        },
    ))

class TestApp(unittest.TestCase):
    
    def test_app(self):
        try:
            app = App(
                ProvideOption(
                    # test named provider
                    NamedProvider("t1", TestClass1),
                    NamedProvider("t2", TestClass1),
                ),
                # test modular implementation
                ProvideOption(
                    TestClass2,
                    new_test_class_3,
                ),
                InvokeOption(
                    invoker,
                ))
            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)

    def test_missing_dependency(self):
        exc = None
        try:
            provides = ProvideOption()
            app = App(
                provides,
                InvokeOption(
                    invoker,
                ))
        
            app.run()
        except Exception as e:
            exc=e
        
        self.assertIsInstance(exc, MissingDependencyError)

    def test_dependency_type_error(self):
        exc = None
        try:
            provides = ProvideOption(
                    NamedProvider("t1", TestClass1),
                    NamedProvider("t2", TestClass2),
                    TestClass2,
                    new_test_class_3,
            )
            app = App(
                provides,
                InvokeOption(
                    invoker,
                ))
        
            app.run()
        except Exception as e:
            exc=e
        
        self.assertIsInstance(exc, DependencyTypeError)

    def test_missing_hint_error(self):
        exc = None
        try:
            provides = ProvideOption(
                    NamedProvider("t1", TestClass1),
                    NamedProvider("t2", TestClass1),
                    TestClass2,
                    new_test_class_3_no_hint,
            )
            app = App(
                provides,
                InvokeOption(
                    invoker,
                ))
        
            app.run()
        except Exception as e:
            exc=e
        
        self.assertIsInstance(exc, MissingHintError)

    def test_missing_hint_error_input_invoke(self):
        exc = None
        try:
            provides = ProvideOption(
                    NamedProvider("t1", TestClass1),
                    NamedProvider("t2", TestClass1),
                    TestClass2,
                    new_test_class_3,
            )
            app = App(
                provides,
                InvokeOption(
                    invoker_no_hint,
                ))
        
            app.run()
        except Exception as e:
            exc=e
        
        self.assertIsInstance(exc, MissingHintError)

    def test_missing_hint_error_input_provide(self):
        exc = None
        try:
            provides = ProvideOption(
                    NamedProvider("t1", TestClass1),
                    NamedProvider("t2", TestClass1),
                    TestClass2,
                    new_test_class_3_no_hint_input,
            )
            app = App(
                provides,
                InvokeOption(
                    invoker,
                ))
        
            app.run()
        except Exception as e:
            exc=e
        
        self.assertIsInstance(exc, MissingHintError)


if __name__ == '__main__':
    unittest.main()
