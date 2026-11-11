# =====================================================================
# SESI 12 · TEKNOLOGI INFORMASI · PEMROGRAMAN DASAR PENGELOLAAN DATA
# ---------------------------------------------------------------------
# Kasus : Unit Arsip Fakultas menerima ekspor "daftar arsip" dari
#         aplikasi lama. Datanya berantakan. Sebelum menyusun usul
#         musnah dan penyerahan arsip statis akhir tahun 2026, data
#         harus dirapikan, dihitung retensinya, lalu disimpan.
# Input : data/daftar_arsip_fakultas.csv          (1 berkas mentah)
# Output: database MySQL bernama sesi12          (DBeaver, Power BI)
#         output/daftar_arsip_bersih.csv           (salinan cadangan)
# Versi : MySQL / MariaDB. Langkah 0–10 sama dengan versi PostgreSQL;
#         yang berbeda hanya import (Langkah 0) dan Langkah 11.
# Cara  : buka folder repositori di VS Code, lalu di Terminal ketik
#             python scripts/olah_daftar_arsip_mysql.py
#         (Windows boleh juga: py scripts/olah_daftar_arsip_mysql.py)
# Catatan: semua data FIKTIF, dibuat khusus untuk latihan.
# =====================================================================


# ---------------------------------------------------------------------
# LANGKAH 0 · Menyiapkan alat (import) dan alamat berkas
# ---------------------------------------------------------------------
# "import" = meminjam kotak perkakas yang sudah dibuat orang lain.
#   pandas  : perkakas utama mengolah tabel (seperti Excel versi kode)
#   sqlalchemy + pymysql : jembatan Python ke MySQL
#   Path    : menulis alamat folder/berkas yang aman di Windows & Mac
#   datetime: mengolah tanggal
#   getpass : meminta password tanpa menampilkannya di layar
from datetime import datetime
from getpass import getpass
from pathlib import Path

import pandas as pd
from sqlalchemy import URL, Date, create_engine, text

# Alamat dihitung dari lokasi skrip ini, sehingga skrip tetap jalan
# walaupun dijalankan dengan tombol Run (▶) di VS Code.
# __file__ = berkas skrip ini; .parent = folder di atasnya.
FOLDER_REPO = Path(__file__).resolve().parent.parent
BERKAS_MENTAH = FOLDER_REPO / "data" / "daftar_arsip_fakultas.csv"
FOLDER_OUTPUT = FOLDER_REPO / "output"
FOLDER_OUTPUT.mkdir(exist_ok=True)       # buat folder bila belum ada

# Tanggal acuan penilaian retensi: akhir tahun 2026, saat unit arsip
# biasanya menyusun daftar usul musnah. Dibuat tetap (bukan "hari
# ini") agar hasil semua mahasiswa sama dan bisa dicocokkan.
TANGGAL_ACUAN = pd.Timestamp("2026-12-31")


# ---------------------------------------------------------------------
# LANGKAH 1 · Membaca CSV dan mengenali isinya
# ---------------------------------------------------------------------
# dtype=str  : baca semua kolom sebagai teks dulu, supaya tidak ada
#              nilai yang "diubah diam-diam" oleh pandas.
# keep_default_na=False : sel kosong dibaca sebagai "" (teks kosong).
df = pd.read_csv(BERKAS_MENTAH, dtype=str, keep_default_na=False)

print("=== LANGKAH 1 · Kenali data ===")
print("Jumlah baris, kolom :", df.shape)      # (baris, kolom)
print("Nama kolom          :", list(df.columns))
print(df.head())                              # 5 baris pertama


# ---------------------------------------------------------------------
# LANGKAH 2 · Merapikan teks: buang spasi berlebih
# ---------------------------------------------------------------------
# Spasi di awal/akhir tidak terlihat, tetapi membuat "Akademik" dan
# " Akademik" dianggap dua nilai berbeda oleh komputer.
# for ... in ... : ulangi perintah yang sama untuk setiap kolom.
for kolom in df.columns:
    df[kolom] = df[kolom].str.strip()         # strip = buang spasi tepi

# Ganti spasi ganda di tengah judul menjadi satu spasi.
df["judul"] = df["judul"].str.replace(r"\s+", " ", regex=True)


# ---------------------------------------------------------------------
# LANGKAH 3 · Kosakata terkendali (ingat Sesi 11: metadata konsisten)
# ---------------------------------------------------------------------
# Kamus (dictionary) Python: { "nilai di data" : "nilai baku" }.
# Kunci ditulis huruf kecil karena data akan kita kecilkan dulu.
KAMUS_UNIT = {
    "kepegawaian": "Kepegawaian", "kpg": "Kepegawaian",
    "kepeg.": "Kepegawaian",
    "keuangan": "Keuangan", "keu": "Keuangan", "keu.": "Keuangan",
    "akademik": "Akademik", "akd": "Akademik", "akad.": "Akademik",
    "kemahasiswaan": "Kemahasiswaan", "kmh": "Kemahasiswaan",
    "umum dan perlengkapan": "Umum dan Perlengkapan",
    "umum & perlengkapan": "Umum dan Perlengkapan",
    "ump": "Umum dan Perlengkapan",
}
KAMUS_MEDIA = {
    "kertas": "Kertas", "fisik": "Kertas",
    "elektronik": "Elektronik", "digital": "Elektronik",
    "e-arsip": "Elektronik",
}
KAMUS_AKSES = {"biasa": "Biasa", "terbatas": "Terbatas",
               "rahasia": "Rahasia"}

# .str.lower() = jadikan huruf kecil; .map(kamus) = terjemahkan.
# Nilai yang tidak ada di kamus akan menjadi kosong (NaN): itu
# tanda ada variasi baru yang harus ditambahkan ke kamus.
df["unit_pencipta"] = df["unit_pencipta"].str.lower().map(KAMUS_UNIT)
df["media"] = df["media"].str.lower().map(KAMUS_MEDIA)
df["tingkat_akses"] = df["tingkat_akses"].str.lower().map(KAMUS_AKSES)

print("\n=== LANGKAH 3 · Nilai unit setelah dibakukan ===")
print(df["unit_pencipta"].value_counts(dropna=False))


# ---------------------------------------------------------------------
# LANGKAH 4 · Menyeragamkan tanggal ke ISO 8601 (YYYY-MM-DD)
# ---------------------------------------------------------------------
# Data berisi tiga format: 2019-03-14, 14/03/2019, dan 14-03-2019.
# def = membuat fungsi sendiri. Fungsi ini mencoba tiap format satu
# per satu; format pertama yang cocok dipakai.
def baca_tanggal(teks):
    for pola in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return pd.Timestamp(datetime.strptime(teks, pola))
        except ValueError:
            pass                              # tidak cocok, coba pola lain
    return pd.NaT                             # NaT = "Not a Time" (kosong)

# .apply(fungsi) = jalankan fungsi untuk setiap baris kolom itu.
df["tanggal_arsip"] = df["tanggal_arsip"].apply(baca_tanggal)
# Kolom bantu "tahun" untuk grafik. Int64 = bilangan bulat yang
# boleh kosong (agar tidak tampil sebagai 2018.0).
df["tahun"] = df["tanggal_arsip"].dt.year.astype("Int64")

# Kolom jumlah_lembar diubah dari teks ke angka (kosong -> NaN).
df["jumlah_lembar"] = pd.to_numeric(df["jumlah_lembar"],
                                    errors="coerce").astype("Int64")


# ---------------------------------------------------------------------
# LANGKAH 5 · Membuang baris duplikat (ekspor ganda)
# ---------------------------------------------------------------------
jumlah_awal = len(df)
df = df.drop_duplicates()                     # hapus baris kembar persis
print("\n=== LANGKAH 5 · Duplikat ===")
print("Duplikat dibuang    :", jumlah_awal - len(df))
print("Sisa baris          :", len(df))


# ---------------------------------------------------------------------
# LANGKAH 6 · Menghubungkan dengan Jadwal Retensi Arsip (JRA)
# ---------------------------------------------------------------------
# JRA (fiktif) disimpan sebagai tabel kecil di dalam skrip.
# Isi tiap baris: kode, nama klasifikasi, retensi aktif (tahun),
# retensi inaktif (tahun), dan keterangan nasib akhir arsip.
JRA = pd.DataFrame([
    ("KP.01", "Formasi Pegawai",          2, 3, "Musnah"),
    ("KP.02", "Cuti Pegawai",             1, 2, "Musnah"),
    ("KP.03", "Penilaian Kinerja",        2, 3, "Musnah"),
    ("KP.04", "Pengangkatan Pegawai",     2, 8, "Permanen"),
    ("KU.01", "Pertanggungjawaban Keuangan", 2, 8, "Musnah"),
    ("KU.02", "Laporan Keuangan Tahunan", 2, 8, "Permanen"),
    ("AK.01", "Jadwal Perkuliahan",       1, 1, "Musnah"),
    ("AK.02", "Daftar Nilai",             2, 5, "Musnah"),
    ("AK.03", "Kurikulum dan RPS",        3, 5, "Permanen"),
    ("KM.01", "Beasiswa",                 2, 3, "Musnah"),
    ("KM.02", "Kegiatan Kemahasiswaan",   2, 3, "Musnah"),
    ("UM.01", "Pengadaan Barang",         2, 5, "Musnah"),
    ("UM.02", "Surat Edaran Pimpinan",    2, 3, "Permanen"),
], columns=["kode_klasifikasi", "nama_klasifikasi",
            "retensi_aktif", "retensi_inaktif", "keterangan_jra"])

# merge = JOIN di SQL (Sesi 7). how="left": semua arsip tetap ada,
# walaupun kodenya tidak ditemukan di JRA (kolom JRA-nya kosong).
df = df.merge(JRA, on="kode_klasifikasi", how="left")
for kolom in ["retensi_aktif", "retensi_inaktif"]:
    df[kolom] = df[kolom].astype("Int64")     # tetap bilangan bulat


# ---------------------------------------------------------------------
# LANGKAH 7 · Menghitung akhir retensi dan status arsip
# ---------------------------------------------------------------------
# Akhir aktif   = tanggal arsip + retensi aktif
# Akhir inaktif = akhir aktif   + retensi inaktif
def tambah_tahun(tanggal, tahun):
    if pd.isna(tanggal) or pd.isna(tahun):
        return pd.NaT                         # data kurang, tak bisa hitung
    return tanggal + pd.DateOffset(years=int(tahun))

df["akhir_aktif"] = [tambah_tahun(t, n) for t, n in
                     zip(df["tanggal_arsip"], df["retensi_aktif"])]
df["akhir_inaktif"] = [tambah_tahun(t, n) for t, n in
                       zip(df["akhir_aktif"], df["retensi_inaktif"])]

# if / elif / else = percabangan: komputer memilih satu jalan.
def tentukan_status(baris):
    if pd.isna(baris["akhir_inaktif"]):
        return "Perlu Dicek"                  # tanggal/kode bermasalah
    if TANGGAL_ACUAN < baris["akhir_aktif"]:
        return "Aktif"
    if TANGGAL_ACUAN < baris["akhir_inaktif"]:
        return "Inaktif"
    if baris["keterangan_jra"] == "Musnah":
        return "Usul Musnah"
    return "Serah ke Arsip Statis"            # keterangan Permanen

# axis=1 berarti fungsi dijalankan per BARIS (bukan per kolom).
df["status_retensi"] = df.apply(tentukan_status, axis=1)


# ---------------------------------------------------------------------
# LANGKAH 8 · Menandai masalah kualitas metadata
# ---------------------------------------------------------------------
# Setiap baris diberi catatan bila ada metadata wajib yang kosong.
def catatan_kualitas(baris):
    masalah = []                              # list kosong
    if baris["judul"] == "":
        masalah.append("judul kosong")
    if pd.isna(baris["tanggal_arsip"]):
        masalah.append("tanggal kosong")
    if pd.isna(baris["nama_klasifikasi"]):
        masalah.append("kode tidak ada di JRA")
    return "; ".join(masalah)                 # gabung jadi satu teks

df["catatan_kualitas"] = df.apply(catatan_kualitas, axis=1)
df["perlu_dicek"] = df["catatan_kualitas"] != ""   # True / False


# ---------------------------------------------------------------------
# LANGKAH 9 · Ringkasan di layar
# ---------------------------------------------------------------------
print("\n=== LANGKAH 9 · Ringkasan ===")
print("Total arsip bersih  :", len(df))
print("\nJumlah per status retensi:")
print(df["status_retensi"].value_counts())
print("\nPerlu dicek manual  :", df["perlu_dicek"].sum(), "arsip")


# ---------------------------------------------------------------------
# LANGKAH 10 · Merapikan urutan kolom dan menyimpan salinan CSV
# ---------------------------------------------------------------------
# Atur urutan kolom agar mudah dibaca.
URUTAN = ["no_arsip", "kode_klasifikasi", "nama_klasifikasi", "judul",
          "unit_pencipta", "tanggal_arsip", "tahun", "media",
          "jumlah_lembar", "tingkat_akses", "lokasi_simpan",
          "retensi_aktif", "retensi_inaktif", "keterangan_jra",
          "akhir_aktif", "akhir_inaktif", "status_retensi",
          "perlu_dicek", "catatan_kualitas"]
df = df[URUTAN].sort_values("no_arsip")

# Salinan CSV (cadangan bila PostgreSQL bermasalah; ingat Sesi 10).
# utf-8-sig: huruf tetap terbaca benar saat dibuka di Excel.
df.to_csv(FOLDER_OUTPUT / "daftar_arsip_bersih.csv",
          index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
print("\nSalinan CSV tersimpan :", FOLDER_OUTPUT)


# ---------------------------------------------------------------------
# LANGKAH 11 · Menyimpan ke database MySQL
# ---------------------------------------------------------------------
# Isian sama dengan koneksi MySQL Anda di DBeaver (Sesi 7).
# Ubah bila berbeda di laptop Anda.
MY_HOST = "localhost"         # server di laptop sendiri
MY_PORT = 3306                # port bawaan MySQL
MY_USER = "root"              # user saat instalasi
NAMA_DB = "sesi12"            # database khusus sesi ini (dibuat otomatis)

# Password TIDAK ditulis di kode (Sesi 9): kode ini akan di-push ke
# GitHub. Saat skrip berjalan, ketik password di Terminal lalu Enter.
# Hurufnya memang tidak tampil saat diketik; itu disengaja.
MY_PASSWORD = getpass("Password MySQL: ")

# Di MySQL, "database" berperan seperti "skema" di PostgreSQL.
# Karena itu kita sambung dulu ke server TANPA memilih database,
# lalu membuat database sesi12 bila belum ada.
# charset=utf8mb4: semua huruf (termasuk simbol) tersimpan benar.
def alamat(database=None):
    return URL.create("mysql+pymysql", username=MY_USER,
                      password=MY_PASSWORD, host=MY_HOST,
                      port=MY_PORT, database=database,
                      query={"charset": "utf8mb4"})

with create_engine(alamat()).begin() as koneksi:
    koneksi.execute(text(f"CREATE DATABASE IF NOT EXISTS {NAMA_DB} "
                         "CHARACTER SET utf8mb4"))

# Sekarang sambung langsung ke database sesi12.
mesin = create_engine(alamat(NAMA_DB))

# engine.begin(): buka koneksi, jalankan, lalu COMMIT otomatis bila
# semua berhasil (atau ROLLBACK bila ada galat, ingat Sesi 10).
with mesin.begin() as koneksi:
    # if_exists="replace": tabel lama ditimpa, jadi aman dijalankan
    # berulang kali tanpa data ganda. Kolom tanggal diberi tipe DATE.
    # Catatan: MySQL menyimpan True/False sebagai angka 1/0.
    df.to_sql("arsip", koneksi, if_exists="replace", index=False,
              dtype={"tanggal_arsip": Date(), "akhir_aktif": Date(),
                     "akhir_inaktif": Date()})
    JRA.to_sql("jra", koneksi, if_exists="replace", index=False)
    # Bukti: hitung ulang baris langsung dari database.
    n = koneksi.execute(text("SELECT COUNT(*) FROM arsip"))
    print("Tersimpan di MySQL :", f"{NAMA_DB}.arsip", "=",
          n.scalar(), "baris")

print("\nSelesai!")
