"""
Package database — modul akses data ke SQLite.

Menyediakan fungsi CRUD (Create, Read, Update, Delete) untuk
menyimpan dan membaca data di media penyimpan (database SQLite).
"""

from database.db_manager import DatabaseManager

__all__ = ["DatabaseManager"]
