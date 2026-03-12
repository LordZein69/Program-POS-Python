"""
Module pengguna — Model data untuk pengguna sistem (admin/kasir).

Menerapkan inheritance dari BaseModel dan polymorphism.
"""

from typing import Any, Dict
from models.base import BaseModel


class Pengguna(BaseModel):
    """Model data pengguna sistem.

    Inherits:
        BaseModel — abstract base class.

    Attributes:
        _username: Username login (private).
        _password: Password login (private).
        _role: Role pengguna ('admin' atau 'kasir').
    """

    ROLES = ("admin", "kasir")

    def __init__(
        self,
        id_pengguna: int = 0,
        username: str = "",
        password: str = "",
        role: str = "kasir",
    ) -> None:
        """Inisialisasi Pengguna.

        Args:
            id_pengguna: ID pengguna.
            username: Username login.
            password: Password login.
            role: Role ('admin' atau 'kasir').
        """
        super().__init__(id_pengguna)
        self._username: str = username
        self._password: str = password
        self._role: str = role

    # ── Properties ────────────────────────────────────────
    @property
    def username(self) -> str:
        """Getter username."""
        return self._username

    @property
    def role(self) -> str:
        """Getter role."""
        return self._role

    @role.setter
    def role(self, value: str) -> None:
        """Setter role dengan validasi.

        Args:
            value: Role baru (harus 'admin' atau 'kasir').

        Raises:
            ValueError: Jika role tidak valid.
        """
        if value not in self.ROLES:
            raise ValueError(f"Role harus salah satu dari {self.ROLES}.")
        self._role = value

    def is_admin(self) -> bool:
        """Cek apakah pengguna adalah admin.

        Returns:
            True jika role == 'admin'.
        """
        return self._role == "admin"

    def is_kasir(self) -> bool:
        """Cek apakah pengguna adalah kasir.

        Returns:
            True jika role == 'kasir'.
        """
        return self._role == "kasir"

    # ── Override abstract methods (polymorphism) ──────────
    def to_dict(self) -> Dict[str, Any]:
        """Konversi pengguna ke dictionary (tanpa password)."""
        return {
            "id": self._id,
            "username": self._username,
            "role": self._role,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Pengguna":
        """Buat instance dari tuple database.

        Args:
            row: Tuple (username, role).
        """
        return cls(username=row[0], role=row[1])

    def validate(self) -> bool:
        """Validasi data pengguna."""
        if not self._username or not self._username.strip():
            return False
        if not self._password:
            return False
        if self._role not in self.ROLES:
            return False
        return True

    def __str__(self) -> str:
        return f"{self._username} ({self._role})"
