"""
Module produk_view — Halaman manajemen produk (admin).

Menerapkan inheritance dari BaseView, polymorphism, form inline (tanpa window baru),
serta penggunaan array dan control structure.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk

from views.base_view import BaseView
from models.produk import Produk
from utils.theme import ThemeManager


class ProdukView(BaseView):
    """Halaman manajemen produk yang meng-inherit BaseView.

    Override build() untuk menampilkan tabel produk dan form inline.
    Form tambah/edit produk ditampilkan inline (bukan window baru).

    Attributes:
        _tree: Treeview untuk tabel produk.
        _form_frame: Frame form inline tambah/edit.
        _search_var: StringVar untuk pencarian.
        _entries: Dict berisi entry fields form.
        _editing_id: ID produk yang sedang di-edit (None jika tambah baru).
    """

    def __init__(self, parent: ctk.CTkFrame, theme: ThemeManager, app) -> None:
        """Inisialisasi ProdukView."""
        super().__init__(parent, theme, app)
        self._tree: ttk.Treeview | None = None
        self._form_frame: ctk.CTkFrame | None = None
        self._search_var: ctk.StringVar = ctk.StringVar()
        self._entries: dict = {}
        self._editing_id: int | None = None

    # ── Override abstract method (polymorphism) ───────────
    def build(self) -> None:
        """Bangun halaman manajemen produk dengan tabel dan form inline."""
        self._clear()
        c = self.colors

        # ── Header ────────────────────────────────────────
        header = ctk.CTkFrame(self._parent, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(20, 0))

        ctk.CTkLabel(
            header, text="📦  Manajemen Produk",
            font=(self.font, 22, "bold"), text_color=c["text"]
        ).pack(side="left")

        self._btn_tambah = ctk.CTkButton(
            header, text="＋ Tambah Produk", width=160, height=38,
            corner_radius=8, font=(self.font, 13, "bold"),
            fg_color=c["success"], hover_color=c["success_hover"],
            command=self._show_form_tambah,
        )
        self._btn_tambah.pack(side="right")

        # ── Search bar ────────────────────────────────────
        self._search_frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._search_frame.pack(fill="x", padx=28, pady=(12, 0))

        ctk.CTkEntry(
            self._search_frame, textvariable=self._search_var,
            width=320, height=38, corner_radius=8,
            placeholder_text="🔍 Cari produk...", font=(self.font, 13),
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
        ).pack(side="left")
        ctk.CTkButton(
            self._search_frame, text="Cari", width=80, height=38,
            corner_radius=8, font=(self.font, 13),
            fg_color=c["primary"], hover_color=c["primary_hover"],
            command=self._refresh_table,
        ).pack(side="left", padx=(8, 0))

        # ── Inline form (hidden by default) ───────────────
        self._form_frame = ctk.CTkFrame(
            self._parent, fg_color=c["card"], corner_radius=12,
            border_width=1, border_color=c["border"]
        )
        # Form tidak di-pack di sini; akan ditampilkan oleh _show_form_*

        # ── Table card ────────────────────────────────────
        card = ctk.CTkFrame(self._parent, fg_color=c["card"], corner_radius=12,
                              border_width=1, border_color=c["border"])
        card.pack(fill="both", expand=True, padx=28, pady=(12, 8))

        # Array definisi kolom: (col_id, heading, width, anchor)
        columns = [
            ("id", "ID", 60, "center"),
            ("nama", "Nama Produk", 300, "w"),
            ("harga", "Harga (Rp)", 160, "e"),
            ("stok", "Stok", 90, "center"),
        ]
        self._tree = self._create_treeview(card, columns, "Produk", height=14)

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        scrollbar.pack(side="right", fill="y", pady=12, padx=(0, 6))

        # ── Action buttons ────────────────────────────────
        action_frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=28, pady=(0, 16))

        ctk.CTkButton(
            action_frame, text="✏️  Edit", width=120, height=36,
            corner_radius=8, font=(self.font, 13),
            fg_color=c["warning"], hover_color=c["warning_hover"],
            text_color="white", command=self._show_form_edit,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            action_frame, text="🗑  Hapus", width=120, height=36,
            corner_radius=8, font=(self.font, 13),
            fg_color=c["danger"], hover_color=c["danger_hover"],
            command=self._hapus_produk,
        ).pack(side="left")

        self._refresh_table()

    # ── Data refresh ──────────────────────────────────────
    def _refresh_table(self) -> None:
        """Refresh data tabel dari database."""
        for row in self._tree.get_children():
            self._tree.delete(row)

        keyword = self._search_var.get().strip()
        # Percabangan if-else
        if keyword:
            rows = self._app.db.search_produk(keyword)
        else:
            rows = self._app.db.get_all_produk()

        # Pengulangan for + penggunaan array + model Produk
        produk_list = [Produk.from_row(r) for r in rows]
        for i, produk in enumerate(produk_list):
            self._insert_striped(self._tree, tuple(produk.to_array()), i)

    # ── Inline form ───────────────────────────────────────
    def _build_form(self, title: str, defaults: dict | None = None) -> None:
        """Bangun form inline tambah/edit produk (tanpa window baru).

        Args:
            title: Judul form.
            defaults: Dict berisi nilai default {nama, harga, stok}.
        """
        c = self.colors
        defaults = defaults or {"nama": "", "harga": "", "stok": ""}

        # Clear previous form content
        for w in self._form_frame.winfo_children():
            w.destroy()

        # Tampilkan form frame setelah search bar
        self._form_frame.pack_forget()
        self._form_frame.pack(fill="x", padx=28, pady=(12, 0), after=self._search_frame)

        # Title
        top = ctk.CTkFrame(self._form_frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 8))
        ctk.CTkLabel(
            top, text=title, font=(self.font, 16, "bold"), text_color=c["text"]
        ).pack(side="left")
        ctk.CTkButton(
            top, text="✕", width=32, height=32, corner_radius=6,
            fg_color=c["danger"], hover_color=c["danger_hover"],
            font=(self.font, 14, "bold"), command=self._hide_form,
        ).pack(side="right")

        # Fields in horizontal layout
        fields_frame = ctk.CTkFrame(self._form_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=16, pady=(0, 12))

        self._entries = {}
        # Array berisi definisi field form
        field_defs = [
            ("nama", "Nama Produk", defaults["nama"], 3),
            ("harga", "Harga (Rp)", defaults["harga"], 2),
            ("stok", "Stok", defaults["stok"], 1),
        ]
        for field_key, label_text, default_val, weight in field_defs:
            col = ctk.CTkFrame(fields_frame, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkLabel(
                col, text=label_text, font=(self.font, 12, "bold"),
                text_color=c["text"]
            ).pack(anchor="w")
            entry = ctk.CTkEntry(
                col, height=36, corner_radius=8, font=(self.font, 12),
                fg_color=c["input_bg"], border_color=c["input_border"],
                text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
            )
            if default_val:
                entry.insert(0, str(default_val))
            entry.pack(fill="x", pady=(2, 0))
            self._entries[field_key] = entry

        # Save button
        btn_text = "💾  Simpan Perubahan" if self._editing_id else "💾  Simpan Produk"
        ctk.CTkButton(
            fields_frame, text=btn_text, width=160, height=36,
            corner_radius=8, font=(self.font, 13, "bold"),
            fg_color=c["success"], hover_color=c["success_hover"],
            command=self._save_form,
        ).pack(side="left", padx=(0, 0), pady=(18, 0))

    def _show_form_tambah(self) -> None:
        """Tampilkan form inline untuk tambah produk baru."""
        self._editing_id = None
        self._build_form("Tambah Produk Baru")

    def _show_form_edit(self) -> None:
        """Tampilkan form inline untuk edit produk yang dipilih."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin diedit!")
            return
        values = self._tree.item(sel[0])["values"]
        id_produk = int(values[0])
        produk_row = self._app.db.get_produk_by_id(id_produk)
        if not produk_row:
            return
        produk = Produk.from_row(produk_row)
        self._editing_id = produk.id
        self._build_form("Edit Produk", {
            "nama": produk.nama,
            "harga": str(produk.harga),
            "stok": str(produk.stok),
        })

    def _hide_form(self) -> None:
        """Sembunyikan form inline."""
        self._form_frame.pack_forget()
        self._editing_id = None

    def _save_form(self) -> None:
        """Simpan data dari form (tambah baru atau update)."""
        nama = self._entries["nama"].get().strip()
        harga_str = self._entries["harga"].get().strip()
        stok_str = self._entries["stok"].get().strip()

        # Validasi input
        if not nama:
            messagebox.showwarning("Peringatan", "Nama produk harus diisi!")
            return
        try:
            harga = float(harga_str)
            stok = int(stok_str)
        except ValueError:
            messagebox.showwarning("Peringatan", "Harga dan stok harus berupa angka!")
            return

        # Validasi menggunakan model Produk
        produk = Produk(nama=nama, harga=harga, stok=stok)
        if not produk.validate():
            messagebox.showwarning("Peringatan", "Data produk tidak valid! Harga dan stok harus >= 0.")
            return

        # Percabangan: tambah baru atau edit
        if self._editing_id is not None:
            self._app.db.edit_produk(self._editing_id, nama, harga, stok)
            messagebox.showinfo("Sukses", "Produk berhasil diperbarui!")
        else:
            self._app.db.tambah_produk(nama, harga, stok)
            messagebox.showinfo("Sukses", "Produk berhasil ditambahkan!")

        self._hide_form()
        self._refresh_table()

    # ── Hapus produk ──────────────────────────────────────
    def _hapus_produk(self) -> None:
        """Hapus produk yang dipilih setelah konfirmasi."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin dihapus!")
            return
        values = self._tree.item(sel[0])["values"]
        if not messagebox.askyesno("Konfirmasi", f'Hapus produk "{values[1]}"?'):
            return
        self._app.db.hapus_produk(int(values[0]))
        self._refresh_table()
        messagebox.showinfo("Sukses", "Produk berhasil dihapus!")
