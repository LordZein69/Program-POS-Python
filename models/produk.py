"""
Module produk — Model data untuk produk/barang.

Menerapkan inheritance dari BaseModel, polymorphism (override method),
dan property dengan validasi.
"""

from typing import Any, Dict
from models.base import BaseModel


class Produk(BaseModel):
    """Model data produk yang dijual di toko.

    Inherits:
        BaseModel — abstract base class.

    Attributes:
        _nama: Nama produk (private).
        _harga: Harga satuan produk (private).
        _stok: Jumlah stok tersedia (private).
    """

    def __init__(
        self,
        id_produk: int = 0,
        nama: str = "",
        harga: float = 0.0,
        stok: int = 0,
    ) -> None:
        """Inisialisasi Produk.

        Args:
            id_produk: ID unik produk.
            nama: Nama produk.
            harga: Harga satuan (>= 0).
            stok: Jumlah stok (>= 0).
        """
        super().__init__(id_produk)
        self._nama: str = nama
        self._harga: float = harga
        self._stok: int = stok

    # ── Properties ────────────────────────────────────────
    @property
    def nama(self) -> str:
        """Getter untuk nama produk."""
        return self._nama

    @nama.setter
    def nama(self, value: str) -> None:
        """Setter nama produk.

        Args:
            value: Nama produk baru (tidak boleh kosong).

        Raises:
            ValueError: Jika nama kosong.
        """
        if not value or not value.strip():
            raise ValueError("Nama produk tidak boleh kosong.")
        self._nama = value.strip()

    @property
    def harga(self) -> float:
        """Getter untuk harga produk."""
        return self._harga

    @harga.setter
    def harga(self, value: float) -> None:
        """Setter harga produk.

        Args:
            value: Harga baru (>= 0).

        Raises:
            ValueError: Jika harga negatif.
        """
        if value < 0:
            raise ValueError("Harga tidak boleh negatif.")
        self._harga = float(value)

    @property
    def stok(self) -> int:
        """Getter untuk stok produk."""
        return self._stok

    @stok.setter
    def stok(self, value: int) -> None:
        """Setter stok produk.

        Args:
            value: Stok baru (>= 0).

        Raises:
            ValueError: Jika stok negatif.
        """
        if value < 0:
            raise ValueError("Stok tidak boleh negatif.")
        self._stok = int(value)

    # ── Polymorphism: override abstract methods ───────────
    def to_dict(self) -> Dict[str, Any]:
        """Konversi produk ke dictionary.

        Returns:
            Dictionary berisi data produk.
        """
        return {
            "id_produk": self._id,
            "nama_produk": self._nama,
            "harga": self._harga,
            "stok": self._stok,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Produk":
        """Buat instance Produk dari tuple database.

        Args:
            row: Tuple (id_produk, nama_produk, harga, stok).

        Returns:
            Instance Produk.
        """
        return cls(id_produk=row[0], nama=row[1], harga=row[2], stok=row[3])

    def validate(self) -> bool:
        """Validasi data produk.

        Returns:
            True jika nama tidak kosong, harga >= 0, stok >= 0.
        """
        if not self._nama or not self._nama.strip():
            return False
        if self._harga < 0:
            return False
        if self._stok < 0:
            return False
        return True

    # ── Overloading ───────────────────────────────────────
    def __str__(self) -> str:
        """Representasi produk yang user-friendly."""
        return f"{self._nama} — Rp {self._harga:,.0f} (stok: {self._stok})"

    def __repr__(self) -> str:
        """Representasi produk untuk debugging."""
        return (
            f"<Produk id={self._id} nama='{self._nama}' "
            f"harga={self._harga} stok={self._stok}>"
        )

    def to_array(self) -> list:
        """Konversi ke array/list untuk ditampilkan di tabel.

        Returns:
            List [id, nama, harga_formatted, stok].
        """
        return [self._id, self._nama, f"{self._harga:,.0f}", self._stok]
