"""
Module base_view — Abstract base class untuk semua view/halaman.

Menerapkan:
- ABC sebagai interface bagi semua halaman GUI
- Method abstract build() yang wajib di-override (polymorphism)
- Helper methods untuk Treeview styling
"""

from abc import ABC, abstractmethod
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Tuple, List

from utils.theme import ThemeManager


class BaseView(ABC):
    """Abstract base class sebagai interface untuk semua halaman.

    Setiap halaman wajib meng-override method build().

    Attributes:
        _parent: Container widget tempat view di-render.
        _theme: ThemeManager untuk palet warna.
        _app: Referensi ke objek App utama.
    """

    def __init__(self, parent: ctk.CTkFrame, theme: ThemeManager, app) -> None:
        """Inisialisasi BaseView.

        Args:
            parent: Frame container.
            theme: ThemeManager instance.
            app: Referensi ke kelas App utama.
        """
        self._parent: ctk.CTkFrame = parent
        self._theme: ThemeManager = theme
        self._app = app

    # ── Property ──────────────────────────────────────────
    @property
    def colors(self) -> dict:
        """Shortcut ke palet warna aktif."""
        return self._theme.colors

    @property
    def font(self) -> str:
        """Shortcut ke font family."""
        return self._theme.font_family

    # ── Abstract method — wajib di-override ───────────────
    @abstractmethod
    def build(self) -> None:
        """Bangun seluruh komponen UI halaman. Wajib diimplementasi."""
        ...

    # ── Helper: clear parent ──────────────────────────────
    def _clear(self) -> None:
        """Hapus semua widget dari parent container."""
        for widget in self._parent.winfo_children():
            widget.destroy()

    # ── Helper: configure treeview style ──────────────────
    def _configure_treeview_style(self, style_name: str) -> None:
        """Konfigurasi style untuk Treeview agar sesuai tema.

        Memperbaiki warna highlight agar kontras dengan background,
        dan menambahkan border antar kolom.

        Args:
            style_name: Nama style untuk Treeview (misal 'Produk.Treeview').
        """
        c = self.colors
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            f"{style_name}.Treeview",
            background=c["table_row"],
            foreground=c["text"],
            rowheight=38,
            fieldbackground=c["table_bg"],
            font=(self.font, 12),
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            f"{style_name}.Treeview.Heading",
            background=c["table_header"],
            foreground=c["table_header_fg"],
            font=(self.font, 12, "bold"),
            borderwidth=1,
            relief="solid",
            padding=(8, 6),
        )
        style.map(
            f"{style_name}.Treeview",
            background=[("selected", c["table_selected"])],
            foreground=[("selected", c["table_selected_fg"])],
        )
        # Tag untuk stripe baris genap
        style.configure(
            f"{style_name}.Treeview",
            bordercolor=c["table_border"],
            lightcolor=c["table_border"],
            darkcolor=c["table_border"],
        )

    def _create_treeview(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, str, int, str]],
        style_name: str,
        height: int = 10,
    ) -> ttk.Treeview:
        """Buat Treeview dengan style dan kolom yang dikonfigurasi.

        Args:
            parent: Widget parent.
            columns: List of (col_id, heading_text, width, anchor).
            style_name: Nama style Treeview.
            height: Jumlah baris terlihat.

        Returns:
            ttk.Treeview yang sudah di-configure.
        """
        self._configure_treeview_style(style_name)
        col_ids = [c[0] for c in columns]
        tree = ttk.Treeview(
            parent,
            columns=col_ids,
            show="headings",
            style=f"{style_name}.Treeview",
            height=height,
        )
        for col_id, heading, width, anchor in columns:
            tree.heading(col_id, text=heading)
            tree.column(col_id, width=width, anchor=anchor, minwidth=width)

        # Konfigurasi tag stripe
        tree.tag_configure("even", background=self.colors["table_stripe"])
        tree.tag_configure("odd", background=self.colors["table_row"])
        return tree

    def _insert_striped(self, tree: ttk.Treeview, values: tuple, index: int) -> str:
        """Insert row ke treeview dengan warna stripe.

        Args:
            tree: Treeview target.
            values: Tuple data kolom.
            index: Nomor baris (untuk menentukan ganjil/genap).

        Returns:
            ID item yang di-insert.
        """
        tag = "even" if index % 2 == 0 else "odd"
        return tree.insert("", "end", values=values, tags=(tag,))
