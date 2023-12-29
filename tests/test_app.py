import unittest

from src.dinjections import *


class TestClass1:
    pass


class TestClass2:
    pass


class TestClass3:
    pass

    def run(self):
        pass


def new_test_class_3(
    p: Provider(TestClass1, "t1"), p2: Provider(TestClass1, "t2"), r: TestClass2
) -> TestClass3:
    return TestClass3()


def register_hooks(l: Lifecycle, t: TestClass3):
    l.append_hook(
        Hook(
            on_start=lambda: {t.run()},
        )
    )


def register_hooks_no_hint(l: Lifecycle, t):
    l.append_hook(
        Hook(
            on_start=lambda: {t.run()},
        )
    )


class TestApp(unittest.TestCase):
    def test_app(self):
        try:
            app = App(
                Provide(
                    # test named provider
                    Provider(TestClass1, "t1"),
                    Provider(TestClass1, "t2"),
                    TestClass2,
                    new_test_class_3,
                ),
                Invoke(
                    register_hooks,
                ),
            )
            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)

    def test_missing_dependency(self):
        exc = None
        try:
            app = App(
                Provide(),
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, MissingDependencyError)

    def test_dependency_type_error(self):
        exc = None
        try:
            provides = Provide(
                Provider(TestClass1, "t1"),
                Provider(TestClass2, "t2"),
                TestClass2,
                new_test_class_3,
            )
            app = App(
                provides,
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, DependencyTypeError)

    def test_missing_hint_error(self):
        def new_test_class_3_no_hint(
            p: Provider(TestClass1, "t1"), p2: Provider(TestClass1, "t2"), r: TestClass2
        ):
            return TestClass3()

        exc = None
        try:
            provides = Provide(
                Provider(TestClass1, "t1"),
                Provider(TestClass1, "t2"),
                TestClass2,
                new_test_class_3_no_hint,
            )
            app = App(
                provides,
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, MissingHintError)

    def test_missing_hint_error_input_invoke(self):
        exc = None
        try:
            provides = Provide(
                Provider(TestClass1, "t1"),
                Provider(TestClass1, "t2"),
                TestClass2,
                new_test_class_3,
            )
            app = App(
                provides,
                Invoke(
                    register_hooks_no_hint,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, MissingHintError)

    def test_missing_hint_error_input_provide(self):
        def new_test_class_3_no_hint_input(
            p: Provider(TestClass1, "t1"), p2: Provider(TestClass1, "t2"), r
        ) -> TestClass3:
            return TestClass3()

        exc = None
        try:
            provides = Provide(
                Provider(TestClass1, "t1"),
                Provider(TestClass1, "t2"),
                TestClass2,
                new_test_class_3_no_hint_input,
            )
            app = App(
                provides,
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, MissingHintError)

    def test_group(self):
        def new_test_class_3_group(
            p: Provider(TestClass1, group=True), r: TestClass2
        ) -> TestClass3:
            return TestClass3()

        try:
            app = App(
                Provide(
                    Provider(TestClass1, group=True),
                    Provider(TestClass1, group=True),
                    TestClass2,
                    new_test_class_3_group,
                ),
                Invoke(
                    register_hooks,
                ),
            )
            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)

    def test_modularity(self):
        m1 = Module(
            Provide(
                Provider(TestClass1, name="t1"),
                Provider(TestClass1, name="t2"),
            )
        )
        m2 = Module(
            Provide(
                TestClass2,
                new_test_class_3,
            ),
            Invoke(
                register_hooks,
            ),
        )
        try:
            app = App(Module(m1, m2))
            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)

    def test_callable_with_provider(self):
        def new_test_class_3_named(p: TestClass1) -> Provider(TestClass3, name="t3"):
            return TestClass3()

        def register_hooks_named(l: Lifecycle, t: Provider(TestClass3, name="t3")):
            l.append_hook(
                Hook(
                    on_start=lambda: {t.run()},
                )
            )

        try:
            app = App(
                Module(
                    Provide(
                        TestClass1,
                        new_test_class_3_named,
                    ),
                    Invoke(
                        register_hooks_named,
                    ),
                )
            )
            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)

    def test_cyclic_dependency(self):
        def new_test_class_3_cyclic(p: TestClass3) -> TestClass3:
            return TestClass3()

        exc = None
        try:
            app = App(
                Provide(new_test_class_3_cyclic),
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            exc = e

        self.assertIsInstance(exc, RecursionError)

    def test_inherited(self):
        class TestClass4(TestClass3):
            pass

        def register_hooks(l: Lifecycle, t: TestClass3):
            l.append_hook(
                Hook(
                    on_start=lambda: {t.run()},
                )
            )

        try:
            app = App(
                Provide(
                    Provider(TestClass4, name=TestClass3),
                ),
                Invoke(
                    register_hooks,
                ),
            )

            app.run()
        except Exception as e:
            self.fail("Exception: " + str(e))
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
