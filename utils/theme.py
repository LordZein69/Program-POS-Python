"""
Module theme — Manajemen tema (dark mode / light mode).

Menerapkan:
- Class dengan property
- Dictionary sebagai data structure
- Percabangan if-else untuk switching tema
"""

from typing import Dict


class ThemeManager:
    """Manager untuk tema tampilan aplikasi (dark/light mode).

    Menyediakan palet warna yang berubah sesuai mode aktif.

    Attributes:
        _mode: Mode aktif ('light' atau 'dark').
        _themes: Dictionary berisi palet warna per mode.
    """

    def __init__(self, mode: str = "light") -> None:
        """Inisialisasi ThemeManager.

        Args:
            mode: Mode awal ('light' atau 'dark').
        """
        # Array (dict) berisi semua definisi warna untuk kedua mode
        self._themes: Dict[str, Dict[str, str]] = {
            "light": {
                "primary": "#2563EB",
                "primary_hover": "#1D4ED8",
                "success": "#16A34A",
                "success_hover": "#15803D",
                "danger": "#DC2626",
                "danger_hover": "#B91C1C",
                "warning": "#F59E0B",
                "warning_hover": "#D97706",
                "bg": "#F1F5F9",
                "card": "#FFFFFF",
                "text": "#1E293B",
                "text_secondary": "#475569",
                "text_muted": "#64748B",
                "border": "#CBD5E1",
                "sidebar": "#1E293B",
                "sidebar_text": "#F8FAFC",
                "sidebar_hover": "#334155",
                "sidebar_active": "#2563EB",
                "table_bg": "#FFFFFF",
                "table_header": "#E2E8F0",
                "table_header_fg": "#1E293B",
                "table_row": "#FFFFFF",
                "table_stripe": "#F8FAFC",
                "table_selected": "#BFDBFE",
                "table_selected_fg": "#1E293B",
                "table_border": "#CBD5E1",
                "input_bg": "#FFFFFF",
                "input_border": "#CBD5E1",
                "entry_fg": "#1E293B",
                "entry_placeholder": "#94A3B8",
            },
            "dark": {
                "primary": "#3B82F6",
                "primary_hover": "#2563EB",
                "success": "#22C55E",
                "success_hover": "#16A34A",
                "danger": "#EF4444",
                "danger_hover": "#DC2626",
                "warning": "#F59E0B",
                "warning_hover": "#D97706",
                "bg": "#0F172A",
                "card": "#1E293B",
                "text": "#F1F5F9",
                "text_secondary": "#CBD5E1",
                "text_muted": "#94A3B8",
                "border": "#334155",
                "sidebar": "#0F172A",
                "sidebar_text": "#F1F5F9",
                "sidebar_hover": "#1E293B",
                "sidebar_active": "#3B82F6",
                "table_bg": "#1E293B",
                "table_header": "#334155",
                "table_header_fg": "#F1F5F9",
                "table_row": "#1E293B",
                "table_stripe": "#263348",
                "table_selected": "#1E3A5F",
                "table_selected_fg": "#F1F5F9",
                "table_border": "#475569",
                "input_bg": "#334155",
                "input_border": "#475569",
                "entry_fg": "#F1F5F9",
                "entry_placeholder": "#64748B",
            },
        }
        self._mode: str = mode if mode in self._themes else "light"

    # ── Properties ────────────────────────────────────────
    @property
    def mode(self) -> str:
        """Getter mode tema aktif."""
        return self._mode

    @property
    def colors(self) -> Dict[str, str]:
        """Getter palet warna sesuai mode aktif.

        Returns:
            Dictionary berisi key-value warna.
        """
        return self._themes[self._mode]

    # ── Methods ───────────────────────────────────────────
    def toggle(self) -> str:
        """Toggle antara dark mode dan light mode.

        Returns:
            Mode baru setelah toggle.
        """
        # Percabangan if-else
        if self._mode == "light":
            self._mode = "dark"
        else:
            self._mode = "light"
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Set mode tema secara eksplisit.

        Args:
            mode: 'light' atau 'dark'.
        """
        if mode in self._themes:
            self._mode = mode

    def get_color(self, key: str) -> str:
        """Ambil satu warna berdasarkan key.

        Args:
            key: Nama warna (misal 'primary', 'bg', dll).

        Returns:
            Kode warna hex string.
        """
        return self._themes[self._mode].get(key, "#000000")

    @property
    def font_family(self) -> str:
        """Font family utama aplikasi."""
        return "Segoe UI"
