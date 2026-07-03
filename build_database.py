"""One-time script: creates banking.db and fills it with realistic fake data."""

import random
import sqlite3
from datetime import date, timedelta

from faker import Faker

DB_PATH = "banking.db"

N_BRANCHES = 15
N_CUSTOMERS = 1000
N_ACCOUNTS = 1500
N_TRANSACTIONS = 50000
N_LOANS = 400

REGIONS = ["North", "South", "East", "West", "Central"]
ACCOUNT_TYPES = ["savings", "current", "salary"]
INCOME_BRACKETS = ["low", "middle", "upper-middle", "high"]
TXN_TYPES = ["credit", "debit"]
TXN_CATEGORIES = [
    "groceries", "rent", "utilities", "salary", "entertainment",
    "healthcare", "travel", "shopping", "transfer", "dining",
]
LOAN_TYPES = ["home", "auto", "personal", "education", "business"]
LOAN_STATUSES = ["active", "closed", "default"]

fake = Faker()
random.seed(42)
Faker.seed(42)


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def build_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS loans;
        DROP TABLE IF EXISTS accounts;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS branches;

        CREATE TABLE branches (
            branch_id   INTEGER PRIMARY KEY,
            branch_name TEXT NOT NULL,
            city        TEXT NOT NULL,
            region      TEXT NOT NULL
        );

        CREATE TABLE customers (
            customer_id    INTEGER PRIMARY KEY,
            name           TEXT NOT NULL,
            age            INTEGER NOT NULL,
            gender         TEXT NOT NULL,
            city           TEXT NOT NULL,
            join_date      TEXT NOT NULL,
            income_bracket TEXT NOT NULL
        );

        CREATE TABLE accounts (
            account_id   INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
            account_type TEXT NOT NULL,
            balance      REAL NOT NULL,
            open_date    TEXT NOT NULL,
            branch_id    INTEGER NOT NULL REFERENCES branches(branch_id)
        );

        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id     INTEGER NOT NULL REFERENCES accounts(account_id),
            txn_date       TEXT NOT NULL,
            amount         REAL NOT NULL,
            txn_type       TEXT NOT NULL,
            category       TEXT NOT NULL
        );

        CREATE TABLE loans (
            loan_id          INTEGER PRIMARY KEY,
            customer_id      INTEGER NOT NULL REFERENCES customers(customer_id),
            loan_type        TEXT NOT NULL,
            principal_amount REAL NOT NULL,
            interest_rate    REAL NOT NULL,
            status           TEXT NOT NULL,
            disbursed_date   TEXT NOT NULL
        );

        CREATE INDEX idx_accounts_customer ON accounts(customer_id);
        CREATE INDEX idx_accounts_branch ON accounts(branch_id);
        CREATE INDEX idx_transactions_account ON transactions(account_id);
        CREATE INDEX idx_transactions_date ON transactions(txn_date);
        CREATE INDEX idx_loans_customer ON loans(customer_id);
        """
    )


def build_branches() -> list[tuple]:
    rows = []
    for branch_id in range(1, N_BRANCHES + 1):
        rows.append(
            (
                branch_id,
                f"{fake.city()} Branch",
                fake.city(),
                random.choice(REGIONS),
            )
        )
    return rows


def build_customers() -> list[tuple]:
    rows = []
    start, end = date(2015, 1, 1), date(2024, 12, 31)
    for customer_id in range(1, N_CUSTOMERS + 1):
        rows.append(
            (
                customer_id,
                fake.name(),
                random.randint(18, 75),
                random.choice(["male", "female"]),
                fake.city(),
                random_date(start, end).isoformat(),
                random.choice(INCOME_BRACKETS),
            )
        )
    return rows


def build_accounts() -> list[tuple]:
    rows = []
    start, end = date(2015, 1, 1), date(2025, 6, 30)
    for account_id in range(1, N_ACCOUNTS + 1):
        rows.append(
            (
                account_id,
                random.randint(1, N_CUSTOMERS),
                random.choice(ACCOUNT_TYPES),
                round(random.uniform(500, 500_000), 2),
                random_date(start, end).isoformat(),
                random.randint(1, N_BRANCHES),
            )
        )
    return rows


def build_transactions() -> list[tuple]:
    rows = []
    start, end = date(2023, 1, 1), date(2024, 12, 31)
    for txn_id in range(1, N_TRANSACTIONS + 1):
        txn_type = random.choice(TXN_TYPES)
        category = random.choice(TXN_CATEGORIES)
        amount = round(random.uniform(50, 20000), 2)
        rows.append(
            (
                txn_id,
                random.randint(1, N_ACCOUNTS),
                random_date(start, end).isoformat(),
                amount,
                txn_type,
                category,
            )
        )
    return rows


def build_loans() -> list[tuple]:
    rows = []
    start, end = date(2018, 1, 1), date(2024, 12, 31)
    for loan_id in range(1, N_LOANS + 1):
        rows.append(
            (
                loan_id,
                random.randint(1, N_CUSTOMERS),
                random.choice(LOAN_TYPES),
                round(random.uniform(50_000, 5_000_000), 2),
                round(random.uniform(6.5, 14.0), 2),
                random.choices(LOAN_STATUSES, weights=[0.6, 0.3, 0.1])[0],
                random_date(start, end).isoformat(),
            )
        )
    return rows


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    build_schema(conn)

    conn.executemany(
        "INSERT INTO branches VALUES (?, ?, ?, ?)", build_branches()
    )
    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)", build_customers()
    )
    conn.executemany(
        "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)", build_accounts()
    )
    conn.executemany(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)", build_transactions()
    )
    conn.executemany(
        "INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?)", build_loans()
    )

    conn.commit()

    counts = {}
    for table in ["branches", "customers", "accounts", "transactions", "loans"]:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()

    print(f"Created {DB_PATH} with:")
    for table, count in counts.items():
        print(f"  {table}: {count} rows")


if __name__ == "__main__":
    main()
