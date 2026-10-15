# Guppy Fish Detector — Offline Starter

Aplikasi sederhana untuk mencoba analisis gambar ikan tanpa API Key, akun Roboflow, atau dataset tambahan.

## Jalankan di Windows (VS Code)

1. Ekstrak ZIP ini.
2. Buka folder `guppy_detector_offline` di VS Code.
3. Buka Terminal → New Terminal.
4. Jalankan:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

5. Browser akan membuka aplikasi, biasanya di `http://localhost:8501`.
6. Klik Browse files dan pilih gambar guppy.

## Catatan penting

Versi ini memakai heuristik OpenCV, bukan model AI guppy yang terlatih. Tidak memerlukan API Key atau dataset, tetapi kotak deteksi hanya perkiraan dan bisa salah. Paket perlu diunduh saat instalasi pertama, jadi koneksi internet diperlukan untuk `pip install`. Setelah terpasang, aplikasi bisa dijalankan offline.
