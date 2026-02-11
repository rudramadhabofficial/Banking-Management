# Advanced Banking Management System

A Python-based **advanced banking management system** with support for:

- Account creation (`savings` and `current`)
- Deposit and withdrawal operations
- Account-to-account transfers
- Monthly interest application for savings accounts
- Transaction history tracking per account
- System-level summary reporting
- JSON snapshot export

## Quick Start

```bash
python3 banking_management_system.py
```

This runs a small demo and creates `bank_snapshot.json`.

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Core API

Main class: `BankingManagementSystem`

Key methods:
- `create_account(owner_name, account_type, opening_balance=0.0)`
- `deposit(account_id, amount)`
- `withdraw(account_id, amount)`
- `transfer(source_account_id, target_account_id, amount)`
- `apply_monthly_interest(annual_rate_percent)`
- `summary()`
- `export_snapshot(file_path)`
