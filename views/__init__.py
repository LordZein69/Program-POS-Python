"""
Package views — semua halaman GUI untuk sistem POS.

Menerapkan:
- Abstract Base Class (BaseView) sebagai interface view
- Inheritance pada setiap halaman
- Polymorphism melalui override method build()
"""

from views.base_view import BaseView
from views.login_view import LoginView
from views.produk_view import ProdukView
from views.kasir_view import KasirView
from views.riwayat_view import RiwayatView

__all__ = ["BaseView", "LoginView", "ProdukView", "KasirView", "RiwayatView"]
