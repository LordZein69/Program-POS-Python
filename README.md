# Sistem Point of Sale (POS) & Manajemen Inventori Barang

Aplikasi desktop untuk manajemen inventori dan transaksi penjualan, dibangun dengan Python, CustomTkinter, dan SQLite.

## Fitur

- **Manajemen Produk** — Tambah, edit, hapus, dan cari produk dengan form inline
- **Kasir / Transaksi** — Keranjang belanja, pembayaran, struk, dan ekspor PDF
- **Riwayat Transaksi** — Daftar transaksi dengan detail item (master-detail)
- **Autentikasi** — Login dengan role admin dan kasir
- **Dark / Light Mode** — Toggle tema gelap dan terang
- **Fullscreen** — Tampilan fullscreen saat startup

## Teknologi

| Komponen   | Teknologi         |
| ---------- | ----------------- |
| Bahasa     | Python 3.13       |
| GUI        | CustomTkinter 5.x |
| Database   | SQLite 3          |
| PDF Export | fpdf2             |

## Struktur Proyek

```
work/
├── main.py                 # Entry point aplikasi
├── models/                 # Package model data
│   ├── __init__.py
│   ├── base.py             # Abstract Base Class (ABC)
│   ├── produk.py           # Model Produk
│   ├── transaksi.py        # Model Transaksi & DetailTransaksi
│   └── pengguna.py         # Model Pengguna
├── database/               # Package database
│   ├── __init__.py
│   └── db_manager.py       # CRUD & manajemen koneksi SQLite
├── views/                  # Package tampilan GUI
│   ├── __init__.py
│   ├── base_view.py        # Abstract base view
│   ├── login_view.py       # Halaman login
│   ├── produk_view.py      # Halaman manajemen produk
│   ├── kasir_view.py       # Halaman kasir & struk
│   └── riwayat_view.py     # Halaman riwayat transaksi
├── utils/                  # Package utilitas
│   ├── __init__.py
│   └── theme.py            # ThemeManager (dark/light mode)
└── .gitignore
```

## Konsep OOP yang Diterapkan

- **Abstract Base Class (ABC)** — `BaseModel`, `BaseView`
- **Inheritance** — Semua model inherit dari `BaseModel`, semua view inherit dari `BaseView`
- **Polymorphism** — Override method `to_dict()`, `from_row()`, `validate()`, `build()`
- **Properties** — Getter/setter dengan validasi di semua model
- **Operator Overloading** — `__str__`, `__repr__`, `__eq__` pada model
- **Array / List** — Keranjang belanja, daftar item transaksi
- **Control Structures** — If-else, for loop, while, try-except

## Instalasi

1. **Clone atau download** proyek ini

2. **Install dependencies:**

   ```bash
   pip install customtkinter fpdf2
   ```

3. **Jalankan aplikasi:**
   ```bash
   python main.py
   ```

## Akun Default

| Username | Password | Role  |
| -------- | -------- | ----- |
| admin    | admin123 | Admin |
| kasir    | kasir123 | Kasir |

## Build Executable

### Download Link (GitHub Releases)

- Download dari tab **Releases** di GitHub: https://github.com/LordZein69/Program-POS-Python/releases/tag/Latest
- Direct link EXE: [POS.System.exe](https://github.com/LordZein69/Program-POS-Python/releases/download/Latest/POS.System.exe)

### Download EXE (untuk pengguna)

- File siap pakai: `dist/POS System.exe`
- Versi ZIP (disarankan untuk distribusi): `dist/POS-System-Windows.zip`
- Untuk pengguna umum, gunakan download dari tab **Releases** GitHub agar bisa langsung pakai tanpa install Python.

### Build EXE sendiri (untuk developer)

Untuk membuat file `.exe` dari source code:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "POS System" main.py
```

Hasil build ada di folder `dist/`.
