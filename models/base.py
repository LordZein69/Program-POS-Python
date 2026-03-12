"""
Module base — Abstract Base Class untuk semua model data.

Menerapkan:
- ABC (Abstract Base Class) sebagai interface/kontrak
- Property dengan getter/setter
- Method abstract yang wajib di-override (polymorphism)
- Overloading operator (__str__, __repr__, __eq__)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """Abstract base class yang menjadi interface untuk semua model.

    Setiap model harus mengimplementasikan:
    - to_dict() — konversi ke dictionary
    - from_row() — class method untuk membuat instance dari tuple database
    - validate() — validasi data sebelum disimpan

    Attributes:
        _id: ID unik dari record (private, diakses via property).
    """

    def __init__(self, id_record: int = 0) -> None:
        """Inisialisasi BaseModel.

        Args:
            id_record: ID unik record, default 0 untuk record baru.
        """
        self._id: int = id_record

    # ── Property (getter/setter) ──────────────────────────
    @property
    def id(self) -> int:
        """Getter untuk ID record."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Setter untuk ID record dengan validasi tipe data.

        Args:
            value: Nilai ID baru (harus integer >= 0).

        Raises:
            ValueError: Jika value bukan integer atau negatif.
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError("ID harus berupa integer non-negatif.")
        self._id = value

    # ── Abstract methods (interface contract) ─────────────
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Konversi model ke dictionary. Wajib di-override oleh subclass."""
        ...

    @classmethod
    @abstractmethod
    def from_row(cls, row: tuple) -> "BaseModel":
        """Buat instance dari tuple hasil query database.

        Args:
            row: Tuple dari database cursor.

        Returns:
            Instance dari subclass.
        """
        ...

    @abstractmethod
    def validate(self) -> bool:
        """Validasi data model. Return True jika valid.

        Returns:
            True jika data valid, False jika tidak.
        """
        ...

    # ── Overloading ───────────────────────────────────────
    def __str__(self) -> str:
        """String representation yang user-friendly."""
        return f"{self.__class__.__name__}(id={self._id})"

    def __repr__(self) -> str:
        """String representation untuk debugging."""
        return f"<{self.__class__.__name__} id={self._id}>"

    def __eq__(self, other: object) -> bool:
        """Perbandingan dua model berdasarkan tipe dan ID."""
        if not isinstance(other, BaseModel):
            return NotImplemented
        return type(self) is type(other) and self._id == other._id
