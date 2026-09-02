import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "olist"
DATABASE_PATH = BASE_DIR / "data" / "rag.db"


DATASETS = {
    "olist_customers_dataset.csv": "olist_customers",
    "olist_geolocation_dataset.csv": "olist_geolocation",
    "olist_order_items_dataset.csv": "olist_order_items",
    "olist_order_payments_dataset.csv": "olist_order_payments",
    "olist_order_reviews_dataset.csv": "olist_order_reviews",
    "olist_orders_dataset.csv": "olist_orders",
    "olist_products_dataset.csv": "olist_products",
    "olist_sellers_dataset.csv": "olist_sellers",
    "product_category_name_translation.csv": "olist_category_translation",
}


def load_dataset(connection, filename, table_name):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    print(f"\nLoading {filename} -> {table_name}")

    first_chunk = True
    total_rows = 0

    for chunk in pd.read_csv(
        file_path,
        chunksize=10000
    ):
        chunk.to_sql(
            table_name,
            connection,
            if_exists="replace" if first_chunk else "append",
            index=False
        )

        total_rows += len(chunk)
        first_chunk = False

    print(f"Loaded {total_rows:,} rows")


def create_indexes(connection):
    print("\nCreating indexes...")

    indexes = [
        """
        CREATE INDEX IF NOT EXISTS idx_olist_orders_customer
        ON olist_orders(customer_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_order_items_order
        ON olist_order_items(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_order_items_product
        ON olist_order_items(product_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_order_items_seller
        ON olist_order_items(seller_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_order_payments_order
        ON olist_order_payments(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_order_reviews_order
        ON olist_order_reviews(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_products_category
        ON olist_products(product_category_name)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_olist_customers_unique
        ON olist_customers(customer_unique_id)
        """,
    ]

    for statement in indexes:
        connection.execute(statement)

    connection.commit()

    print("Indexes created")


def verify_database(connection):
    print("\nDatabase verification")
    print("=" * 60)

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name LIKE 'olist_%'
        ORDER BY name
        """
    ).fetchall()

    for (table_name,) in tables:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(f"{table_name:<35} {count:>10,} rows")


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Olist data directory not found: {DATA_DIR}"
        )

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        for filename, table_name in DATASETS.items():
            load_dataset(
                connection,
                filename,
                table_name
            )

        create_indexes(connection)
        verify_database(connection)

    finally:
        connection.close()

    print("\nOlist data loading completed successfully.")


if __name__ == "__main__":
    main()