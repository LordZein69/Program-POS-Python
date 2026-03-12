import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pos_inventory.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id_produk INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_produk TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_transaksi INTEGER NOT NULL,
            id_produk INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi),
            FOREIGN KEY (id_produk) REFERENCES produk(id_produk)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pengguna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'kasir'))
        )
    """)

    # Insert default users if table is empty
    cursor.execute("SELECT COUNT(*) FROM pengguna")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO pengguna (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin"),
        )
        cursor.execute(
            "INSERT INTO pengguna (username, password, role) VALUES (?, ?, ?)",
            ("kasir", "kasir123", "kasir"),
        )

    conn.commit()
    conn.close()


# ─── Pengguna ─────────────────────────────────────────────
def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, role FROM pengguna WHERE username = ? AND password = ?",
        (username, password),
    )
    user = cursor.fetchone()
    conn.close()
    return user  # (username, role) or None


# ─── Produk ───────────────────────────────────────────────
def get_all_produk():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk, nama_produk, harga, stok FROM produk ORDER BY id_produk")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_produk_by_id(id_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_produk, nama_produk, harga, stok FROM produk WHERE id_produk = ?",
        (id_produk,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def search_produk(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_produk, nama_produk, harga, stok FROM produk WHERE nama_produk LIKE ? ORDER BY id_produk",
        (f"%{keyword}%",),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def tambah_produk(nama, harga, stok):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produk (nama_produk, harga, stok) VALUES (?, ?, ?)",
        (nama, harga, stok),
    )
    conn.commit()
    conn.close()


def edit_produk(id_produk, nama, harga, stok):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produk SET nama_produk = ?, harga = ?, stok = ? WHERE id_produk = ?",
        (nama, harga, stok, id_produk),
    )
    conn.commit()
    conn.close()


def hapus_produk(id_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id_produk = ?", (id_produk,))
    conn.commit()
    conn.close()


# ─── Transaksi ────────────────────────────────────────────
def simpan_transaksi(items):
    """
    items: list of dict {id_produk, nama_produk, harga, qty, subtotal}
    Returns id_transaksi on success.
    """
    conn = get_connection()
    cursor = conn.cursor()
    total = sum(item["subtotal"] for item in items)
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO transaksi (tanggal, total) VALUES (?, ?)",
        (tanggal, total),
    )
    id_transaksi = cursor.lastrowid

    for item in items:
        cursor.execute(
            "INSERT INTO detail_transaksi (id_transaksi, id_produk, qty, subtotal) VALUES (?, ?, ?, ?)",
            (id_transaksi, item["id_produk"], item["qty"], item["subtotal"]),
        )
        # Kurangi stok
        cursor.execute(
            "UPDATE produk SET stok = stok - ? WHERE id_produk = ?",
            (item["qty"], item["id_produk"]),
        )

    conn.commit()
    conn.close()
    return id_transaksi


def get_all_transaksi():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_transaksi, tanggal, total FROM transaksi ORDER BY id_transaksi DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_detail_transaksi(id_transaksi):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d.id, p.nama_produk, d.qty, p.harga, d.subtotal
        FROM detail_transaksi d
        JOIN produk p ON d.id_produk = p.id_produk
        WHERE d.id_transaksi = ?
        ORDER BY d.id
        """,
        (id_transaksi,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
