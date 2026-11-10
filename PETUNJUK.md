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

## Suara natural (rekaman sendiri)
Rekam tiap adegan lewat HP (ruangan sepi, bicara ekspresif seperti pengisi suara kartun).
Beri nama berurutan: adegan1.mp3, adegan2.mp3, dst (sesuai urutan adegan di naskah.json)
lalu taruh di folder assets/suara/. Adegan tanpa rekaman otomatis memakai suara komputer.
Format mp3, wav, m4a, atau ogg boleh. Boleh dicampur: sebagian rekaman, sebagian suara komputer.

## Latar (background)
Di naskah.json, isi "bg" tiap adegan dengan:
- kode warna, mis. "#BDE0FE"  -> latar warna polos
- nama file gambar di folder assets/, mis. "malam.png" -> gambar latar
Gambar paling bagus berukuran 1080x1920 (vertikal); ukuran lain akan dipotong di tengah.
Sudah disediakan: malam.png, angkasa.png, jalan.png.
Buat latar sendiri: Canva (ukuran custom 1080x1920) lalu Download PNG, taruh di assets/.
