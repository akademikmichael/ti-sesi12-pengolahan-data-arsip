-- =====================================================================
-- SESI 12 · LANGKAH 5 · Memeriksa hasil Python di DBeaver (PostgreSQL)
-- Database : postgres   ·  Skema: sesi12   ·  Tabel: arsip, jra
-- Cara     : letakkan kursor di satu query, tekan Ctrl+Enter
-- Nama tabel ditulis lengkap (sesi12.arsip) agar tidak tertukar
-- dengan tabel arsip dari Sesi 7.
-- =====================================================================

-- Q1. Apakah semua data masuk? (harus 1200: 1236 baris mentah - 36 duplikat)
SELECT COUNT(*) AS total_arsip
FROM sesi12.arsip;

-- Q2. Rekap status retensi per 31 Desember 2026
SELECT status_retensi, COUNT(*) AS jumlah
FROM sesi12.arsip
GROUP BY status_retensi
ORDER BY jumlah DESC;

-- Q3. Usul musnah per unit pencipta: unit mana yang paling banyak?
SELECT unit_pencipta, COUNT(*) AS jumlah_usul_musnah
FROM sesi12.arsip
WHERE status_retensi = 'Usul Musnah'
GROUP BY unit_pencipta
ORDER BY jumlah_usul_musnah DESC;

-- Q4. JOIN ke tabel jra (ingat Sesi 7): rekap per klasifikasi
SELECT j.kode_klasifikasi, j.nama_klasifikasi, j.keterangan_jra,
       COUNT(a.no_arsip) AS jumlah_arsip
FROM sesi12.jra AS j
LEFT JOIN sesi12.arsip AS a
       ON a.kode_klasifikasi = j.kode_klasifikasi
GROUP BY j.kode_klasifikasi, j.nama_klasifikasi, j.keterangan_jra
ORDER BY j.kode_klasifikasi;

-- Q5. Daftar yang harus dicek manual oleh arsiparis (Sesi 11: kualitas metadata)
SELECT no_arsip, kode_klasifikasi, judul, catatan_kualitas
FROM sesi12.arsip
WHERE perlu_dicek = TRUE
ORDER BY catatan_kualitas, no_arsip;

-- Q6. Bahan berita acara: arsip KERTAS usul musnah, berapa lembar per unit?
SELECT unit_pencipta,
       COUNT(*)           AS jumlah_berkas,
       SUM(jumlah_lembar) AS total_lembar
FROM sesi12.arsip
WHERE status_retensi = 'Usul Musnah'
  AND media = 'Kertas'
GROUP BY unit_pencipta
ORDER BY total_lembar DESC;

-- Bonus. Tipe DATE memungkinkan hitung tanggal: arsip yang retensinya
-- habis dalam 12 bulan ke depan (bahan rencana usul musnah 2027)
SELECT unit_pencipta, COUNT(*) AS habis_2027
FROM sesi12.arsip
WHERE akhir_inaktif >  DATE '2026-12-31'
  AND akhir_inaktif <= DATE '2027-12-31'
GROUP BY unit_pencipta
ORDER BY habis_2027 DESC;
