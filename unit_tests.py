import unittest


def check_ratios(combined):
    i = 1
    while i < len(combined.get_scenario_names()):
        first = combined.casemodel.cases[0].area/combined.ie.posterior('aux')[{'aux':combined.get_scenario_names()[0]}]
        try:
            assert first == combined.casemodel.cases[i].area / combined.ie.posterior('aux')[{'aux':combined.get_scenario_names()[i]}]
        except AssertionError:
            print('ratio between case model and bn is wrong, D: ', first - combined.casemodel.cases[i].area / combined.ie.posterior('aux')[{'aux':combined.get_scenario_names()[i]}])
            print(first,combined.casemodel.cases[i].area / combined.ie.posterior('aux')[{'aux':combined.get_scenario_names()[i]}])
        i = i + 1


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
