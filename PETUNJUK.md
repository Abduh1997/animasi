# Video Animasi Negara (GitHub Actions)

Cara pakai: unggah semua isi folder ini ke repository GitHub, edit naskah.json, jalankan tab Actions > Buat Video,
lalu unduh video.mp4 dari bagian Artifacts.

## Karakter (di naskah.json, bagian "karakter")
- "bendera": indonesia, jepang, prancis, italia, jerman, belanda, brasil, india, meksiko, mesir, turki, polandia, korea, swedia, amerika
  (bendera lain: tulis "warna": "#RRGGBB" untuk warna polos)
- "bentuk": bulat | tinggi | gemuk
- "aksesori" (boleh lebih dari satu): peci, beret, hachimaki, kacamata, kumis, topi_koki, mahkota, bunga
- "suara": nama suara edge-tts (mis. en-US-GuyNeural, en-US-AnaNeural, en-GB-RyanNeural, en-US-JennyNeural)
  "rate": kecepatan (mis. "+10%"), "pitch": nada (mis. "+6Hz")
- "nama_tampil": teks nama di bawah karakter (opsional)
Jumlah karakter bebas (2 sampai 5 paling enak dilihat).

## Adegan (bagian "adegan")
- "karakter": siapa yang bicara, "teks": dialognya
- "bg": nama gambar latar di assets/ (atau kode warna "#RRGGBB")
- "efek": awan | bintang | sakura | konfeti (opsional, boleh digabung: "awan sakura")
- "ekspresi": {"Prancis": "marah", "Jepang": "kaget"}  -> normal | senang | kaget | marah | sedih
- "tumpang": detik (mis. 0.2) = karakter ini menyela sebelum dialog sebelumnya selesai
Jeda antar dialog sudah dibuat sangat singkat otomatis.

## Latar
Tersedia: indonesia, jepang, prancis, brasil, italia, jerman, india, belanda, meksiko, mesir, malam, angkasa, jalan.
Latar bergerak otomatis (kamera zoom dan geser pelan). Tambah latar sendiri: PNG 1080x1920 di assets/.
bikin_latar.py = skrip pembuat latar bawaan (opsional dijalankan di komputer).

## Suara rekaman sendiri (lebih natural)
Rekam tiap adegan, beri nama adegan1.mp3, adegan2.mp3, dst, taruh di assets/suara/. Adegan tanpa rekaman memakai suara komputer.
Musik latar: taruh musik.mp3 di assets/ (otomatis dipelankan).
