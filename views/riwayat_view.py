"""
Module riwayat_view — Halaman riwayat transaksi.

Menerapkan inheritance dari BaseView dan polymorphism (override build).
"""

import customtkinter as ctk
from tkinter import ttk

from views.base_view import BaseView
from models.transaksi import Transaksi, DetailTransaksi
from utils.theme import ThemeManager


class RiwayatView(BaseView):
    """Halaman riwayat transaksi yang meng-inherit BaseView.

    Override build() untuk menampilkan daftar dan detail transaksi.

    Attributes:
        _tree_trx: Treeview daftar transaksi.
        _tree_detail: Treeview detail transaksi.
    """

    def __init__(self, parent: ctk.CTkFrame, theme: ThemeManager, app) -> None:
        """Inisialisasi RiwayatView."""
        super().__init__(parent, theme, app)
        self._tree_trx: ttk.Treeview | None = None
        self._tree_detail: ttk.Treeview | None = None

    # ── Override abstract method (polymorphism) ───────────
    def build(self) -> None:
        """Bangun halaman riwayat transaksi."""
        self._clear()
        c = self.colors

        # Header
        ctk.CTkLabel(
            self._parent, text="📋  Riwayat Transaksi",
            font=(self.font, 22, "bold"), text_color=c["text"]
        ).pack(anchor="w", padx=28, pady=(20, 12))

        # ── Top: Daftar Transaksi ─────────────────────────
        card_top = ctk.CTkFrame(self._parent, fg_color=c["card"], corner_radius=12,
                                  border_width=1, border_color=c["border"])
        card_top.pack(fill="x", padx=28, pady=(0, 8))

        trx_cols = [
            ("id", "ID Transaksi", 120, "center"),
            ("tanggal", "Tanggal & Waktu", 240, "w"),
            ("total", "Total (Rp)", 180, "e"),
        ]
        self._tree_trx = self._create_treeview(card_top, trx_cols, "Riwayat", height=8)
        self._tree_trx.pack(fill="x", padx=12, pady=12)
        self._tree_trx.bind("<<TreeviewSelect>>", self._on_select)

        # ── Bottom: Detail Transaksi ──────────────────────
        ctk.CTkLabel(
            self._parent, text="Detail Transaksi",
            font=(self.font, 16, "bold"), text_color=c["text"]
        ).pack(anchor="w", padx=28, pady=(8, 4))

        card_bottom = ctk.CTkFrame(self._parent, fg_color=c["card"], corner_radius=12,
                                     border_width=1, border_color=c["border"])
        card_bottom.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        det_cols = [
            ("no", "No", 50, "center"),
            ("nama", "Produk", 220, "w"),
            ("qty", "Qty", 70, "center"),
            ("harga", "Harga (Rp)", 140, "e"),
            ("subtotal", "Subtotal (Rp)", 140, "e"),
        ]
        self._tree_detail = self._create_treeview(card_bottom, det_cols, "RiwayatD")
        self._tree_detail.pack(fill="both", expand=True, padx=12, pady=12)

        # Load data
        self._load_transaksi()

    # ── Data methods ──────────────────────────────────────
    def _load_transaksi(self) -> None:
        """Muat semua transaksi dari database ke tabel."""
        rows = self._app.db.get_all_transaksi()
        # Pengulangan + array + model
        transaksi_list = [Transaksi.from_row(r) for r in rows]
        for i, trx in enumerate(transaksi_list):
            self._insert_striped(
                self._tree_trx,
                (f"TRX-{trx.id:04d}", trx.tanggal, f"{trx.total:,.0f}"),
                i,
            )

    def _on_select(self, event) -> None:
        """Event handler saat transaksi dipilih — tampilkan detail.

        Args:
            event: Tkinter event object.
        """
        sel = self._tree_trx.selection()
        if not sel:
            return

        # Ambil ID dari string "TRX-0001" → 1
        trx_id_str = str(self._tree_trx.item(sel[0])["values"][0])
        id_trx = int(trx_id_str.replace("TRX-", ""))

        # Clear detail table
        for row in self._tree_detail.get_children():
            self._tree_detail.delete(row)

        # Load detail dari database
        details = self._app.db.get_detail_transaksi(id_trx)
        detail_list = [DetailTransaksi.from_row(d) for d in details]

        # Pengulangan for + array
        for i, det in enumerate(detail_list):
            self._insert_striped(
                self._tree_detail,
                (i + 1, det.nama_produk, det.qty, f"{det.harga:,.0f}", f"{det.subtotal:,.0f}"),
                i,
            )
