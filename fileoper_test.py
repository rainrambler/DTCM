import fileoper
import unittest


class Test_FileOper(unittest.TestCase):
    def test_check(self):
        full_path = r"/home/user1/aaa.json"
        signed = fileoper.get_signed_name(full_path)

        self.assertEqual(signed, r"/home/user1/aaa_signed.json")


if __name__ == "__main__":
    unittest.main()
