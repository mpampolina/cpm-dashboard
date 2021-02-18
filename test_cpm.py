import unittest
from cpm import Cpm
from test_utilities import *

class TestCalc(unittest.TestCase):
    def setUp(self):
        self.cpm1 = Cpm(testActivities1)
        self.cpm1.run()
        self.cpm1_1 = Cpm(testActivities1_1)
        self.cpm1_1.run()
        self.cpm2 = Cpm(testActivities2)
        self.cpm2.run()
        self.cpm3 = Cpm(testActivities3)
        self.cpm3.run()

    # Check for a discrepancy between the 
    # given reference list items (including nested dictionaries
    # or lists) and the the class generated  list items, irrespective
    # of order and number type
    def test_equalData(self):
        self.assertCountEqual(self.cpm1.activities, testResults1)
        self.assertCountEqual(self.cpm1_1.activities, testResults1_1)
        self.assertCountEqual(self.cpm2.activities, testResults2)
        self.assertCountEqual(self.cpm3.activities, testResults3)

if __name__ == "__main__":
    unittest.main()