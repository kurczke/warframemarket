#!/usr/bin/env python3
import argparse
import sqlite3
import time
from typing import Iterable

import requests

DEFAULT_API_BASE_URL = "https://api.warframe.market/v1"
DEFAULT_LANGUAGE = "en"


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Language": DEFAULT_LANGUAGE,
            "Platform": "pc",
            "User-Agent": "warframe-market-fetcher/1.0",
        }
    )
    return session


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            url_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            thumb TEXT,
            last_seen TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            order_type TEXT NOT NULL,
            platinum INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            user_status TEXT,
            mod_rank INTEGER,
            region TEXT,
            platform TEXT,
            created_at TEXT,
            last_update TEXT,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_orders_item_id ON orders(item_id)")
    connection.commit()


def request_json(session: requests.Session, url: str) -> dict:
    response = session.get(url, timeout=30)
    if response.status_code == 404:
        raise RuntimeError(
            "Otrzymano HTTP 404 z API Warframe Market. "
            "Sprawdź bazowy URL API i połączenie sieciowe."
        )
    response.raise_for_status()
    return response.json()


def fetch_items(session: requests.Session, api_base_url: str) -> list[dict]:
    payload = request_json(session, f"{api_base_url}/items")
    return payload["payload"]["items"]


def fetch_orders(
    session: requests.Session, api_base_url: str, item_url_name: str
) -> list[dict]:
    payload = request_json(session, f"{api_base_url}/items/{item_url_name}/orders")
    return payload["payload"]["orders"]


def save_items(connection: sqlite3.Connection, items: Iterable[dict]) -> None:
    connection.executemany(
        """
        INSERT INTO items (id, url_name, item_name, thumb, last_seen)
        VALUES (:id, :url_name, :item_name, :thumb, :last_seen)
        ON CONFLICT(id) DO UPDATE SET
            url_name=excluded.url_name,
            item_name=excluded.item_name,
            thumb=excluded.thumb,
            last_seen=excluded.last_seen
        """,
        items,
    )
    connection.commit()


def save_orders(
    connection: sqlite3.Connection, item_id: str, orders: Iterable[dict]
) -> None:
    rows = []
    for order in orders:
        user = order.get("user", {})
        rows.append(
            {
                "order_id": order["id"],
                "item_id": item_id,
                "order_type": order["order_type"],
                "platinum": order["platinum"],
                "quantity": order["quantity"],
                "user_id": user.get("id", "unknown"),
                "user_status": user.get("status"),
                "mod_rank": order.get("mod_rank"),
                "region": order.get("region"),
                "platform": order.get("platform"),
                "created_at": order.get("creation_date"),
                "last_update": order.get("last_update"),
            }
        )
    connection.executemany(
        """
        INSERT INTO orders (
            order_id,
            item_id,
            order_type,
            platinum,
            quantity,
            user_id,
            user_status,
            mod_rank,
            region,
            platform,
            created_at,
            last_update
        )
        VALUES (
            :order_id,
            :item_id,
            :order_type,
            :platinum,
            :quantity,
            :user_id,
            :user_status,
            :mod_rank,
            :region,
            :platform,
            :created_at,
            :last_update
        )
        ON CONFLICT(order_id) DO UPDATE SET
            item_id=excluded.item_id,
            order_type=excluded.order_type,
            platinum=excluded.platinum,
            quantity=excluded.quantity,
            user_id=excluded.user_id,
            user_status=excluded.user_status,
            mod_rank=excluded.mod_rank,
            region=excluded.region,
            platform=excluded.platform,
            created_at=excluded.created_at,
            last_update=excluded.last_update
        """,
        rows,
    )
    connection.commit()


def iter_items(items: list[dict], limit: int | None) -> Iterable[dict]:
    if limit is None:
        yield from items
        return
    for item in items[:limit]:
        yield item


def run_fetcher(
    database_path: str,
    limit: int | None,
    pause_seconds: float,
    api_base_url: str,
) -> None:
    session = build_session()
    items = fetch_items(session, api_base_url)
    connection = sqlite3.connect(database_path)
    try:
        ensure_schema(connection)
        save_items(connection, items)
        for item in iter_items(items, limit):
            orders = fetch_orders(session, api_base_url, item["url_name"])
            save_orders(connection, item["id"], orders)
            if pause_seconds:
                time.sleep(pause_seconds)
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pobiera listy przedmiotów i aukcje z Warframe Market."
    )
    parser.add_argument(
        "--db",
        dest="database_path",
        default="warframe_market.sqlite3",
        help="Ścieżka do pliku bazy danych SQLite.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Opcjonalny limit liczby przedmiotów do pobrania (ułatwia testy).",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.2,
        help="Pauza między kolejnymi zapytaniami do API (sekundy).",
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE_URL,
        help=(
            "Bazowy adres API (domyślnie https://api.warframe.market/v1). "
            "Użyj, jeśli Twoje środowisko wymaga innej ścieżki."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_fetcher(args.database_path, args.limit, args.pause, args.api_base)


if __name__ == "__main__":
    main()
