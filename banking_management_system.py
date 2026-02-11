from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
import json
import uuid


@dataclass
class Transaction:
    timestamp: str
    transaction_type: str
    amount: float
    description: str
    balance_after: float


@dataclass
class Account:
    owner_name: str
    account_type: str
    opening_balance: float = 0.0
    account_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    is_active: bool = True
    _balance: float = field(init=False, repr=False)
    _transactions: List[Transaction] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.opening_balance < 0:
            raise ValueError("Opening balance cannot be negative")

        self._balance = float(self.opening_balance)
        if self.opening_balance > 0:
            self._record("OPEN", self.opening_balance, "Opening deposit")

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def _record(self, transaction_type: str, amount: float, description: str) -> None:
        self._transactions.append(
            Transaction(
                timestamp=datetime.utcnow().isoformat(timespec="seconds"),
                transaction_type=transaction_type,
                amount=round(amount, 2),
                description=description,
                balance_after=round(self._balance, 2),
            )
        )

    def deposit(self, amount: float, description: str = "Cash deposit") -> None:
        if not self.is_active:
            raise ValueError("Cannot deposit to an inactive account")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._record("DEPOSIT", amount, description)

    def withdraw(self, amount: float, description: str = "Cash withdrawal") -> None:
        if not self.is_active:
            raise ValueError("Cannot withdraw from an inactive account")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")

        self._balance -= amount
        self._record("WITHDRAW", amount, description)

    def close(self) -> None:
        if self._balance != 0:
            raise ValueError("Account can only be closed when balance is zero")

        self.is_active = False
        self._record("CLOSE", 0, "Account closed")


class BankingManagementSystem:
    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}

    def create_account(self, owner_name: str, account_type: str, opening_balance: float = 0.0) -> Account:
        if not owner_name.strip():
            raise ValueError("Owner name is required")
        if account_type.lower() not in {"savings", "current"}:
            raise ValueError("Account type must be 'savings' or 'current'")

        account = Account(owner_name=owner_name.strip(), account_type=account_type.lower(), opening_balance=opening_balance)
        self._accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> Account:
        account = self._accounts.get(account_id)
        if not account:
            raise KeyError(f"Account '{account_id}' not found")
        return account

    def deposit(self, account_id: str, amount: float) -> None:
        self.get_account(account_id).deposit(amount)

    def withdraw(self, account_id: str, amount: float) -> None:
        self.get_account(account_id).withdraw(amount)

    def transfer(self, source_account_id: str, target_account_id: str, amount: float) -> None:
        if source_account_id == target_account_id:
            raise ValueError("Cannot transfer to the same account")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        source = self.get_account(source_account_id)
        target = self.get_account(target_account_id)

        source.withdraw(amount, description=f"Transfer to {target.account_id}")
        target.deposit(amount, description=f"Transfer from {source.account_id}")

    def apply_monthly_interest(self, annual_rate_percent: float) -> None:
        if annual_rate_percent < 0:
            raise ValueError("Annual interest rate cannot be negative")

        monthly_rate = annual_rate_percent / 100 / 12
        for account in self._accounts.values():
            if account.is_active and account.account_type == "savings" and account.balance > 0:
                interest = account.balance * monthly_rate
                if interest > 0:
                    account.deposit(interest, description="Monthly interest")

    def summary(self) -> dict:
        active_accounts = [acc for acc in self._accounts.values() if acc.is_active]
        return {
            "total_accounts": len(self._accounts),
            "active_accounts": len(active_accounts),
            "total_holdings": round(sum(acc.balance for acc in active_accounts), 2),
        }

    def export_snapshot(self, file_path: str) -> None:
        payload = {
            "summary": self.summary(),
            "accounts": [
                {
                    "account_id": acc.account_id,
                    "owner_name": acc.owner_name,
                    "account_type": acc.account_type,
                    "is_active": acc.is_active,
                    "balance": round(acc.balance, 2),
                    "transactions": [t.__dict__ for t in acc.transactions],
                }
                for acc in self._accounts.values()
            ],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


if __name__ == "__main__":
    bank = BankingManagementSystem()
    a1 = bank.create_account("Alice", "savings", 1000)
    a2 = bank.create_account("Bob", "current", 500)

    bank.deposit(a1.account_id, 200)
    bank.withdraw(a2.account_id, 100)
    bank.transfer(a1.account_id, a2.account_id, 150)
    bank.apply_monthly_interest(6)

    print("System summary:", bank.summary())
    bank.export_snapshot("bank_snapshot.json")
    print("Snapshot saved to bank_snapshot.json")
