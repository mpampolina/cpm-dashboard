import unittest
from test_utilities import *
import pprint
from cpm import Cpm

pp = pprint.PrettyPrinter(indent=4)


class TestCalc(unittest.TestCase):
    def setUp(self):
        self.cpm2 = Cpm(testActivities2)
        self.cpm2.run()

    def test_add(self):
        self.assertCountEqual(self.cpm2.activities, testResults2)


if __name__ == "__main__":
    unittest.main()