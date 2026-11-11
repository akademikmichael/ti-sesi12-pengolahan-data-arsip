# Sesi 12 · Pemrograman Dasar untuk Pengelolaan Data Arsip

Mata Kuliah Teknologi Informasi · Program Studi Manajemen Rekod dan Arsip
Pengampu: Sony Harianto

## Kasus

Unit Arsip Fakultas menerima **ekspor daftar arsip** dari aplikasi lama: 1.236 baris, 2015–2025.
Akhir tahun 2026 unit harus menyusun **daftar usul musnah** dan **daftar arsip yang diserahkan ke arsip statis**.
Masalahnya, datanya berantakan: nama unit ditulis macam-macam, format tanggal campur, ada baris ganda, ada judul dan tanggal kosong.

Alur kerja: **Git → CSV → VS Code → Python → PostgreSQL (DBeaver) → Power BI → GitHub Anda.**

> Semua data di repositori ini **fiktif**, dibuat khusus untuk latihan. JRA di dalam skrip juga fiktif, bukan JRA resmi.

## Isi repositori

```
ti-sesi12-pengolahan-data-arsip/
├── data/daftar_arsip_fakultas.csv     ← data mentah (jangan diubah)
├── scripts/olah_daftar_arsip.py       ← skrip Python, 12 langkah, berkomentar
├── sql/latihan_dbeaver.sql            ← 6 query pemeriksaan + bonus
├── powerbi/panduan_powerbi.md         ← panduan dashboard
├── output/                            ← salinan CSV muncul di sini
├── requirements.txt
└── README.md
```

## Persiapan (cek sebelum kelas)

| Perangkat | Cek |
|---|---|
| Git | `git --version` |
| Python 3.10+ | `python --version` (Windows: `py --version`) |
| PostgreSQL (dari Sesi 7) | koneksi PostgreSQL di DBeaver bisa dibuka; **ingat password user `postgres`** |
| VS Code + ekstensi **Python** (Microsoft) | buka VS Code → Extensions |
| DBeaver Community | buka aplikasinya |
| Power BI Desktop (Windows) | buka aplikasinya |

## Langkah 1 · Git clone

```bash
cd Documents
git clone https://github.com/USERNAME/ti-sesi12-pengolahan-data-arsip.git
cd ti-sesi12-pengolahan-data-arsip
git log --oneline
```

## Langkah 2 · Lihat data mentah

Buka `data/daftar_arsip_fakultas.csv` di VS Code (opsional: pasang ekstensi **Rainbow CSV**).
Cari lima masalah: variasi nama unit, tiga format tanggal, variasi media/akses, baris ganda, judul/tanggal kosong.

## Langkah 3 · Siapkan VS Code

1. **File → Open Folder…** → pilih folder `ti-sesi12-pengolahan-data-arsip`.
2. **Terminal → New Terminal**.
3. Pasang pustaka (pandas, sqlalchemy, psycopg2):
   ```bash
   py -m pip install -r requirements.txt        # Windows
   python3 -m pip install -r requirements.txt   # Mac
   ```
4. `Ctrl+Shift+P` → **Python: Select Interpreter** → pilih Python yang tadi dipakai.
5. Pastikan layanan PostgreSQL menyala (biasanya otomatis sejak laptop dinyalakan).

## Langkah 4 · Jalankan skrip Python

```bash
py scripts/olah_daftar_arsip.py       # Windows
python3 scripts/olah_daftar_arsip.py  # Mac
```

Skrip akan meminta `Password PostgreSQL:`. Ketik password user `postgres`, lalu Enter (hurufnya tidak tampil, itu disengaja).
Password sengaja **tidak** ditulis di kode karena kode ini akan di-push ke GitHub (Sesi 9).

Hasil yang benar di akhir layar:

```
Total arsip bersih  : 1200
Usul Musnah 571 · Inaktif 429 · Aktif 77 · Serah ke Arsip Statis 70 · Perlu Dicek 53
Perlu dicek manual  : 72 arsip
Tersimpan di PostgreSQL : postgres › sesi12.arsip = 1200 baris
```

Isian koneksi (host, port, user, database) ada di Langkah 11 skrip. Ubah bila berbeda dengan laptop Anda.

### Memakai MySQL, bukan PostgreSQL?

Jalankan versi MySQL. Langkah 0–10 identik; hanya penyimpanan (Langkah 11) yang berbeda.

```bash
py scripts\olah_daftar_arsip_mysql.py        # Windows
python3 scripts/olah_daftar_arsip_mysql.py   # Mac
```

- Isian bawaan: host `localhost`, port `3306`, user `root`. Ubah di Langkah 11 bila berbeda.
- Skrip membuat **database** `sesi12` (di MySQL, database berperan seperti skema di PostgreSQL), berisi tabel `arsip` dan `jra`.
- Hasil yang benar: `Tersimpan di MySQL : sesi12.arsip = 1200 baris`.
- Di DBeaver: koneksi MySQL Anda → Refresh (F5) → **sesi12 → Tables**. Berkas `sql/latihan_dbeaver.sql` berjalan tanpa perubahan.
- Power BI: **Get data → MySQL database** butuh driver *MySQL Connector/NET* (unduh dari dev.mysql.com). Bila belum terpasang, pakai cadangan `output/daftar_arsip_bersih.csv`.

## Langkah 5 · Periksa di DBeaver

1. Buka koneksi PostgreSQL Anda (Sesi 7). Klik kanan → **Refresh** (F5).
2. Buka **postgres → Schemas → sesi12 → Tables**: harus ada `arsip` dan `jra`.
   Database `postgres` tidak terlihat? Klik kanan koneksi → **Edit Connection** → tab **PostgreSQL** → centang **Show all databases**.
3. Klik database `postgres` → **SQL Editor → Open SQL script** (`Ctrl+]`), salin isi `sql/latihan_dbeaver.sql`, jalankan satu per satu dengan `Ctrl+Enter`.

Kunci: Q1 = 1200 · Q3 Kepegawaian 264 tertinggi · Q4 total 1189 (11 arsip berkode `XX.99` tidak masuk JRA) · Q5 = 72 baris · Bonus = 118 arsip habis retensi tahun 2027.

## Langkah 6 · Dashboard Power BI

Ikuti `powerbi/panduan_powerbi.md` (sumber data: PostgreSQL langsung).

## Langkah 7 · Push ke repositori GitHub Anda sendiri

Hasil clone masih menunjuk ke repositori dosen, yang tidak bisa Anda push. Arahkan dulu ke repositori Anda.

**Sebelumnya di github.com:** **New repository** → nama, misalnya `ti-sesi12-latihan` → **Create repository**.
**Jangan** centang *Add a README*, *.gitignore*, atau *license*: repositori harus kosong.

```bash
# 0. Sekali per laptop: identitas penulis commit
git config --global user.name "Nama Lengkap"
git config --global user.email "email-akun-github@contoh.com"

# 1. Repositori dosen jadi upstream; repositori Anda jadi origin
git remote rename origin upstream
git remote add origin https://github.com/NAMA/ti-sesi12-latihan.git
git remote -v

# 2. Commit pekerjaan
git add scripts/latihan_sesi12.py
git commit -m "Latihan Sesi 12: olah daftar arsip"

# 3. Push (pertama kali: login lewat browser)
git push -u origin main
```

- Push pertama membuka jendela **Sign in with GitHub** → **Authorize**.
- Diminta password di terminal? Isi **Personal Access Token**, bukan password akun:
  GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → izin **Contents: Read and write**.
- Folder `output/` tidak ikut ter-push (diatur `.gitignore`), karena bisa dibuat ulang dari skrip.
- Mengambil pembaruan dari dosen: `git pull upstream main`.
- Sudah punya repositori pribadi sejak Sesi 7? Cukup salin `latihan_sesi12.py` ke folder `sesi12` di repositori itu, lalu add, commit, push dari sana.

Kirim tautan repositori Anda di EMAS UI sebagai bukti partisipasi.

| Pesan push | Penyebab | Solusi |
|---|---|---|
| `Permission denied` / `403` | masih push ke repositori dosen | ulangi langkah 1; `git remote -v` harus menunjukkan akun Anda |
| `Author identity unknown` | nama & email belum diatur | langkah 0, lalu ulangi commit |
| `src refspec main does not match any` | belum ada commit | langkah 2 dulu |
| `rejected ... (fetch first)` | repositori GitHub dibuat dengan README | `git pull origin main --rebase --allow-unrelated-histories`, lalu push |
| `Authentication failed` | kredensial lama tersimpan | hapus `git:https://github.com` di Credential Manager (Windows) / Keychain (Mac) |

## Galat yang sering muncul

| Pesan | Penyebab | Solusi |
|---|---|---|
| `'python' is not recognized` | Python belum masuk PATH | pakai `py` (Windows) / `python3` (Mac) |
| `No module named 'pandas'` / `'sqlalchemy'` / `'psycopg2'` | pustaka terpasang di Python lain | ulangi Langkah 3 nomor 3–4 dengan perintah python yang sama |
| `password authentication failed for user "postgres"` | password salah | jalankan ulang, ketik password yang dipakai saat instal PostgreSQL |
| `'cryptography' package is required` | login MySQL 8 butuh pustaka tambahan | `py -m pip install -r requirements.txt` |
| `Access denied for user 'root'@'localhost'` | password MySQL salah | jalankan ulang, ketik password MySQL yang benar |
| `connection ... failed: Connection refused` | layanan PostgreSQL mati | Windows: **Services** → `postgresql-x64-1x` → Start · Mac (Postgres.app): klik Start |
| `database "postgres" does not exist` / port lain | instalasi berbeda | sesuaikan `PG_DB` / `PG_PORT` di Langkah 11 |
| DBeaver: skema `sesi12` tidak ada | belum di-refresh | klik kanan koneksi → **Refresh** (F5) |
