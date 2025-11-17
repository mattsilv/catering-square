"""
Purpose: SQLite database utilities for tracking Square catalog IDs across environments
Related: catalog_utils.py, create_catalog_safe.py
Refactor if: >500 lines OR handling unrelated database operations

This is the SINGLE SOURCE OF TRUTH for Square catalog ID tracking
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

# Get project root and set data paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / 'data' / 'square_catalog.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize SQLite database with schema"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()

        # Locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,  -- 'sandbox' or 'production'
                square_id TEXT NOT NULL,
                name TEXT NOT NULL,
                store_number TEXT,
                address TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(environment, square_id)
            )
        ''')

        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,
                square_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(environment, square_id),
                UNIQUE(environment, name)
            )
        ''')

        # Images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,
                square_id TEXT NOT NULL,
                source_url TEXT,
                local_path TEXT,
                downloaded_at TIMESTAMP,
                uploaded_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(environment, square_id)
            )
        ''')

        # Menu items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,
                square_id TEXT NOT NULL,
                name TEXT NOT NULL,
                category_id INTEGER,
                description TEXT,
                price_cents INTEGER,
                image_id INTEGER,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(environment, square_id),
                UNIQUE(environment, name),
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (image_id) REFERENCES images(id)
            )
        ''')

        # Item variations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_variations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,
                square_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price_cents INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(environment, square_id),
                FOREIGN KEY (item_id) REFERENCES menu_items(id)
            )
        ''')

        # Sync log table - track all operations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                environment TEXT NOT NULL,
                operation TEXT NOT NULL,  -- 'create', 'update', 'delete'
                object_type TEXT NOT NULL,  -- 'location', 'category', 'item', 'image'
                square_id TEXT,
                status TEXT NOT NULL,  -- 'success', 'error'
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print(f"✅ Database initialized: {DB_PATH}")
    finally:
        conn.close()


def save_location(environment, square_id, name, store_number=None, address=None, phone=None):
    """Save or update location in database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO locations (environment, square_id, name, store_number, address, phone)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(environment, square_id)
            DO UPDATE SET
                name=excluded.name,
                store_number=excluded.store_number,
                address=excluded.address,
                phone=excluded.phone,
                updated_at=CURRENT_TIMESTAMP
        ''', (environment, square_id, name, store_number, address, phone))

        # Log within same transaction
        cursor.execute('''
            INSERT INTO sync_log (environment, operation, object_type, square_id, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (environment, 'create', 'location', square_id, 'success', None))


def save_category(environment, square_id, name, description=None):
    """Save or update category in database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (environment, square_id, name, description)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(environment, square_id)
            DO UPDATE SET
                name=excluded.name,
                description=excluded.description,
                updated_at=CURRENT_TIMESTAMP
        ''', (environment, square_id, name, description))

        cursor.execute('''
            INSERT INTO sync_log (environment, operation, object_type, square_id, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (environment, 'create', 'category', square_id, 'success', None))

        return cursor.lastrowid


def save_image(environment, square_id, source_url=None, local_path=None):
    """Save image metadata in database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO images (environment, square_id, source_url, local_path)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(environment, square_id)
            DO UPDATE SET
                source_url=excluded.source_url,
                local_path=excluded.local_path
        ''', (environment, square_id, source_url, local_path))

        cursor.execute('''
            INSERT INTO sync_log (environment, operation, object_type, square_id, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (environment, 'create', 'image', square_id, 'success', None))

        return cursor.lastrowid


def save_menu_item(environment, square_id, name, category_square_id, description=None,
                   price_cents=None, image_square_id=None, source_url=None):
    """Save or update menu item in database"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get category internal ID
        category_id = None
        if category_square_id:
            cursor.execute(
                'SELECT id FROM categories WHERE environment=? AND square_id=?',
                (environment, category_square_id)
            )
            row = cursor.fetchone()
            if row:
                category_id = row['id']

        # Get image internal ID
        image_id = None
        if image_square_id:
            cursor.execute(
                'SELECT id FROM images WHERE environment=? AND square_id=?',
                (environment, image_square_id)
            )
            row = cursor.fetchone()
            if row:
                image_id = row['id']

        cursor.execute('''
            INSERT INTO menu_items
                (environment, square_id, name, category_id, description, price_cents, image_id, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(environment, square_id)
            DO UPDATE SET
                name=excluded.name,
                category_id=excluded.category_id,
                description=excluded.description,
                price_cents=excluded.price_cents,
                image_id=excluded.image_id,
                source_url=excluded.source_url,
                updated_at=CURRENT_TIMESTAMP
        ''', (environment, square_id, name, category_id, description, price_cents, image_id, source_url))

        cursor.execute('''
            INSERT INTO sync_log (environment, operation, object_type, square_id, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (environment, 'create', 'menu_item', square_id, 'success', None))


def get_category_by_name(environment, name):
    """Get category Square ID by name"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT square_id FROM categories WHERE environment=? AND name=?',
            (environment, name)
        )
        row = cursor.fetchone()
        return row['square_id'] if row else None


def get_item_by_name(environment, name):
    """Get menu item Square ID by name"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT square_id FROM menu_items WHERE environment=? AND name=?',
            (environment, name)
        )
        row = cursor.fetchone()
        return row['square_id'] if row else None


def log_sync(environment, operation, object_type, square_id, status, error_message=None):
    """Log sync operation"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sync_log (environment, operation, object_type, square_id, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (environment, operation, object_type, square_id, status, error_message))


def get_all_categories(environment):
    """Get all categories for an environment"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, square_id FROM categories WHERE environment=? ORDER BY name',
            (environment,)
        )
        return {row['name']: row['square_id'] for row in cursor.fetchall()}


def get_all_items(environment):
    """Get all menu items for an environment"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, square_id FROM menu_items WHERE environment=? ORDER BY name',
            (environment,)
        )
        return {row['name']: row['square_id'] for row in cursor.fetchall()}


def export_to_json(environment, output_dir=None):
    """Export database to JSON files (for backward compatibility)"""
    import json

    if output_dir is None:
        output_dir = PROJECT_ROOT / 'data'

    categories = get_all_categories(environment)
    items = get_all_items(environment)

    with open(f'{output_dir}/category_ids.json', 'w') as f:
        json.dump(categories, f, indent=2)

    with open(f'{output_dir}/menu_item_ids.json', 'w') as f:
        json.dump(items, f, indent=2)

    print(f"✅ Exported to JSON: {len(categories)} categories, {len(items)} items")


def show_summary(environment=None):
    """Show database summary"""
    with get_db() as conn:
        cursor = conn.cursor()

        if environment:
            print(f"\n📊 Database Summary - {environment.upper()}")
            print("=" * 60)

            cursor.execute('SELECT COUNT(*) as count FROM locations WHERE environment=?', (environment,))
            print(f"Locations: {cursor.fetchone()['count']}")

            cursor.execute('SELECT COUNT(*) as count FROM categories WHERE environment=?', (environment,))
            print(f"Categories: {cursor.fetchone()['count']}")

            cursor.execute('SELECT COUNT(*) as count FROM menu_items WHERE environment=?', (environment,))
            print(f"Menu Items: {cursor.fetchone()['count']}")

            cursor.execute('SELECT COUNT(*) as count FROM images WHERE environment=?', (environment,))
            print(f"Images: {cursor.fetchone()['count']}")
        else:
            print("\n📊 Database Summary - ALL ENVIRONMENTS")
            print("=" * 60)

            for env in ['sandbox', 'production']:
                cursor.execute('SELECT COUNT(*) as count FROM categories WHERE environment=?', (env,))
                cat_count = cursor.fetchone()['count']

                cursor.execute('SELECT COUNT(*) as count FROM menu_items WHERE environment=?', (env,))
                item_count = cursor.fetchone()['count']

                print(f"{env.capitalize()}: {cat_count} categories, {item_count} items")


if __name__ == "__main__":
    init_database()
    show_summary()
