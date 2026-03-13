"""
Module kasir_view — Halaman kasir untuk transaksi penjualan.

Menerapkan inheritance dari BaseView, polymorphism, array (keranjang),
control structures (if-else, for), dan struk pembayaran dalam window baru.
"""

import os

import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from typing import List, Dict
from fpdf import FPDF

from views.base_view import BaseView
from models.produk import Produk
from models.transaksi import Transaksi, DetailTransaksi
from utils.theme import ThemeManager


class KasirView(BaseView):
    """Halaman kasir yang meng-inherit BaseView.

    Override build() untuk menampilkan layout kasir.

    Attributes:
        _cart: Array (list) berisi dict item keranjang.
        _tree_produk: Treeview daftar produk.
        _tree_cart: Treeview keranjang belanja.
        _lbl_total: Label total harga.
        _lbl_kembalian: Label kembalian.
        _entry_bayar: Entry nominal pembayaran.
        _entry_qty: Entry jumlah item.
        _search_var: StringVar pencarian produk.
    """

    def __init__(self, parent: ctk.CTkFrame, theme: ThemeManager, app) -> None:
        """Inisialisasi KasirView."""
        super().__init__(parent, theme, app)
        # Array (list) untuk menyimpan item keranjang
        self._cart: List[Dict] = []
        self._tree_produk: ttk.Treeview | None = None
        self._tree_cart: ttk.Treeview | None = None
        self._lbl_total: ctk.CTkLabel | None = None
        self._lbl_kembalian: ctk.CTkLabel | None = None
        self._entry_bayar: ctk.CTkEntry | None = None
        self._entry_qty: ctk.CTkEntry | None = None
        self._search_var: ctk.StringVar = ctk.StringVar()

    # ── Override abstract method (polymorphism) ───────────
    def build(self) -> None:
        """Bangun layout halaman kasir: produk (kiri) + keranjang (kanan)."""
        self._clear()
        self._cart = []
        c = self.colors

        # ═══ LEFT: Daftar Produk ══════════════════════════
        left = ctk.CTkFrame(self._parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(20, 8), pady=16)

        ctk.CTkLabel(
            left, text="📋  Daftar Produk",
            font=(self.font, 18, "bold"), text_color=c["text"]
        ).pack(anchor="w")

        # Search bar
        sf = ctk.CTkFrame(left, fg_color="transparent")
        sf.pack(fill="x", pady=(8, 8))
        ctk.CTkEntry(
            sf, textvariable=self._search_var, height=36, corner_radius=8,
            placeholder_text="🔍 Cari produk...", font=(self.font, 12),
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
        ).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            sf, text="Cari", width=70, height=36, corner_radius=8,
            font=(self.font, 12), fg_color=c["primary"],
            hover_color=c["primary_hover"], command=self._refresh_produk,
        ).pack(side="left", padx=(6, 0))

        # Product table
        card_left = ctk.CTkFrame(left, fg_color=c["card"], corner_radius=12,
                                    border_width=1, border_color=c["border"])
        card_left.pack(fill="both", expand=True)

        columns = [
            ("id", "ID", 50, "center"),
            ("nama", "Nama Produk", 200, "w"),
            ("harga", "Harga (Rp)", 120, "e"),
            ("stok", "Stok", 60, "center"),
        ]
        self._tree_produk = self._create_treeview(card_left, columns, "KasirP", height=12)
        self._tree_produk.pack(fill="both", expand=True, padx=8, pady=8)

        # Add to cart row
        add_frame = ctk.CTkFrame(left, fg_color="transparent")
        add_frame.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(
            add_frame, text="Qty:", font=(self.font, 13, "bold"), text_color=c["text"]
        ).pack(side="left")
        self._entry_qty = ctk.CTkEntry(
            add_frame, width=60, height=36, corner_radius=8, font=(self.font, 13),
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"],
        )
        self._entry_qty.insert(0, "1")
        self._entry_qty.pack(side="left", padx=(6, 10))
        ctk.CTkButton(
            add_frame, text="➕  Tambah ke Keranjang", height=36,
            corner_radius=8, font=(self.font, 13, "bold"),
            fg_color=c["primary"], hover_color=c["primary_hover"],
            command=self._add_to_cart,
        ).pack(side="left", fill="x", expand=True)

        # ═══ RIGHT: Keranjang & Pembayaran ════════════════
        right = ctk.CTkFrame(self._parent, width=380, fg_color=c["card"],
                              corner_radius=12, border_width=1, border_color=c["border"])
        right.pack(side="right", fill="y", padx=(8, 20), pady=16)
        right.pack_propagate(False)

        ctk.CTkLabel(
            right, text="🛒  Keranjang",
            font=(self.font, 18, "bold"), text_color=c["text"]
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Cart table
        cart_cols = [
            ("nama", "Produk", 150, "w"),
            ("qty", "Qty", 50, "center"),
            ("subtotal", "Subtotal (Rp)", 110, "e"),
        ]
        self._tree_cart = self._create_treeview(right, cart_cols, "KasirC", height=9)
        self._tree_cart.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        # Remove item button
        ctk.CTkButton(
            right, text="🗑  Hapus Item", height=32, corner_radius=8,
            font=(self.font, 12), fg_color=c["danger"],
            hover_color=c["danger_hover"], command=self._remove_cart_item,
        ).pack(fill="x", padx=12, pady=(4, 10))

        # Separator
        ctk.CTkFrame(right, height=2, fg_color=c["border"]).pack(fill="x", padx=12)

        # Total display
        self._lbl_total = ctk.CTkLabel(
            right, text="Total: Rp 0",
            font=(self.font, 20, "bold"), text_color=c["text"]
        )
        self._lbl_total.pack(anchor="w", padx=16, pady=(12, 8))

        # Payment entry
        ctk.CTkLabel(
            right, text="Uang Pembayaran:", font=(self.font, 13, "bold"),
            text_color=c["text"]
        ).pack(anchor="w", padx=16)
        self._entry_bayar = ctk.CTkEntry(
            right, height=38, corner_radius=8, font=(self.font, 14),
            placeholder_text="Masukkan nominal...",
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
        )
        self._entry_bayar.pack(fill="x", padx=16, pady=(2, 8))

        # Kembalian display
        self._lbl_kembalian = ctk.CTkLabel(
            right, text="Kembalian: Rp 0",
            font=(self.font, 16, "bold"), text_color=c["success"]
        )
        self._lbl_kembalian.pack(anchor="w", padx=16, pady=(0, 8))

        # Buttons
        ctk.CTkButton(
            right, text="Hitung Kembalian", height=36, corner_radius=8,
            font=(self.font, 13), fg_color=c["primary"],
            hover_color=c["primary_hover"], command=self._hitung_kembalian,
        ).pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkButton(
            right, text="💾  Proses Pembayaran", height=42, corner_radius=8,
            font=(self.font, 14, "bold"), fg_color=c["success"],
            hover_color=c["success_hover"], command=self._proses_bayar,
        ).pack(fill="x", padx=16, pady=(0, 16))

        self._refresh_produk()

    # ── Data methods ──────────────────────────────────────
    def _refresh_produk(self) -> None:
        """Refresh tabel produk dari database."""
        for row in self._tree_produk.get_children():
            self._tree_produk.delete(row)

        keyword = self._search_var.get().strip()
        rows = self._app.db.search_produk(keyword) if keyword else self._app.db.get_all_produk()

        # Pengulangan + array + model
        produk_list = [Produk.from_row(r) for r in rows]
        for i, produk in enumerate(produk_list):
            self._insert_striped(self._tree_produk, tuple(produk.to_array()), i)

    def _refresh_cart_display(self) -> None:
        """Refresh tampilan keranjang dari array _cart."""
        for row in self._tree_cart.get_children():
            self._tree_cart.delete(row)

        total = 0.0
        # Pengulangan for pada array keranjang
        for i, item in enumerate(self._cart):
            self._insert_striped(
                self._tree_cart,
                (item["nama_produk"], item["qty"], f"{item['subtotal']:,.0f}"),
                i,
            )
            total += item["subtotal"]

        self._lbl_total.configure(text=f"Total: Rp {total:,.0f}")
        self._lbl_kembalian.configure(
            text="Kembalian: Rp 0", text_color=self.colors["success"]
        )

    def _get_cart_total(self) -> float:
        """Hitung total dari array keranjang.

        Returns:
            Total harga semua item di keranjang.
        """
        return sum(item["subtotal"] for item in self._cart)

    # ── Cart operations ───────────────────────────────────
    def _add_to_cart(self) -> None:
        """Tambah produk yang dipilih ke array keranjang."""
        sel = self._tree_produk.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih produk terlebih dahulu!")
            return
        try:
            qty = int(self._entry_qty.get().strip())
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah harus berupa angka!")
            return
        if qty <= 0:
            messagebox.showwarning("Peringatan", "Jumlah harus lebih dari 0!")
            return

        values = self._tree_produk.item(sel[0])["values"]
        id_produk = int(values[0])
        nama = str(values[1])
        harga = float(str(values[2]).replace(",", ""))
        stok = int(values[3])

        # Cek stok tersedia (termasuk yang sudah di keranjang)
        already = sum(i["qty"] for i in self._cart if i["id_produk"] == id_produk)
        if qty + already > stok:
            messagebox.showwarning(
                "Peringatan", f"Stok tidak mencukupi! Tersedia: {stok - already}"
            )
            return

        # Percabangan: jika produk sudah di keranjang, update qty
        for item in self._cart:
            if item["id_produk"] == id_produk:
                item["qty"] += qty
                item["subtotal"] = item["qty"] * item["harga"]
                self._refresh_cart_display()
                return

        # Tambah item baru ke array keranjang
        self._cart.append({
            "id_produk": id_produk,
            "nama_produk": nama,
            "harga": harga,
            "qty": qty,
            "subtotal": harga * qty,
        })
        self._refresh_cart_display()

    def _remove_cart_item(self) -> None:
        """Hapus item yang dipilih dari array keranjang."""
        sel = self._tree_cart.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih item yang ingin dihapus!")
            return
        idx = self._tree_cart.index(sel[0])
        del self._cart[idx]
        self._refresh_cart_display()

    # ── Payment ───────────────────────────────────────────
    def _hitung_kembalian(self) -> None:
        """Hitung dan tampilkan kembalian."""
        total = self._get_cart_total()
        if total == 0:
            messagebox.showwarning("Peringatan", "Keranjang masih kosong!")
            return
        try:
            bayar = float(self._entry_bayar.get().strip())
        except ValueError:
            messagebox.showwarning("Peringatan", "Masukkan nominal pembayaran yang valid!")
            return

        kembalian = bayar - total
        # Percabangan if-else
        if kembalian < 0:
            self._lbl_kembalian.configure(
                text=f"Kurang: Rp {abs(kembalian):,.0f}",
                text_color=self.colors["danger"],
            )
        else:
            self._lbl_kembalian.configure(
                text=f"Kembalian: Rp {kembalian:,.0f}",
                text_color=self.colors["success"],
            )

    def _proses_bayar(self) -> None:
        """Proses pembayaran: simpan ke DB dan tampilkan struk."""
        if not self._cart:
            messagebox.showwarning("Peringatan", "Keranjang masih kosong!")
            return

        total = self._get_cart_total()
        try:
            bayar = float(self._entry_bayar.get().strip())
        except ValueError:
            messagebox.showwarning("Peringatan", "Masukkan nominal pembayaran yang valid!")
            return
        if bayar < total:
            messagebox.showwarning("Peringatan", "Uang pembayaran kurang!")
            return

        kembalian = bayar - total
        id_trx = self._app.db.simpan_transaksi(self._cart)

        # Simpan salinan cart untuk PDF sebelum di-clear
        self._last_receipt_items = list(self._cart)

        # Tampilkan struk sebelum reset keranjang
        self._show_receipt(id_trx, total, bayar, kembalian)

        # Reset
        self._cart.clear()
        self._refresh_cart_display()
        self._refresh_produk()
        self._entry_bayar.delete(0, "end")

    # ── Struk Pembayaran (New Window) ─────────────────────
    def _show_receipt(
        self, id_trx: int, total: float, bayar: float, kembalian: float
    ) -> None:
        """Tampilkan struk pembayaran dalam window baru.

        Args:
            id_trx: ID transaksi.
            total: Total belanja.
            bayar: Uang pembayaran.
            kembalian: Uang kembalian.
        """
        c = self.colors
        receipt = ctk.CTkToplevel(self._app)
        receipt.title("Struk Pembayaran")
        receipt.geometry("420x600")
        receipt.resizable(False, False)
        receipt.grab_set()
        receipt.configure(fg_color="#FFFFFF")

        # ── Receipt content (white background like real receipt) ──
        canvas = ctk.CTkFrame(receipt, fg_color="#FFFFFF", corner_radius=0)
        canvas.pack(fill="both", expand=True, padx=20, pady=20)

        txt_color = "#1E293B"
        muted = "#64748B"
        line_color = "#CBD5E1"

        # Store name
        ctk.CTkLabel(
            canvas, text="🏪  TOKO POS", font=(self.font, 20, "bold"),
            text_color=txt_color
        ).pack(pady=(10, 2))
        ctk.CTkLabel(
            canvas, text="Jl. Ida No. 258, Kota",
            font=(self.font, 10), text_color=muted
        ).pack()
        ctk.CTkLabel(
            canvas, text="Telp: (021) 230 030 258",
            font=(self.font, 10), text_color=muted
        ).pack(pady=(0, 8))

        # Separator
        ctk.CTkFrame(canvas, height=2, fg_color=line_color).pack(fill="x", padx=10, pady=4)

        # Transaction info
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        info_frame.pack(fill="x", padx=16, pady=(4, 2))
        ctk.CTkLabel(
            info_frame, text=f"No: TRX-{id_trx:04d}",
            font=(self.font, 11), text_color=txt_color
        ).pack(side="left")
        ctk.CTkLabel(
            info_frame, text=now,
            font=(self.font, 11), text_color=muted
        ).pack(side="right")

        kasir_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        kasir_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(
            kasir_frame, text=f"Kasir: {self._app.current_user}",
            font=(self.font, 11), text_color=txt_color
        ).pack(side="left")

        # Separator
        ctk.CTkFrame(canvas, height=1, fg_color=line_color).pack(fill="x", padx=10, pady=4)

        # Item header
        hdr = ctk.CTkFrame(canvas, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(4, 2))
        ctk.CTkLabel(hdr, text="Item", font=(self.font, 11, "bold"),
                      text_color=txt_color, width=160, anchor="w").pack(side="left")
        ctk.CTkLabel(hdr, text="Qty", font=(self.font, 11, "bold"),
                      text_color=txt_color, width=40, anchor="center").pack(side="left")
        ctk.CTkLabel(hdr, text="Harga", font=(self.font, 11, "bold"),
                      text_color=txt_color, width=80, anchor="e").pack(side="left")
        ctk.CTkLabel(hdr, text="Subtotal", font=(self.font, 11, "bold"),
                      text_color=txt_color, width=80, anchor="e").pack(side="right")

        ctk.CTkFrame(canvas, height=1, fg_color=line_color).pack(fill="x", padx=10, pady=2)

        # Items — pengulangan for pada array keranjang
        items_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        items_frame.pack(fill="x")

        for item in self._cart:
            row = ctk.CTkFrame(items_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=1)
            ctk.CTkLabel(
                row, text=item["nama_produk"], font=(self.font, 11),
                text_color=txt_color, width=160, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=str(item["qty"]), font=(self.font, 11),
                text_color=txt_color, width=40, anchor="center"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"{item['harga']:,.0f}", font=(self.font, 11),
                text_color=muted, width=80, anchor="e"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"{item['subtotal']:,.0f}", font=(self.font, 11),
                text_color=txt_color, width=80, anchor="e"
            ).pack(side="right")

        # Separator
        ctk.CTkFrame(canvas, height=2, fg_color=line_color).pack(fill="x", padx=10, pady=(8, 4))

        # Totals
        totals = [
            ("Total", f"Rp {total:,.0f}", (self.font, 14, "bold"), txt_color),
            ("Bayar", f"Rp {bayar:,.0f}", (self.font, 12), txt_color),
            ("Kembalian", f"Rp {kembalian:,.0f}", (self.font, 14, "bold"), "#16A34A"),
        ]
        for label, value, fnt, color in totals:
            r = ctk.CTkFrame(canvas, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(r, text=label, font=fnt, text_color=color).pack(side="left")
            ctk.CTkLabel(r, text=value, font=fnt, text_color=color).pack(side="right")

        # Separator
        ctk.CTkFrame(canvas, height=1, fg_color=line_color).pack(fill="x", padx=10, pady=(8, 4))

        # Footer
        ctk.CTkLabel(
            canvas, text="Terima kasih atas kunjungan Anda!",
            font=(self.font, 12, "bold"), text_color=muted
        ).pack(pady=(4, 2))
        ctk.CTkLabel(
            canvas, text="Barang yang sudah dibeli tidak dapat dikembalikan",
            font=(self.font, 9), text_color=muted
        ).pack(pady=(0, 10))

        # Buttons row
        btn_row = ctk.CTkFrame(receipt, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkButton(
            btn_row, text="📄  Cetak PDF", width=160, height=38, corner_radius=8,
            font=(self.font, 13, "bold"), fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda: self._export_receipt_pdf(
                id_trx, total, bayar, kembalian, list(self._last_receipt_items)
            ),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Tutup", width=160, height=38, corner_radius=8,
            font=(self.font, 13, "bold"), fg_color=c["primary"],
            hover_color=c["primary_hover"], command=receipt.destroy,
        ).pack(side="left")

    # ── PDF Receipt Export ────────────────────────────────
    def _export_receipt_pdf(
        self,
        id_trx: int,
        total: float,
        bayar: float,
        kembalian: float,
        items: List[Dict],
    ) -> None:
        """Export struk pembayaran ke file PDF.

        Args:
            id_trx: ID transaksi.
            total: Total belanja.
            bayar: Uang pembayaran.
            kembalian: Uang kembalian.
            items: Salinan array keranjang.
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Struk_TRX-{id_trx:04d}.pdf",
            title="Simpan Struk PDF",
        )
        if not filepath:
            return

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        pdf = FPDF(unit="mm", format=(80, 200))
        pdf.set_auto_page_break(auto=True, margin=5)
        pdf.add_page()
        pdf.set_font("Helvetica", size=7)

        w = 70  # usable width (80 - margins)

        # ─── Header ──────────────────────────────────────
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(w, 5, "TOKO POS", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=7)
        pdf.cell(w, 3.5, "Jl. Ida No. 258, Kota", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(w, 3.5, "Telp: (021) 230 030 258", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Dashed separator
        pdf.cell(w, 3, "-" * 40, align="C", new_x="LMARGIN", new_y="NEXT")

        # ─── Transaction info ─────────────────────────────
        pdf.set_font("Helvetica", size=7)
        pdf.cell(w / 2, 4, f"No: TRX-{id_trx:04d}", new_x="END")
        pdf.cell(w / 2, 4, now, align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(w, 4, f"Kasir: {self._app.current_user}", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(w, 3, "-" * 40, align="C", new_x="LMARGIN", new_y="NEXT")

        # ─── Column headers ──────────────────────────────
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(28, 4, "Item", new_x="END")
        pdf.cell(8, 4, "Qty", align="C", new_x="END")
        pdf.cell(16, 4, "Harga", align="R", new_x="END")
        pdf.cell(18, 4, "Subtotal", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", size=7)
        pdf.cell(w, 3, "-" * 40, align="C", new_x="LMARGIN", new_y="NEXT")

        # ─── Items ────────────────────────────────────────
        for item in items:
            nama = item["nama_produk"]
            # Potong nama jika terlalu panjang
            if len(nama) > 16:
                nama = nama[:15] + "."
            pdf.cell(28, 4, nama, new_x="END")
            pdf.cell(8, 4, str(item["qty"]), align="C", new_x="END")
            pdf.cell(16, 4, f"{item['harga']:,.0f}", align="R", new_x="END")
            pdf.cell(18, 4, f"{item['subtotal']:,.0f}", align="R", new_x="LMARGIN", new_y="NEXT")

        # ─── Totals ───────────────────────────────────────
        pdf.cell(w, 3, "=" * 40, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(w / 2, 5, "Total", new_x="END")
        pdf.cell(w / 2, 5, f"Rp {total:,.0f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", size=7)
        pdf.cell(w / 2, 4, "Bayar", new_x="END")
        pdf.cell(w / 2, 4, f"Rp {bayar:,.0f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(w / 2, 5, "Kembalian", new_x="END")
        pdf.cell(w / 2, 5, f"Rp {kembalian:,.0f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(w, 3, "-" * 40, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # ─── Footer ──────────────────────────────────────
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(w, 4, "Terima kasih atas kunjungan Anda!", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=6)
        pdf.cell(w, 3, "Barang yang sudah dibeli tidak dapat dikembalikan", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.output(filepath)
        messagebox.showinfo("Sukses", f"Struk berhasil disimpan:\n{filepath}")

        # Buka PDF otomatis
        try:
            os.startfile(filepath)
        except Exception:
            pass
