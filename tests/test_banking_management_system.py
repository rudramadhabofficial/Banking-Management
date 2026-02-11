import json
import tempfile
import unittest

from banking_management_system import BankingManagementSystem


class TestBankingManagementSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.system = BankingManagementSystem()
        self.savings = self.system.create_account("Alice", "savings", 1000)
        self.current = self.system.create_account("Bob", "current", 500)

    def test_deposit_withdraw_and_transfer(self):
        self.system.deposit(self.savings.account_id, 200)
        self.system.withdraw(self.current.account_id, 100)
        self.system.transfer(self.savings.account_id, self.current.account_id, 150)

        self.assertAlmostEqual(self.savings.balance, 1050)
        self.assertAlmostEqual(self.current.balance, 550)

    def test_interest_only_applies_to_savings(self):
        self.system.apply_monthly_interest(12)

        self.assertAlmostEqual(self.savings.balance, 1010)
        self.assertAlmostEqual(self.current.balance, 500)

    def test_summary(self):
        self.system.deposit(self.savings.account_id, 100)
        summary = self.system.summary()

        self.assertEqual(summary["total_accounts"], 2)
        self.assertEqual(summary["active_accounts"], 2)
        self.assertAlmostEqual(summary["total_holdings"], 1600)

    def test_export_snapshot(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as temp:
            self.system.export_snapshot(temp.name)
            temp.seek(0)
            payload = json.load(temp)

        self.assertIn("summary", payload)
        self.assertIn("accounts", payload)
        self.assertEqual(len(payload["accounts"]), 2)


if __name__ == "__main__":
    unittest.main()
