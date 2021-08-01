#
#   |                |
#   __|   _ \   __|  __|     __ \   |   |
#   |     __/ \__ \  |       |   |  |   |
#  \__| \___| ____/ \__| _)  .__/  \__, |
#                           _|     ____/
#

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
