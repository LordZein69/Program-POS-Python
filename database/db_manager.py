"""
Module db_manager — Mengelola koneksi dan operasi database SQLite.

Menerapkan:
- Class dengan method-method (prosedur dan fungsi)
- Parameterized query (mencegah SQL injection)
- Penyimpanan dan pembacaan data dari media penyimpan
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple


class DatabaseManager:
    """Manager untuk semua operasi database SQLite.

    Attributes:
        _db_path: Path file database SQLite (private).
    """

    def __init__(self, db_path: str = "") -> None:
        """Inisialisasi DatabaseManager.

        Args:
            db_path: Path ke file database. Default di direktori project.
        """
        if db_path:
            self._db_path: str = db_path
        else:
            self._db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "pos_inventory.db",
            )

    # ── Property ──────────────────────────────────────────
    @property
    def db_path(self) -> str:
        """Getter path database."""
        return self._db_path

    # ── Koneksi ───────────────────────────────────────────
    def _get_connection(self) -> sqlite3.Connection:
        """Buat dan kembalikan koneksi database.

        Returns:
            sqlite3.Connection object.
        """
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ── Inisialisasi Tabel ────────────────────────────────
    def init_db(self) -> None:
        """Buat semua tabel jika belum ada dan insert data default.

        Tabel yang dibuat: produk, transaksi, detail_transaksi, pengguna.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Array berisi SQL statement pembuatan tabel
        create_statements: List[str] = [
            """CREATE TABLE IF NOT EXISTS produk (
                id_produk INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_produk TEXT NOT NULL,
                harga REAL NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS transaksi (
                id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                total REAL NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS detail_transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_transaksi INTEGER NOT NULL,
                id_produk INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi),
                FOREIGN KEY (id_produk) REFERENCES produk(id_produk)
            )""",
            """CREATE TABLE IF NOT EXISTS pengguna (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'kasir'))
            )""",
        ]

        # Pengulangan for — eksekusi setiap statement
        for sql in create_statements:
            cursor.execute(sql)

        # Insert default users jika tabel kosong (percabangan if)
        cursor.execute("SELECT COUNT(*) FROM pengguna")
        count = cursor.fetchone()[0]
        if count == 0:
            default_users: List[Tuple[str, str, str]] = [
                ("admin", "admin123", "admin"),
                ("kasir", "kasir123", "kasir"),
            ]
            for username, password, role in default_users:
                cursor.execute(
                    "INSERT INTO pengguna (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role),
                )

        conn.commit()
        conn.close()

    # ── Pengguna ──────────────────────────────────────────
    def authenticate(self, username: str, password: str) -> Optional[Tuple[str, str]]:
        """Autentikasi pengguna berdasarkan username dan password.

        Args:
            username: Username pengguna.
            password: Password pengguna.

        Returns:
            Tuple (username, role) jika berhasil, None jika gagal.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, role FROM pengguna WHERE username = ? AND password = ?",
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()
        return user

    # ── Produk — CRUD ─────────────────────────────────────
    def get_all_produk(self) -> List[Tuple]:
        """Ambil semua data produk dari database.

        Returns:
            List of tuples (id_produk, nama_produk, harga, stok).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_produk, nama_produk, harga, stok FROM produk ORDER BY id_produk"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_produk_by_id(self, id_produk: int) -> Optional[Tuple]:
        """Ambil data produk berdasarkan ID.

        Args:
            id_produk: ID produk yang dicari.

        Returns:
            Tuple data produk atau None jika tidak ditemukan.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_produk, nama_produk, harga, stok FROM produk WHERE id_produk = ?",
            (id_produk,),
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def search_produk(self, keyword: str) -> List[Tuple]:
        """Cari produk berdasarkan nama (LIKE search).

        Args:
            keyword: Kata kunci pencarian.

        Returns:
            List of tuples hasil pencarian.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_produk, nama_produk, harga, stok FROM produk "
            "WHERE nama_produk LIKE ? ORDER BY id_produk",
            (f"%{keyword}%",),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def tambah_produk(self, nama: str, harga: float, stok: int) -> None:
        """Tambah produk baru ke database.

        Args:
            nama: Nama produk.
            harga: Harga produk.
            stok: Jumlah stok awal.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produk (nama_produk, harga, stok) VALUES (?, ?, ?)",
            (nama, harga, stok),
        )
        conn.commit()
        conn.close()

    def edit_produk(self, id_produk: int, nama: str, harga: float, stok: int) -> None:
        """Update data produk yang sudah ada.

        Args:
            id_produk: ID produk.
            nama: Nama baru.
            harga: Harga baru.
            stok: Stok baru.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produk SET nama_produk = ?, harga = ?, stok = ? WHERE id_produk = ?",
            (nama, harga, stok, id_produk),
        )
        conn.commit()
        conn.close()

    def hapus_produk(self, id_produk: int) -> None:
        """Hapus produk dari database.

        Args:
            id_produk: ID produk yang akan dihapus.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produk WHERE id_produk = ?", (id_produk,))
        conn.commit()
        conn.close()

    # ── Transaksi ─────────────────────────────────────────
    def simpan_transaksi(self, items: List[dict]) -> int:
        """Simpan transaksi beserta detail item ke database.

        Mengurangi stok produk secara otomatis.

        Args:
            items: Array (list) of dict berisi data item transaksi.
                   Setiap dict: {id_produk, nama_produk, harga, qty, subtotal}.

        Returns:
            ID transaksi yang baru dibuat.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Hitung total dari array items (pengulangan)
        total: float = sum(item["subtotal"] for item in items)
        tanggal: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO transaksi (tanggal, total) VALUES (?, ?)",
            (tanggal, total),
        )
        id_transaksi: int = cursor.lastrowid

        # Loop array items — simpan setiap detail dan kurangi stok
        for item in items:
            cursor.execute(
                "INSERT INTO detail_transaksi (id_transaksi, id_produk, qty, subtotal) "
                "VALUES (?, ?, ?, ?)",
                (id_transaksi, item["id_produk"], item["qty"], item["subtotal"]),
            )
            cursor.execute(
                "UPDATE produk SET stok = stok - ? WHERE id_produk = ?",
                (item["qty"], item["id_produk"]),
            )

        conn.commit()
        conn.close()
        return id_transaksi

    def get_all_transaksi(self) -> List[Tuple]:
        """Ambil semua data transaksi.

        Returns:
            List of tuples (id_transaksi, tanggal, total) terurut DESC.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_transaksi, tanggal, total FROM transaksi ORDER BY id_transaksi DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_detail_transaksi(self, id_transaksi: int) -> List[Tuple]:
        """Ambil detail item dari sebuah transaksi.

        Args:
            id_transaksi: ID transaksi.

        Returns:
            List of tuples (id, nama_produk, qty, harga, subtotal).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT d.id, p.nama_produk, d.qty, p.harga, d.subtotal
               FROM detail_transaksi d
               JOIN produk p ON d.id_produk = p.id_produk
               WHERE d.id_transaksi = ?
               ORDER BY d.id""",
            (id_transaksi,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
