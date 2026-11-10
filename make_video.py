"""Naskah (naskah.json) -> video Shorts 1080x1920 lengkap suara + subtitle."""
import asyncio, json, math, subprocess, textwrap, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H, FPS, SR = 1080, 1920, 24, 44100
JEDA = 0.5                      # detik hening setelah tiap adegan
OUT = Path("output"); TMP = OUT / "tmp"; ASSETS = Path("assets")
FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Helvetica.ttc"]


def font(size):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def ffmpeg_pcm(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16)


async def tts(teks, suara, path):
    await edge_tts.Communicate(teks, suara).save(str(path))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def bikin_bg(spec):
    if spec.startswith("#"):
        return Image.new("RGB", (W, H), hex_rgb(spec))
    im = Image.open(ASSETS / spec).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)))
    return im.crop(((im.width - W) // 2, (im.height - H) // 2,
                    (im.width - W) // 2 + W, (im.height - H) // 2 + H))


def gambar_karakter(img, d, nama, info, bicara, amp, t, idx):
    cx = int(W * (0.27 if info.get("posisi", "kiri") == "kiri" else 0.73))
    dasar = 1150
    bob = math.sin(t * 3 + idx) * 12 - (amp * 25 if bicara else 0)
    y = int(dasar + bob)
    warna = hex_rgb(info["warna"])
    custom = ASSETS / f"{nama}.png"
    if custom.exists():                       # pakai gambar sendiri
        im = Image.open(custom).convert("RGBA")
        img.paste(im, (cx - im.width // 2, y - im.height), im)
        mx, my = cx + info.get("mulut", [0, -150])[0], y + info.get("mulut", [0, -150])[1]
    else:                                     # karakter bawaan (placeholder)
        d.rounded_rectangle((cx - 150, y - 60, cx + 150, y + 330), 80, fill=warna)
        d.ellipse((cx - 190, y - 440, cx + 190, y - 60), fill=warna)
        for ex in (-85, 85):
            if (t + idx) % 3.2 < 0.15:        # berkedip
                d.line((cx + ex - 40, y - 270, cx + ex + 40, y - 270), fill="black", width=8)
            else:
                d.ellipse((cx + ex - 45, y - 310, cx + ex + 45, y - 220), fill="white")
                d.ellipse((cx + ex - 20, y - 285, cx + ex + 20, y - 245), fill="black")
        d.ellipse((cx - 160, y - 190, cx - 110, y - 150), fill=(255, 150, 150))
        d.ellipse((cx + 110, y - 190, cx + 160, y - 150), fill=(255, 150, 150))
        mx, my = cx, y - 130
    if bicara:                                # mulut mengikuti volume suara
        tinggi = int(10 + amp * 80)
        d.ellipse((mx - 45, my - tinggi // 2, mx + 45, my + tinggi // 2), fill=(120, 20, 40))
    else:
        d.arc((mx - 45, my - 30, mx + 45, my + 20), 20, 160, fill=(120, 20, 40), width=8)
    f = font(48)
    d.text((cx, y + 380), nama, font=f, fill="white", anchor="mm", stroke_width=4, stroke_fill="black")


def subtitle(d, teks):
    f = font(64)
    baris = textwrap.wrap(teks, 24)
    y0 = 1500
    d.rounded_rectangle((60, y0 - 40, W - 60, y0 + 90 * len(baris) + 20), 40, fill=(0, 0, 0))
    for i, b in enumerate(baris):
        d.text((W // 2, y0 + 45 + i * 90), b, font=f, fill="white", anchor="mm")


def main():
    data = json.load(open("naskah.json", encoding="utf-8"))
    karakter = data["karakter"]; adegan = data["adegan"]
    TMP.mkdir(parents=True, exist_ok=True)

    # 1) suara tiap adegan
    pcm_adegan = []
    for i, ad in enumerate(adegan):
        mp3 = TMP / f"s{i}.mp3"
        asyncio.run(tts(ad["teks"], karakter[ad["karakter"]]["suara"], mp3))
        pcm = ffmpeg_pcm(mp3)
        pcm_adegan.append(np.concatenate([pcm, np.zeros(int(JEDA * SR), dtype=np.int16)]))

    # 2) gabung audio (+ musik latar opsional assets/musik.mp3)
    audio = np.concatenate(pcm_adegan)
    musik = ASSETS / "musik.mp3"
    if musik.exists():
        m = ffmpeg_pcm(musik)
        m = np.tile(m, len(audio) // len(m) + 1)[:len(audio)]
        audio = np.clip(audio.astype(np.int32) + (m * 0.12).astype(np.int32), -32768, 32767).astype(np.int16)
    wav = TMP / "audio.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio.tobytes())

    # 3) gambar frame -> ffmpeg
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(OUT / "video.mp4")], stdin=subprocess.PIPE)
    frame_global = 0
    for ad, pcm in zip(adegan, pcm_adegan):
        bg = bikin_bg(ad["bg"])
        n = math.ceil(len(pcm) / SR * FPS)
        per = SR // FPS
        for k in range(n):
            seg = pcm[k * per:(k + 1) * per].astype(np.float32)
            amp = float(min(1.0, np.sqrt(np.mean(seg ** 2)) / 6000)) if len(seg) else 0.0
            t = frame_global / FPS
            img = bg.copy(); d = ImageDraw.Draw(img)
            d.text((W // 2, 130), data.get("judul", ""), font=font(70), fill="white",
                   anchor="mm", stroke_width=5, stroke_fill="black")
            for idx, (nama, info) in enumerate(karakter.items()):
                gambar_karakter(img, d, nama, info, nama == ad["karakter"], amp, t, idx)
            subtitle(d, ad["teks"])
            proc.stdin.write(img.tobytes())
            frame_global += 1
    proc.stdin.close(); proc.wait()
    print("Selesai:", OUT / "video.mp4")


if __name__ == "__main__":
    main()
