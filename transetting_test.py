import transettings
import ruleset
import propset
import unittest


class Test_TranSettings(unittest.TestCase):
    def test_random_region(self):
        region1 = transettings.random_region()
        region2 = transettings.random_region()
        print(f"{region1} vs {region2}")
        self.assertNotEqual(region1, region2)


TRANS_TICKET_NUM = 10


class Test_TransGenerator(unittest.TestCase):
    def test_gen(self):
        tg = transettings.TransGenerator()
        arr = tg.generate_settings(TRANS_TICKET_NUM)
        self.assertEqual(len(arr), TRANS_TICKET_NUM)

    def test_check(self):
        tg = transettings.TransGenerator()
        arr = tg.generate_settings(TRANS_TICKET_NUM)

        resarr = []
        checker = ruleset.RuleChecker()
        for ts in arr:
            tp = propset.TransProps(ts)
            res = checker.judge(tp)
            resarr.append(res)
        self.assertEqual(len(resarr), TRANS_TICKET_NUM)

    def test_check_hardcode(self):
        a_trans = transettings.create_setting(
            "user2",
            "user3",
            "user4",
            "Personal Data",
            "GB",
            "100",
            "Germany",
            "China",
            "Customer data analysis",
        )

        checker = ruleset.RuleChecker()
        tp = propset.TransProps(a_trans)
        res = checker.judge(tp)

        self.assertEqual(res, ruleset.Decision.TBD)


if __name__ == "__main__":
    unittest.main()
