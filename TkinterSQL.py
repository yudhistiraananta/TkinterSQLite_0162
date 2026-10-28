"""
Aplikasi Prediksi Risiko Diabetes
Python + Tkinter + SQLite (database: prediksi_diabetes.db)
"""

import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prediksi_diabetes.db")

WARNA_RISIKO = {
    "Rendah": "#2e9e4f",
    "Waspada": "#d4a017",
    "Sedang": "#e67e22",
    "Tinggi": "#d9381e",
    "Sangat Tinggi": "#8b0000",
}



def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pasien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pasien TEXT NOT NULL,
                usia INTEGER NOT NULL,
                gula_darah REAL NOT NULL,
                bmi REAL NOT NULL,
                riwayat_ortu TEXT NOT NULL,
                hasil_prediksi TEXT NOT NULL
            )
            """
        )


def simpan_pasien(nama, usia, gula, bmi, riwayat, hasil):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO pasien (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nama, usia, gula, bmi, riwayat, hasil),
        )


def ambil_semua_pasien():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi "
            "FROM pasien ORDER BY id DESC"
        ).fetchall()



def prediksi_risiko(gula, bmi, riwayat):
    """
    Aturan:
    - Gula >= 200            : Sangat Tinggi bila BMI >= 30 atau ada riwayat ortu, selain itu Tinggi.
    - Gula 140-199           : Tinggi bila BMI >= 30 atau ada riwayat ortu, selain itu Sedang.
    - Gula < 140 & BMI >= 30 : Sedang bila ada riwayat ortu, selain itu Waspada.
    - Gula < 140 & BMI < 30  : Waspada bila ada riwayat ortu, selain itu Rendah.
    """
    ada_riwayat = riwayat == "Ya"
    obesitas = bmi >= 30

    if gula >= 200:
        return "Sangat Tinggi" if (obesitas or ada_riwayat) else "Tinggi"
    if gula >= 140:
        return "Tinggi" if (obesitas or ada_riwayat) else "Sedang"
    if obesitas:
        return "Sedang" if ada_riwayat else "Waspada"
    return "Waspada" if ada_riwayat else "Rendah"



def validasi_input(nama, usia, gula, bmi, riwayat):
    """Mengembalikan (data_valid, pesan_error)."""
    nama = nama.strip()
    if not nama:
        return None, "Nama pasien tidak boleh kosong."
    if len(nama) < 3 or len(nama) > 50:
        return None, "Nama pasien harus 3-50 karakter."
    if not re.fullmatch(r"[A-Za-z .,'\-]+", nama):
        return None, "Nama pasien hanya boleh berisi huruf, spasi, dan tanda baca nama (. , ' -)."

    try:
        usia_val = int(usia.strip())
    except ValueError:
        return None, "Usia harus berupa bilangan bulat."
    if not 1 <= usia_val <= 120:
        return None, "Usia harus berada di antara 1 dan 120 tahun."

    try:
        gula_val = float(gula.strip().replace(",", "."))
    except ValueError:
        return None, "Kadar gula darah harus berupa angka."
    if not 20 <= gula_val <= 600:
        return None, "Kadar gula darah harus berada di antara 20 dan 600 mg/dL."

    try:
        bmi_val = float(bmi.strip().replace(",", "."))
    except ValueError:
        return None, "BMI harus berupa angka."
    if not 10 <= bmi_val <= 70:
        return None, "BMI harus berada di antara 10 dan 70."

    if riwayat not in ("Ya", "Tidak"):
        return None, "Pilih riwayat diabetes orang tua (Ya/Tidak)."

    return (nama, usia_val, gula_val, bmi_val, riwayat), None



class AplikasiDiabetes(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prediksi Risiko Diabetes")
        self.geometry("680x700")
        self.resizable(False, False)
        self.warna_latar = "#f3f6fb"
        self.warna_utama = "#173b57"
        self.warna_aksen = "#17a589"
        self.configure(bg=self.warna_latar)
        self._atur_style()
        self._buat_widget()

    def _atur_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.warna_latar)
        style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat",
        )
        style.configure(
            "Header.TLabel",
            background=self.warna_utama,
            foreground="#ffffff",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.warna_utama,
            foreground="#d7e5ef",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background="#ffffff",
            foreground=self.warna_utama,
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background="#ffffff",
            foreground="#34495e",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Hint.TLabel",
            background="#ffffff",
            foreground="#7b8a97",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Footer.TLabel",
            background=self.warna_latar,
            foreground="#7b8a97",
            font=("Segoe UI", 9),
        )
        style.configure(
            "TEntry",
            fieldbackground="#f8fafc",
            foreground="#243746",
            padding=(10, 8),
            bordercolor="#dce4ec",
            lightcolor="#dce4ec",
            darkcolor="#dce4ec",
        )
        style.configure(
            "TCombobox",
            fieldbackground="#f8fafc",
            foreground="#243746",
            padding=(8, 7),
            bordercolor="#dce4ec",
            lightcolor="#dce4ec",
            darkcolor="#dce4ec",
        )
        style.configure(
            "Primary.TButton",
            background=self.warna_aksen,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#12816b"), ("pressed", "#0f6f5c")],
            foreground=[("disabled", "#dce4ec")],
        )
        style.configure(
            "Secondary.TButton",
            background="#eaf0f5",
            foreground=self.warna_utama,
            font=("Segoe UI", 10, "bold"),
            padding=(14, 10),
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#dce6ee"), ("pressed", "#cfdae4")],
        )
        style.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#263746",
            rowheight=32,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=self.warna_utama,
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 10),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", "#d8eee9")],
            foreground=[("selected", self.warna_utama)],
        )

    def _buat_widget(self):
        header = tk.Frame(self, bg=self.warna_utama, padx=38, pady=25)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="Prediksi Risiko Diabetes",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Catat data pasien dan dapatkan gambaran tingkat risiko.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        card = ttk.Frame(self, style="Card.TFrame", padding=(30, 24))
        card.pack(fill="both", expand=True, padx=34, pady=(22, 12))

        ttk.Label(
            card,
            text="Data Pasien",
            style="Section.TLabel",
        ).pack(anchor="w", pady=(0, 16))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        self.var_nama = tk.StringVar()
        self.var_usia = tk.StringVar()
        self.var_gula = tk.StringVar()
        self.var_bmi = tk.StringVar()
        self.var_riwayat = tk.StringVar()

        fields = (
            ("Nama Pasien", self.var_nama, "entry", "Masukkan nama lengkap"),
            ("Usia", self.var_usia, "entry", "Tahun"),
            ("Gula Darah", self.var_gula, "entry", "mg/dL"),
            ("BMI", self.var_bmi, "entry", "Indeks massa tubuh"),
            ("Riwayat Diabetes Ortu", self.var_riwayat, "choice", ""),
        )
        for row, (label, variable, field_type, hint) in enumerate(fields):
            ttk.Label(form, text=label, style="Field.TLabel").grid(
                row=row, column=0, sticky="w", padx=(0, 18), pady=8
            )
            if field_type == "choice":
                field = ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=("Ya", "Tidak"),
                    state="readonly",
                )
            else:
                field = ttk.Entry(form, textvariable=variable)
            field.grid(row=row, column=1, sticky="ew", pady=8)
            if hint:
                ttk.Label(form, text=hint, style="Hint.TLabel").grid(
                    row=row, column=2, sticky="w", padx=(10, 0)
                )

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(18, 18))
        ttk.Label(
            card,
            text="Hasil Prediksi",
            style="Section.TLabel",
        ).pack(anchor="w", pady=(0, 10))
        self.lbl_hasil = tk.Label(
            card,
            text="Hasil akan tampil di sini",
            font=("Segoe UI", 13, "bold"),
            height=2,
            bg="#edf2f7",
            fg="#7b8a97",
            anchor="w",
            padx=18,
        )
        self.lbl_hasil.pack(fill="x")

        tombol = ttk.Frame(card, style="Card.TFrame")
        tombol.pack(fill="x", pady=(20, 0))
        ttk.Button(
            tombol,
            text="Prediksi & Simpan",
            command=self.proses_prediksi,
            style="Primary.TButton",
        ).pack(side="left")
        ttk.Button(
            tombol,
            text="Lihat Riwayat",
            command=self.lihat_data,
            style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))
        ttk.Button(
            tombol,
            text="Reset",
            command=self.reset_form,
            style="Secondary.TButton",
        ).pack(side="right")

        ttk.Label(
            self,
            text="Hasil prediksi merupakan skrining awal, bukan diagnosis medis.",
            style="Footer.TLabel",
        ).pack(pady=(0, 14))

    def proses_prediksi(self):
        data, error = validasi_input(
            self.var_nama.get(),
            self.var_usia.get(),
            self.var_gula.get(),
            self.var_bmi.get(),
            self.var_riwayat.get(),
        )
        if error:
            messagebox.showwarning("Input Tidak Valid", error)
            return

        nama, usia, gula, bmi, riwayat = data
        hasil = prediksi_risiko(gula, bmi, riwayat)

        try:
            simpan_pasien(nama, usia, gula, bmi, riwayat, hasil)
        except sqlite3.Error as e:
            messagebox.showerror("Kesalahan Database", f"Gagal menyimpan data:\n{e}")
            return

        self.lbl_hasil.config(
            text=f"Risiko {hasil}", bg=WARNA_RISIKO[hasil], fg="white"
        )
        messagebox.showinfo("Berhasil", f"Data {nama} tersimpan.\nRisiko diabetes: {hasil}")

    def reset_form(self):
        for var in (self.var_nama, self.var_usia, self.var_gula, self.var_bmi, self.var_riwayat):
            var.set("")
        self.lbl_hasil.config(
            text="Hasil akan tampil di sini",
            bg="#edf2f7",
            fg="#7b8a97",
        )

    def lihat_data(self):
        win = tk.Toplevel(self)
        win.title("Riwayat Data Pasien")
        win.geometry("900x460")
        win.configure(bg=self.warna_latar)

        kolom = ("id", "nama", "usia", "gula", "bmi", "riwayat", "hasil")
        judul = ("ID", "Nama Pasien", "Usia", "Gula Darah", "BMI", "Riwayat Ortu", "Hasil Prediksi")
        lebar = (40, 190, 60, 90, 60, 100, 120)

        container = ttk.Frame(win, padding=18)
        container.pack(fill="both", expand=True)
        tree = ttk.Treeview(container, columns=kolom, show="headings")
        for k, j, w in zip(kolom, judul, lebar):
            tree.heading(k, text=j)
            tree.column(k, width=w, anchor="center" if k != "nama" else "w")

        tree.tag_configure("even", background="#f3f7fa")
        for risiko, warna in WARNA_RISIKO.items():
            tree.tag_configure(risiko, foreground=warna)

        scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        try:
            baris = ambil_semua_pasien()
        except sqlite3.Error as e:
            messagebox.showerror("Kesalahan Database", f"Gagal membaca data:\n{e}")
            win.destroy()
            return

        if not baris:
            messagebox.showinfo("Informasi", "Belum ada data pasien tersimpan.")
        for index, row in enumerate(baris):
            tags = (row[6], "even") if index % 2 == 0 else (row[6],)
            tree.insert("", "end", values=row, tags=tags)


if __name__ == "__main__":
    init_db()
    AplikasiDiabetes().mainloop()