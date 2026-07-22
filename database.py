from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).parent / "data" / "acme_audio.db"


def get_order(customer_id: str, order_id: str) -> dict | None:
    """Return an order when it belongs to the given customer."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        order = connection.execute(
            """
            SELECT id, status, ordered_at, estimated_delivery_date, total_cents
            FROM orders
            WHERE id = ? AND customer_id = ?
            """,
            (order_id, customer_id),
        ).fetchone()

    return dict(order) if order else None
