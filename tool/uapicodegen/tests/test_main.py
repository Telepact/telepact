import unittest
from uapicodegen.main import main


class TestMain(unittest.TestCase):
    def test_my_function(self) -> None:
        # Add your test cases here
        self.assertEqual(main(2, 3), 5)
        self.assertEqual(main(5, 5), 10)
        self.assertEqual(main(0, 0), 0)


if __name__ == '__main__':
    unittest.main()
