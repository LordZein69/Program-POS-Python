"""
main.py — Entry point untuk Sistem POS & Manajemen Inventori.

Menerapkan:
- CustomTkinter (external library) untuk GUI modern
- SQLite (database) untuk penyimpanan data
- Multiple packages (models, database, views, utils)
- OOP: inheritance, polymorphism, properties, overloading, abstract class
- Dark mode / Light mode toggle
- Fullscreen saat startup

Cara menjalankan:
    python main.py
"""

import customtkinter as ctk

from database.db_manager import DatabaseManager
from utils.theme import ThemeManager
from views.login_view import LoginView
from views.produk_view import ProdukView
from views.kasir_view import KasirView
from views.riwayat_view import RiwayatView


class App(ctk.CTk):
    """Kelas utama aplikasi POS.

    Mengelola navigasi antar halaman, sidebar, dan state pengguna.

    Attributes:
        db: Instance DatabaseManager untuk akses data.
        theme: Instance ThemeManager untuk tema warna.
        current_user: Username pengguna yang sedang login.
        current_role: Role pengguna ('admin' atau 'kasir').
    """

    def __init__(self) -> None:
        """Inisialisasi aplikasi: setup window, database, dan tema."""
        super().__init__()
        self.title("Sistem POS & Manajemen Inventori")
        self._is_fullscreen: bool = True

        # Fullscreen saat startup (lebih stabil untuk mode .exe)
        self.after(100, self._apply_startup_fullscreen)
        self.minsize(960, 600)
        self.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda e: self._exit_fullscreen())

        # Inisialisasi komponen
        self.db: DatabaseManager = DatabaseManager()
        self.theme: ThemeManager = ThemeManager("light")
        self.current_user: str | None = None
        self.current_role: str | None = None

        # Array untuk sidebar buttons
        self._sidebar_btns: list = []
        self._sidebar: ctk.CTkFrame | None = None
        self._content: ctk.CTkFrame | None = None

        self.db.init_db()

        # Set appearance mode dari CustomTkinter
        ctk.set_appearance_mode(self.theme.mode)
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=self.theme.colors["bg"])
        self._show_login()

    def _apply_startup_fullscreen(self) -> None:
        """Terapkan fullscreen saat startup dengan fallback maximize.

        Pada beberapa build .exe, fullscreen atau zoomed bisa berbeda perilakunya.
        Coba fullscreen dulu, lalu fallback ke maximize/geometry layar penuh.
        """
        try:
            self.attributes("-fullscreen", True)
            self._is_fullscreen = True
        except Exception:
            self._is_fullscreen = False

        if not self._is_fullscreen:
            try:
                self.state("zoomed")
            except Exception:
                pass

        if not self._is_fullscreen and self.state() != "zoomed":
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}+0+0")

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen dengan shortcut F11."""
        self._is_fullscreen = not self._is_fullscreen
        self.attributes("-fullscreen", self._is_fullscreen)
        if not self._is_fullscreen:
            self.state("zoomed")

    def _exit_fullscreen(self) -> None:
        """Keluar dari fullscreen dengan tombol Escape."""
        self._is_fullscreen = False
        self.attributes("-fullscreen", False)
        self.state("zoomed")

    # ══════════════════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════════════════
    def _clear_all(self) -> None:
        """Hapus semua widget dari window utama."""
        for w in self.winfo_children():
            w.destroy()

    def _show_login(self) -> None:
        """Tampilkan halaman login."""
        self._clear_all()
        c = self.theme.colors
        self.configure(fg_color=c["bg"])

        # Container for login (centered)
        container = ctk.CTkFrame(self, fg_color=c["bg"], corner_radius=0)
        container.pack(fill="both", expand=True)

        view = LoginView(container, self.theme, self)
        view.build()

    def on_login_success(self, username: str, role: str) -> None:
        """Callback saat login berhasil.

        Args:
            username: Username pengguna.
            role: Role pengguna.
        """
        self.current_user = username
        self.current_role = role
        self._show_main_layout()

    def _show_main_layout(self) -> None:
        """Bangun layout utama: sidebar + content area."""
        self._clear_all()
        c = self.theme.colors

        # ── Sidebar ───────────────────────────────────────
        self._sidebar = ctk.CTkFrame(
            self, width=230, fg_color=c["sidebar"], corner_radius=0
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Brand
        ctk.CTkLabel(
            self._sidebar, text="🏪  POS System",
            font=(self.theme.font_family, 18, "bold"),
            text_color=c["sidebar_text"],
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            self._sidebar,
            text=f"Login: {self.current_user} ({self.current_role})",
            font=(self.theme.font_family, 11),
            text_color=c["text_muted"],
        ).pack(pady=(0, 16))

        ctk.CTkFrame(
            self._sidebar, height=1, fg_color=c["sidebar_hover"]
        ).pack(fill="x", padx=16, pady=(0, 12))

        # Menu — percabangan if-else berdasarkan role
        self._sidebar_btns = []
        menus: list = []
        if self.current_role == "admin":
            menus = [
                ("📦  Manajemen Produk", self._page_produk),
                ("📋  Riwayat Transaksi", self._page_riwayat),
            ]
        else:
            menus = [
                ("🛒  Kasir", self._page_kasir),
                ("📋  Riwayat Transaksi", self._page_riwayat),
            ]

        # Pengulangan for — buat tombol menu
        for label, cmd in menus:
            btn = ctk.CTkButton(
                self._sidebar, text=label, anchor="w",
                font=(self.theme.font_family, 14), height=42,
                fg_color="transparent", text_color=c["sidebar_text"],
                hover_color=c["sidebar_hover"], corner_radius=8,
                command=cmd,
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._sidebar_btns.append(btn)

        # ── Spacer ────────────────────────────────────────
        spacer = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # ── Dark/Light toggle ─────────────────────────────
        toggle_label = "🌙  Dark Mode" if self.theme.mode == "light" else "☀️  Light Mode"
        self._btn_theme = ctk.CTkButton(
            self._sidebar, text=toggle_label, anchor="w",
            font=(self.theme.font_family, 13), height=38,
            fg_color="transparent", text_color=c["sidebar_text"],
            hover_color=c["sidebar_hover"], corner_radius=8,
            command=self._toggle_theme,
        )
        self._btn_theme.pack(fill="x", padx=12, pady=(0, 4))

        # Logout
        ctk.CTkButton(
            self._sidebar, text="🚪  Logout", anchor="w",
            font=(self.theme.font_family, 13), height=38,
            fg_color="transparent", text_color="#F87171",
            hover_color="#7F1D1D", corner_radius=8,
            command=self._logout,
        ).pack(fill="x", padx=12, pady=(0, 20))

        # ── Content area ──────────────────────────────────
        self._content = ctk.CTkFrame(self, fg_color=c["bg"], corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

        # Default page
        if self.current_role == "admin":
            self._page_produk()
        else:
            self._page_kasir()

    # ── Sidebar helpers ───────────────────────────────────
    def _highlight_sidebar(self, idx: int) -> None:
        """Highlight tombol sidebar aktif.

        Args:
            idx: Index tombol yang aktif.
        """
        c = self.theme.colors
        # Pengulangan for
        for i, btn in enumerate(self._sidebar_btns):
            if i == idx:
                btn.configure(fg_color=c["sidebar_active"])
            else:
                btn.configure(fg_color="transparent")

    def _clear_content(self) -> None:
        """Hapus semua widget dari content area."""
        for w in self._content.winfo_children():
            w.destroy()

    # ── Theme toggle ──────────────────────────────────────
    def _toggle_theme(self) -> None:
        """Toggle dark/light mode dan rebuild layout."""
        new_mode = self.theme.toggle()
        ctk.set_appearance_mode(new_mode)
        # Rebuild seluruh layout agar warna berubah
        self._show_main_layout()

    # ── Logout ────────────────────────────────────────────
    def _logout(self) -> None:
        """Logout dan kembali ke halaman login."""
        self.current_user = None
        self.current_role = None
        self._show_login()

    # ══════════════════════════════════════════════════════
    #  PAGES — Delegasi ke View classes (polymorphism)
    # ══════════════════════════════════════════════════════
    def _page_produk(self) -> None:
        """Tampilkan halaman manajemen produk (admin)."""
        self._clear_content()
        self._highlight_sidebar(0)
        view = ProdukView(self._content, self.theme, self)
        view.build()

    def _page_kasir(self) -> None:
        """Tampilkan halaman kasir."""
        self._clear_content()
        self._highlight_sidebar(0)
        view = KasirView(self._content, self.theme, self)
        view.build()

    def _page_riwayat(self) -> None:
        """Tampilkan halaman riwayat transaksi."""
        self._clear_content()
        self._highlight_sidebar(1)
        view = RiwayatView(self._content, self.theme, self)
        view.build()


if __name__ == "__main__":
    app = App()
    app.mainloop()
