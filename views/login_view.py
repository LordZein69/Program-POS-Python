"""
Module login_view — Halaman login untuk autentikasi pengguna.

Menerapkan inheritance dari BaseView dan override method build() (polymorphism).
"""

import customtkinter as ctk
from tkinter import messagebox

from views.base_view import BaseView
from utils.theme import ThemeManager


class LoginView(BaseView):
    """Halaman login yang meng-inherit BaseView.

    Override build() untuk menampilkan form login.

    Attributes:
        _entry_user: Entry widget untuk username.
        _entry_pass: Entry widget untuk password.
    """

    def __init__(self, parent: ctk.CTkFrame, theme: ThemeManager, app) -> None:
        """Inisialisasi LoginView.

        Args:
            parent: Frame container.
            theme: ThemeManager instance.
            app: Referensi ke App utama.
        """
        super().__init__(parent, theme, app)
        self._entry_user: ctk.CTkEntry | None = None
        self._entry_pass: ctk.CTkEntry | None = None

    # ── Override abstract method (polymorphism) ───────────
    def build(self) -> None:
        """Bangun tampilan halaman login."""
        self._clear()
        c = self.colors

        frame = ctk.CTkFrame(self._parent, fg_color=c["card"], corner_radius=16,
                              border_width=1, border_color=c["border"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header icon & title
        ctk.CTkLabel(
            frame, text="🏪", font=(self.font, 48)
        ).pack(pady=(30, 0))
        ctk.CTkLabel(
            frame, text="Sistem POS",
            font=(self.font, 24, "bold"), text_color=c["text"]
        ).pack(pady=(4, 0))
        ctk.CTkLabel(
            frame, text="Silakan login untuk melanjutkan",
            font=(self.font, 12), text_color=c["text_muted"]
        ).pack(pady=(2, 20))

        # Username field
        ctk.CTkLabel(
            frame, text="Username", font=(self.font, 13, "bold"),
            text_color=c["text"], anchor="w"
        ).pack(padx=36, anchor="w")
        self._entry_user = ctk.CTkEntry(
            frame, width=300, height=40, corner_radius=8,
            placeholder_text="Masukkan username", font=(self.font, 13),
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
        )
        self._entry_user.pack(padx=36, pady=(2, 12))

        # Password field
        ctk.CTkLabel(
            frame, text="Password", font=(self.font, 13, "bold"),
            text_color=c["text"], anchor="w"
        ).pack(padx=36, anchor="w")
        self._entry_pass = ctk.CTkEntry(
            frame, width=300, height=40, corner_radius=8,
            placeholder_text="Masukkan password", show="•",
            font=(self.font, 13),
            fg_color=c["input_bg"], border_color=c["input_border"],
            text_color=c["entry_fg"], placeholder_text_color=c["entry_placeholder"],
        )
        self._entry_pass.pack(padx=36, pady=(2, 20))

        # Login button
        ctk.CTkButton(
            frame, text="Login", width=300, height=42,
            corner_radius=8, font=(self.font, 14, "bold"),
            fg_color=c["primary"], hover_color=c["primary_hover"],
            command=self._do_login,
        ).pack(padx=36, pady=(0, 10))

        # Hint
        ctk.CTkLabel(
            frame, text="Admin: admin / admin123  |  Kasir: kasir / kasir123",
            font=(self.font, 10), text_color=c["text_muted"]
        ).pack(pady=(0, 24))

        self._entry_user.focus()
        self._entry_pass.bind("<Return>", lambda e: self._do_login())

    # ── Private method ────────────────────────────────────
    def _do_login(self) -> None:
        """Proses login: validasi input dan autentikasi ke database."""
        username = self._entry_user.get().strip()
        password = self._entry_pass.get().strip()

        # Percabangan if-else
        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan password harus diisi!")
            return

        user = self._app.db.authenticate(username, password)
        if user is None:
            messagebox.showerror("Gagal", "Username atau password salah!")
        else:
            self._app.on_login_success(user[0], user[1])
