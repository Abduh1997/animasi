# Cara pakai (tanpa memasang apa pun di laptop)

1. Buat akun di github.com, lalu buat repository baru (boleh Private).
2. Klik "Add file > Upload files", unggah SEMUA isi folder ini
   (termasuk folder `.github`). Kalau folder tersembunyi tidak ikut ter-upload,
   buat manual file `.github/workflows/buat-video.yml` lewat "Add file > Create new file".
3. Edit `naskah.json` langsung di GitHub (ikon pensil) -> Commit.
4. Buka tab **Actions** -> "Buat Video" -> tunggu hijau (beberapa menit).
5. Klik run tersebut -> bagian **Artifacts** -> unduh `video-shorts` -> ekstrak -> `video.mp4`.
6. Upload ke YouTube Shorts, atur "dibuat untuk anak-anak".

Opsional (taruh di folder `assets/`):
- `Bimo.png`, `Mila.png`  : gambar karakter sendiri (PNG transparan, nama sama dengan di naskah)
- `musik.mp3`             : musik latar bebas hak cipta
- gambar latar            : isi "bg" di naskah dengan nama file, mis. "taman.png"
Suara Indonesia: id-ID-ArdiNeural (laki-laki), id-ID-GadisNeural (perempuan).
