"""
Module transaksi — Model data untuk transaksi dan detail transaksi.

Menerapkan inheritance dari BaseModel, polymorphism, dan penggunaan array.
"""

from datetime import datetime
from typing import Any, Dict, List
from models.base import BaseModel


class DetailTransaksi(BaseModel):
    """Model data detail item dalam satu transaksi.

    Inherits:
        BaseModel — abstract base class.

    Attributes:
        _id_transaksi: FK ke transaksi induk.
        _id_produk: FK ke produk yang dibeli.
        _nama_produk: Nama produk (untuk display).
        _harga: Harga satuan saat transaksi.
        _qty: Jumlah item.
        _subtotal: Total harga item (harga * qty).
    """

    def __init__(
        self,
        id_detail: int = 0,
        id_transaksi: int = 0,
        id_produk: int = 0,
        nama_produk: str = "",
        harga: float = 0.0,
        qty: int = 0,
        subtotal: float = 0.0,
    ) -> None:
        """Inisialisasi DetailTransaksi.

        Args:
            id_detail: ID detail.
            id_transaksi: ID transaksi induk.
            id_produk: ID produk.
            nama_produk: Nama produk.
            harga: Harga satuan.
            qty: Jumlah item.
            subtotal: Total = harga * qty.
        """
        super().__init__(id_detail)
        self._id_transaksi: int = id_transaksi
        self._id_produk: int = id_produk
        self._nama_produk: str = nama_produk
        self._harga: float = harga
        self._qty: int = qty
        self._subtotal: float = subtotal

    # ── Properties ────────────────────────────────────────
    @property
    def id_transaksi(self) -> int:
        """Getter ID transaksi."""
        return self._id_transaksi

    @property
    def id_produk(self) -> int:
        """Getter ID produk."""
        return self._id_produk

    @property
    def nama_produk(self) -> str:
        """Getter nama produk."""
        return self._nama_produk

    @property
    def harga(self) -> float:
        """Getter harga satuan."""
        return self._harga

    @property
    def qty(self) -> int:
        """Getter quantity."""
        return self._qty

    @qty.setter
    def qty(self, value: int) -> None:
        """Setter qty dengan auto-update subtotal.

        Args:
            value: Jumlah item baru (> 0).

        Raises:
            ValueError: Jika qty <= 0.
        """
        if value <= 0:
            raise ValueError("Qty harus lebih dari 0.")
        self._qty = value
        self._subtotal = self._harga * self._qty

    @property
    def subtotal(self) -> float:
        """Getter subtotal."""
        return self._subtotal

    # ── Override abstract methods (polymorphism) ──────────
    def to_dict(self) -> Dict[str, Any]:
        """Konversi detail transaksi ke dictionary."""
        return {
            "id": self._id,
            "id_transaksi": self._id_transaksi,
            "id_produk": self._id_produk,
            "nama_produk": self._nama_produk,
            "harga": self._harga,
            "qty": self._qty,
            "subtotal": self._subtotal,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "DetailTransaksi":
        """Buat instance dari tuple database.

        Args:
            row: Tuple (id, nama_produk, qty, harga, subtotal).
        """
        return cls(
            id_detail=row[0],
            nama_produk=row[1],
            qty=row[2],
            harga=row[3],
            subtotal=row[4],
        )

    def validate(self) -> bool:
        """Validasi detail transaksi."""
        return self._qty > 0 and self._subtotal >= 0

    def __str__(self) -> str:
        return f"{self._nama_produk} x{self._qty} = Rp {self._subtotal:,.0f}"


class Transaksi(BaseModel):
    """Model data transaksi penjualan.

    Inherits:
        BaseModel — abstract base class.

    Attributes:
        _tanggal: Tanggal transaksi.
        _total: Total nominal transaksi.
        _items: Array (list) berisi DetailTransaksi.
    """

    def __init__(
        self,
        id_transaksi: int = 0,
        tanggal: str = "",
        total: float = 0.0,
        items: List[DetailTransaksi] | None = None,
    ) -> None:
        """Inisialisasi Transaksi.

        Args:
            id_transaksi: ID transaksi.
            tanggal: Tanggal transaksi (string ISO).
            total: Total nominal transaksi.
            items: Array/list berisi DetailTransaksi.
        """
        super().__init__(id_transaksi)
        self._tanggal: str = tanggal or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._total: float = total
        # Penggunaan array (list) untuk menyimpan item transaksi
        self._items: List[DetailTransaksi] = items if items is not None else []

    # ── Properties ────────────────────────────────────────
    @property
    def tanggal(self) -> str:
        """Getter tanggal."""
        return self._tanggal

    @property
    def total(self) -> float:
        """Getter total."""
        return self._total

    @property
    def items(self) -> List[DetailTransaksi]:
        """Getter array items."""
        return self._items

    # ── Methods ───────────────────────────────────────────
    def hitung_total(self) -> float:
        """Hitung ulang total dari semua item di array.

        Returns:
            Jumlah total semua subtotal item.
        """
        self._total = sum(item.subtotal for item in self._items)
        return self._total

    def tambah_item(self, item: DetailTransaksi) -> None:
        """Tambah item ke array keranjang.

        Args:
            item: DetailTransaksi yang akan ditambahkan.
        """
        # Loop array untuk cek duplikat (pengulangan for)
        for existing in self._items:
            if existing.id_produk == item.id_produk:
                existing.qty = existing.qty + item.qty
                self.hitung_total()
                return
        self._items.append(item)
        self.hitung_total()

    def hapus_item(self, index: int) -> None:
        """Hapus item dari array berdasarkan index.

        Args:
            index: Index item di array.
        """
        if 0 <= index < len(self._items):
            del self._items[index]
            self.hitung_total()

    # ── Override abstract methods (polymorphism) ──────────
    def to_dict(self) -> Dict[str, Any]:
        """Konversi transaksi ke dictionary termasuk array items."""
        return {
            "id_transaksi": self._id,
            "tanggal": self._tanggal,
            "total": self._total,
            "items": [item.to_dict() for item in self._items],
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Transaksi":
        """Buat instance dari tuple database.

        Args:
            row: Tuple (id_transaksi, tanggal, total).
        """
        return cls(id_transaksi=row[0], tanggal=row[1], total=row[2])

    def validate(self) -> bool:
        """Validasi transaksi: harus punya minimal 1 item."""
        return len(self._items) > 0 and self._total > 0

    def __str__(self) -> str:
        return f"Transaksi #{self._id} — {self._tanggal} — Rp {self._total:,.0f}"
