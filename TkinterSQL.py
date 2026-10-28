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
        self.geometry("460x520")
        self.resizable(False, False)
        self._buat_widget()

    def _buat_widget(self):
        ttk.Label(
            self, text="Prediksi Risiko Diabetes", font=("Segoe UI", 16, "bold")
        ).pack(pady=(15, 5))
        ttk.Label(self, text="Isi data pasien di bawah ini").pack(pady=(0, 10))

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x", padx=20)

        self.var_nama = tk.StringVar()
        self.var_usia = tk.StringVar()
        self.var_gula = tk.StringVar()
        self.var_bmi = tk.StringVar()
        self.var_riwayat = tk.StringVar()

        ttk.Label(form, text="Nama Pasien").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.var_nama, width=30).grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Usia (tahun)").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.var_usia, width=30).grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Gula Darah (mg/dL)").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.var_gula, width=30).grid(row=2, column=1, pady=6)

        ttk.Label(form, text="BMI").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.var_bmi, width=30).grid(row=3, column=1, pady=6)

        ttk.Label(form, text="Riwayat Diabetes Ortu").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Combobox(
            form,
            textvariable=self.var_riwayat,
            values=("Ya", "Tidak"),
            state="readonly",
            width=27,
        ).grid(row=4, column=1, pady=6)

        tombol = ttk.Frame(self)
        tombol.pack(pady=15)
        ttk.Button(tombol, text="Prediksi & Simpan", command=self.proses_prediksi).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(tombol, text="Lihat Data", command=self.lihat_data).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(tombol, text="Reset", command=self.reset_form).grid(
            row=0, column=2, padx=5
        )

        ttk.Label(self, text="Hasil Prediksi:", font=("Segoe UI", 11, "bold")).pack()
        self.lbl_hasil = tk.Label(
            self,
            text="-",
            font=("Segoe UI", 18, "bold"),
            width=22,
            height=2,
            bg="#e0e0e0",
            fg="black",
        )
        self.lbl_hasil.pack(pady=10)

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
        self.lbl_hasil.config(text="-", bg="#e0e0e0", fg="black")

    def lihat_data(self):
        win = tk.Toplevel(self)
        win.title("Riwayat Data Pasien")
        win.geometry("760x380")

        kolom = ("id", "nama", "usia", "gula", "bmi", "riwayat", "hasil")
        judul = ("ID", "Nama Pasien", "Usia", "Gula Darah", "BMI", "Riwayat Ortu", "Hasil Prediksi")
        lebar = (40, 190, 60, 90, 60, 100, 120)

        tree = ttk.Treeview(win, columns=kolom, show="headings")
        for k, j, w in zip(kolom, judul, lebar):
            tree.heading(k, text=j)
            tree.column(k, width=w, anchor="center" if k != "nama" else "w")

        for risiko, warna in WARNA_RISIKO.items():
            tree.tag_configure(risiko, foreground=warna)

        scroll = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
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
        for row in baris:
            tree.insert("", "end", values=row, tags=(row[6],))


if __name__ == "__main__":
    init_db()
    AplikasiDiabetes().mainloop()