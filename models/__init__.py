"""
Package models — berisi class-class model data untuk sistem POS.

Menerapkan:
- Abstract Base Class (ABC) sebagai interface
- Inheritance (pewarisan)
- Polymorphism (method overriding)
- Properties (getter/setter)
- Overloading (__str__, __repr__, __eq__)
"""

from models.base import BaseModel
from models.produk import Produk
from models.transaksi import Transaksi, DetailTransaksi
from models.pengguna import Pengguna

__all__ = ["BaseModel", "Produk", "Transaksi", "DetailTransaksi", "Pengguna"]
