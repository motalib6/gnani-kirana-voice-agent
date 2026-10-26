"""Tiny SQLite order store for the shopkeeper dashboard."""
import json
import sqlite3
from datetime import datetime, timezone

from . import config


def _connect():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items_json TEXT,
            total REAL,
            status TEXT,
            created_at TEXT
        )"""
    )
    return conn


def save_order(customer_name, items, total, status="pending"):
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO orders (customer_name, items_json, total, status, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (customer_name, json.dumps(items), total, status,
         datetime.now(timezone.utc).isoformat()),
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def update_status(order_id, status):
    conn = _connect()
    cur = conn.execute(
        "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed


def list_orders():
    conn = _connect()
    rows = conn.execute(
        "SELECT id, customer_name, items_json, total, status, created_at"
        " FROM orders ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "customer_name": r[1], "items": json.loads(r[2]),
            "total": r[3], "status": r[4], "created_at": r[5],
        }
        for r in rows
    ]
