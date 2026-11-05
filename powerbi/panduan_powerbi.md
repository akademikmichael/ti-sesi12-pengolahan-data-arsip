# Langkah 6 · Dashboard "Usul Musnah 2026" di Power BI Desktop

Sumber data: tabel `sesi12.arsip` di PostgreSQL (hasil skrip Python).
Power BI Desktop hanya tersedia untuk Windows. Pengguna Mac bergabung dengan teman sebelah.

## A. Menghubungkan Power BI ke PostgreSQL

1. Buka **Power BI Desktop** → **Blank report**.
2. **Home → Get data → More…** → kategori **Database** → **PostgreSQL database** → **Connect**.
3. Isi:
   - **Server**: `localhost`  (bila port bukan 5432, tulis `localhost:5433`)
   - **Database**: `postgres`
   - **Data Connectivity mode**: **Import**
   → **OK**.
4. Jendela kredensial: pilih tab **Database** (kiri), isi **User name** `postgres` dan **Password** Anda → **Connect**.
5. Muncul pesan *"Unable to connect using an encrypted connection…"*? Klik **OK** untuk tersambung tanpa enkripsi.
   Ini wajar karena server ada di laptop sendiri. Untuk server kantor, minta admin mengaktifkan SSL (Sesi 9).
6. Di **Navigator**, centang **sesi12.arsip** → klik **Transform Data**.
7. Di Power Query, panel **Query Settings** (kanan) → **Name**: ganti `sesi12 arsip` menjadi **`arsip`**.
   Periksa ikon tipe: `tanggal_arsip`, `akhir_aktif`, `akhir_inaktif` sudah **Date** (dibawa dari PostgreSQL), `perlu_dicek` **True/False**.
8. **Home → Close & Apply**. Tabel `arsip` muncul di panel **Data** (kanan).

> Cadangan: bila PostgreSQL gagal tersambung, pakai **Get data → Text/CSV** → `output/daftar_arsip_bersih.csv`, lalu beri nama query `arsip`. Langkah berikutnya sama persis.

## B. Membuat ukuran (measure)

Klik kanan tabel `arsip` di panel Data → **New measure**, lalu ketik satu per satu:

```
Total Arsip = COUNTROWS(arsip)
```
```
Usul Musnah = CALCULATE([Total Arsip], arsip[status_retensi] = "Usul Musnah")
```
```
Perlu Dicek = CALCULATE([Total Arsip], arsip[perlu_dicek] = TRUE())
```
```
% Usul Musnah = DIVIDE([Usul Musnah], [Total Arsip])
```
Untuk `% Usul Musnah`: pilih measure-nya → tab **Measure tools** → Format **Percentage** (hasil 47,6%).

## C. Enam visual

| # | Visual (panel Visualizations) | Isian | Hasil yang diharapkan |
|---|---|---|---|
| 1 | **Card** | Fields: `Total Arsip` | 1.200 |
| 2 | **Card** | Fields: `Usul Musnah` | 571 |
| 3 | **Card** | Fields: `Perlu Dicek` | 72 |
| 4 | **Donut chart** | Legend: `status_retensi` · Values: `Total Arsip` | 5 potongan |
| 5 | **Clustered bar chart** | Y-axis: `unit_pencipta` · X-axis: `Total Arsip` · Legend: `status_retensi` | Kepegawaian paling panjang |
| 6 | **Clustered column chart** | X-axis: `tahun` (Don't summarize) · Y-axis: `Total Arsip` | Tren 2015–2025 |

Tambahan:
- **Slicer**: field `unit_pencipta`, lalu satu slicer lagi untuk `media`. Klik Kepegawaian: card Usul Musnah menjadi 264.
- **Table**: kolom `no_arsip`, `judul`, `unit_pencipta`, `tanggal_arsip`, `akhir_inaktif`. Panel **Filters → Filters on this visual → status_retensi** → centang hanya **Usul Musnah**.
- Judul halaman: **Insert → Text box** → "Dashboard Usul Musnah Arsip Fakultas · per 31 Desember 2026".

## D. Simpan dan perbarui

- **File → Save as** → `output/dashboard_usul_musnah.pbix`.
- Bila data berubah: jalankan ulang skrip Python, lalu di Power BI klik **Home → Refresh**. Dashboard langsung mengambil data terbaru dari PostgreSQL.
