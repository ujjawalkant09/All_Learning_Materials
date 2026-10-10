"""Create ``inventory.db`` with random demo data for the SQL agent notebook.

Usage (from this folder)::

    python seed_inventory_db.py            # adds 500 rows
    python seed_inventory_db.py --reset    # deletes the old file first

The table it creates::

    inventory(id, product_name, category, sku, quantity, price,
              supplier, warehouse, created_at)
"""

import random
import sqlite3
import string
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_NAME = Path(__file__).with_name("inventory.db")
NUMBER_OF_RECORDS = 500

PRODUCTS = [
    "Laptop", "Keyboard", "Mouse", "Monitor", "Printer",
    "Router", "SSD", "Hard Drive", "RAM", "USB Drive",
    "Chair", "Desk", "Camera", "Microphone", "Speaker",
    "Headphone", "Projector", "Tablet", "Phone", "Scanner",
]
CATEGORIES = ["Electronics", "Computer Accessories", "Office", "Networking", "Furniture"]
SUPPLIERS = ["TechWorld", "ABC Electronics", "Global Supplies", "Prime Distributors", "Innovate Ltd", "SupplyHub"]
WAREHOUSES = ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Pune", "Kolkata"]


def random_sku() -> str:
    """Return a unique-looking stock keeping unit such as ``SKU-AB12CD34``."""
    return "SKU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def random_date() -> datetime:
    """Return a random timestamp within the last year."""
    return datetime.now() - timedelta(days=random.randint(0, 365))


def random_record() -> tuple:
    """Build one inventory row (without the auto-increment id)."""
    return (
        random.choice(PRODUCTS),
        random.choice(CATEGORIES),
        random_sku(),
        random.randint(0, 1000),
        round(random.uniform(50, 100000), 2),
        random.choice(SUPPLIERS),
        random.choice(WAREHOUSES),
        random_date().strftime("%Y-%m-%d %H:%M:%S"),
    )


def main() -> None:
    """Create the table (if needed) and insert NUMBER_OF_RECORDS random rows."""
    if "--reset" in sys.argv:
        DB_NAME.unlink(missing_ok=True)

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                supplier TEXT NOT NULL,
                warehouse TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO inventory (product_name, category, sku, quantity, price, supplier, warehouse, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [random_record() for _ in range(NUMBER_OF_RECORDS)],
        )
        total = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]

    print(f"Inserted {NUMBER_OF_RECORDS} rows. Total rows: {total}")


if __name__ == "__main__":
    main()
