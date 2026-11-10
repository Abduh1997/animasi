"""naskah.json -> video Shorts 1080x1920: karakter bendera, latar bergerak, dialog tanpa jeda."""
import asyncio, bisect, json, math, random, subprocess, textwrap, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H, FPS, SR = 1080, 1920, 24, 44100
JEDA = 0.06                       # jeda antar dialog (detik) - sangat singkat supaya natural
FEET_Y = 1440                     # garis kaki karakter
LW, LH, OX, OY = 800, 1200, 400, 700   # ukuran kanvas satu karakter & titik asalnya
OUT = Path("output"); TMP = OUT / "tmp"; ASSETS = Path("assets")
FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Helvetica.ttc"]
TINTA = (20, 20, 30, 255)
BENTUK = {   # rx, ry, cy = kepala; hw, top, bot = badan
    "bulat":  dict(rx=190, ry=190, cy=-250, hw=150, top=-70, bot=330),
    "tinggi": dict(rx=150, ry=210, cy=-300, hw=115, top=-100, bot=380),
    "gemuk":  dict(rx=215, ry=165, cy=-210, hw=200, top=-60, bot=290),
}
ALIAS = {"japan": "jepang", "france": "prancis", "italy": "italia", "germany": "jerman", "netherlands": "belanda",
         "brazil": "brasil", "mexico": "meksiko", "turkey": "turki", "poland": "polandia", "usa": "amerika",
         "egypt": "mesir", "sweden": "swedia", "korea selatan": "korea"}


def font(size):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ bendera
def bendera(nama, w, h, warna="#888888"):
    n = ALIAS.get(nama.lower(), nama.lower())
    im = Image.new("RGB", (w, h), "white"); d = ImageDraw.Draw(im)
    cx, cy = w // 2, int(h * 0.62)

    def horiz(cols):
        for i, c in enumerate(cols):
            d.rectangle((0, round(h * i / len(cols)), w, round(h * (i + 1) / len(cols))), fill=c)

    def vert(cols):
        for i, c in enumerate(cols):
            d.rectangle((round(w * i / len(cols)), 0, round(w * (i + 1) / len(cols)), h), fill=c)

    if n == "indonesia": horiz(["#E70011", "#FFFFFF"])
    elif n == "polandia": horiz(["#FFFFFF", "#DC143C"])
    elif n == "jepang": d.ellipse((cx - w * .27, cy - w * .27, cx + w * .27, cy + w * .27), fill="#BC002D")
    elif n == "prancis": vert(["#0055A4", "#FFFFFF", "#EF4135"])
    elif n == "italia": vert(["#009246", "#FFFFFF", "#CE2B37"])
    elif n == "jerman": horiz(["#000000", "#DD0000", "#FFCE00"])
    elif n == "belanda": horiz(["#AE1C28", "#FFFFFF", "#21468B"])
    elif n == "meksiko":
        vert(["#006847", "#FFFFFF", "#CE1126"]); d.ellipse((cx - w * .1, cy - w * .1, cx + w * .1, cy + w * .1), fill="#8B5A2B")
    elif n == "mesir":
        horiz(["#CE1126", "#FFFFFF", "#000000"]); d.ellipse((cx - w * .08, h * .5 - w * .08, cx + w * .08, h * .5 + w * .08), fill="#C09300")
    elif n == "india":
        horiz(["#FF9933", "#FFFFFF", "#138808"]); r = w * .13
        d.ellipse((cx - r, h * .5 - r, cx + r, h * .5 + r), outline="#000080", width=6)
        d.ellipse((cx - 8, h * .5 - 8, cx + 8, h * .5 + 8), fill="#000080")
    elif n == "brasil":
        d.rectangle((0, 0, w, h), fill="#009C3B")
        d.polygon([(w / 2, h * .38), (w * .93, h * .62), (w / 2, h * .86), (w * .07, h * .62)], fill="#FFDF00")
        d.ellipse((cx - w * .2, cy - w * .2, cx + w * .2, cy + w * .2), fill="#002776")
    elif n == "turki":
        d.rectangle((0, 0, w, h), fill="#E30A17"); d.ellipse((cx - w * .2, cy - w * .2, cx + w * .2, cy + w * .2), fill="white")
        d.ellipse((cx - w * .13, cy - w * .16, cx + w * .27, cy + w * .16), fill="#E30A17")
    elif n == "korea":
        r = w * .24
        d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill="#CD2E3A"); d.pieslice((cx - r, cy - r, cx + r, cy + r), 0, 180, fill="#0047A0")
    elif n == "swedia":
        d.rectangle((0, 0, w, h), fill="#006AA7"); d.rectangle((w * .3, 0, w * .45, h), fill="#FECC00"); d.rectangle((0, h * .45, w, h * .58), fill="#FECC00")
    elif n == "amerika":
        for i in range(13):
            d.rectangle((0, round(h * i / 13), w, round(h * (i + 1) / 13)), fill="#B22234" if i % 2 == 0 else "#FFFFFF")
        d.rectangle((0, 0, w * .5, h * .54), fill="#3C3B6E")
        for r_ in range(4):
            for c_ in range(3): d.ellipse((w * (.08 + c_ * .15), h * (.05 + r_ * .12), w * (.08 + c_ * .15) + 9, h * (.05 + r_ * .12) + 9), fill="white")
    else:
        d.rectangle((0, 0, w, h), fill=warna)
    return im


def bikin_sprite(info, b):
    """Siluet kepala+badan berwarna bendera, dengan garis tepi. Dibuat sekali saja."""
    def bentuk(dr, e):
        dr.ellipse((OX - b["rx"] - e, OY + b["cy"] - b["ry"] - e, OX + b["rx"] + e, OY + b["cy"] + b["ry"] + e), fill=255)
        dr.rounded_rectangle((OX - b["hw"] - e, OY + b["top"] - e, OX + b["hw"] + e, OY + b["bot"] + e), 70, fill=255)
    mask = Image.new("L", (LW, LH), 0); bentuk(ImageDraw.Draw(mask), 0)
    garis = Image.new("L", (LW, LH), 0); bentuk(ImageDraw.Draw(garis), 8)
    x0, x1 = -max(b["rx"], b["hw"]), max(b["rx"], b["hw"]); y0, y1 = b["cy"] - b["ry"], b["bot"]
    full = Image.new("RGB", (LW, LH), "white")
    full.paste(bendera(info.get("bendera", ""), x1 - x0, y1 - y0, info.get("warna", "#888888")), (OX + x0, OY + y0))
    sp = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    sp.paste(TINTA, mask=garis); sp.paste(full, mask=mask)
    return sp


def L(*xy):
    return tuple(v + (OX if i % 2 == 0 else OY) for i, v in enumerate(xy))


def render_karakter(info, sprite, b, bicara, amp, t, idx, ekspresi, lihat):
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    bounce = -abs(math.sin(t * 8 + idx)) * amp * 30 if bicara else math.sin(t * 2 + idx) * 6
    for sx in (-1, 1):                                            # kaki
        lx = sx * b["hw"] * .5
        d.rounded_rectangle(L(lx - 18, b["bot"] - 20, lx + 18, b["bot"] + 40), 10, fill=(60, 45, 40, 255))
        d.ellipse(L(lx - 40 + sx * 8, b["bot"] + 20, lx + 40 + sx * 8, b["bot"] + 58), fill=TINTA)
    for sx in (-1, 1):                                            # lengan
        px, py = sx * b["hw"], b["top"] + 80
        if ekspresi == "kaget": ang = 150 + math.sin(t * 14 + idx) * 8
        elif bicara and sx == (1 if idx % 2 == 0 else -1): ang = 115 + math.sin(t * 9 + idx) * 28
        else: ang = 22 + math.sin(t * 2 + idx + sx) * 6
        a = math.radians(ang); ex, ey = px + sx * math.sin(a) * 150, py + math.cos(a) * 150
        d.line(L(px, py, ex, ey), fill=TINTA, width=20)
        d.ellipse(L(ex - 30, ey - 30, ex + 30, ey + 30), fill=(255, 255, 255, 255), outline=TINTA, width=7)
    layer.paste(sprite, (0, 0), sprite)
    hcy, rx, ry = b["cy"], b["rx"], b["ry"]
    ex_, ey_, er = rx * .36, hcy - ry * .12, 36
    kedip = (t + idx * .9) % 3.4 < .14
    mult = 1.25 if ekspresi == "kaget" else (.85 if ekspresi == "marah" else 1.0)
    for sx in (-1, 1):                                            # mata + alis
        c0 = sx * ex_
        if kedip:
            d.line(L(c0 - er, ey_, c0 + er, ey_), fill=TINTA, width=9)
        else:
            e2 = er * mult
            d.ellipse(L(c0 - e2, ey_ - e2 * 1.1, c0 + e2, ey_ + e2 * 1.1), fill=(255, 255, 255, 255), outline=TINTA, width=7)
            pr = e2 * .45; pxx = c0 + lihat * e2 * .45; pyy = ey_ + e2 * .1
            d.ellipse(L(pxx - pr, pyy - pr, pxx + pr, pyy + pr), fill=TINTA)
            d.ellipse(L(pxx - pr * .6, pyy - pr * .7, pxx - pr * .1, pyy - pr * .2), fill=(255, 255, 255, 255))
        by = ey_ - er * 1.9
        o, i_ = c0 + sx * er, c0 - sx * er                         # ujung luar / dalam alis
        if ekspresi == "marah": yo, yi = by - 14, by + 14
        elif ekspresi == "sedih": yo, yi = by + 10, by - 14
        elif ekspresi == "kaget": yo, yi = by - 26, by - 26
        else: yo, yi = by + 2, by - 2
        d.line(L(o, yo, i_, yi), fill=TINTA, width=11)
    my = hcy + ry * .42                                           # mulut
    if bicara:
        mh, mw = 12 + amp * 95, 60 + amp * 40
        d.ellipse(L(-mw / 2, my - mh / 2, mw / 2, my + mh / 2), fill=(120, 20, 40, 255), outline=TINTA, width=7)
        if mh > 45: d.ellipse(L(-mw * .28, my + mh * .08, mw * .28, my + mh * .38), fill=(240, 120, 130, 255))
    elif ekspresi == "kaget": d.ellipse(L(-22, my - 8, 22, my + 48), fill=(120, 20, 40, 255), outline=TINTA, width=7)
    elif ekspresi == "sedih": d.arc(L(-50, my + 5, 50, my + 55), 200, 340, fill=TINTA, width=9)
    elif ekspresi == "marah": d.line(L(-45, my + 12, 45, my + 12), fill=TINTA, width=10)
    elif ekspresi == "senang": d.chord(L(-60, my - 25, 60, my + 45), 0, 180, fill=(120, 20, 40, 255), outline=TINTA, width=7)
    else: d.arc(L(-50, my - 35, 50, my + 25), 20, 160, fill=TINTA, width=9)
    top_y = hcy - ry
    for ak in info.get("aksesori", []):                            # aksesori
        if ak == "peci": d.rounded_rectangle(L(-rx * .62, top_y - 70, rx * .62, top_y + 35), 18, fill=(25, 25, 30, 255), outline=TINTA, width=6)
        elif ak == "beret":
            d.ellipse(L(-rx * .95, top_y - 50, rx * .75, top_y + 45), fill=(40, 60, 150, 255), outline=TINTA, width=6)
            d.ellipse(L(-rx * .12, top_y - 75, rx * .02, top_y - 45), fill=TINTA)
        elif ak == "hachimaki":
            yb = hcy - ry * .72; hw = rx * .69
            d.rounded_rectangle(L(-hw, yb - 20, hw, yb + 20), 10, fill=(255, 255, 255, 255), outline=TINTA, width=5)
            d.ellipse(L(-18, yb - 14, 18, yb + 14), fill=(188, 0, 45, 255))
            d.polygon([L(hw, yb)[0:2], L(hw + 60, yb - 30)[0:2], L(hw + 50, yb + 10)[0:2]], fill=(255, 255, 255, 255), outline=TINTA)
        elif ak == "kacamata":
            for sx in (-1, 1):
                d.rounded_rectangle(L(sx * ex_ - er * 1.45, ey_ - er * 1.1, sx * ex_ + er * 1.45, ey_ + er * 1.05), 22, fill=(15, 15, 20, 255))
                d.line(L(sx * ex_ - er, ey_ - er * .7, sx * ex_ - er * .4, ey_ - er * .7), fill=(255, 255, 255, 255), width=6)
            d.line(L(-ex_ + er * 1.4, ey_ - 10, ex_ - er * 1.4, ey_ - 10), fill=TINTA, width=8)
        elif ak == "kumis":
            d.ellipse(L(-80, my - 42, 2, my - 6), fill=(60, 35, 20, 255)); d.ellipse(L(-2, my - 42, 80, my - 6), fill=(60, 35, 20, 255))
        elif ak == "topi_koki":
            d.rounded_rectangle(L(-rx * .5, top_y - 5, rx * .5, top_y + 40), 8, fill=(255, 255, 255, 255), outline=TINTA, width=5)
            for dx in (-.4, 0, .4): d.ellipse(L(dx * rx - 60, top_y - 120, dx * rx + 60, top_y - 5), fill=(255, 255, 255, 255), outline=TINTA, width=5)
        elif ak == "mahkota":
            d.polygon([L(-100, top_y + 20)[0:2], L(-100, top_y - 70)[0:2], L(-50, top_y - 25)[0:2], L(0, top_y - 85)[0:2],
                       L(50, top_y - 25)[0:2], L(100, top_y - 70)[0:2], L(100, top_y + 20)[0:2]], fill=(255, 205, 40, 255), outline=TINTA)
        elif ak == "bunga":
            fx, fy = rx * .6, top_y + 60
            for k in range(5):
                a = math.radians(k * 72); d.ellipse(L(fx + math.cos(a) * 28 - 20, fy + math.sin(a) * 28 - 20, fx + math.cos(a) * 28 + 20, fy + math.sin(a) * 28 + 20), fill=(255, 130, 190, 255))
            d.ellipse(L(fx - 15, fy - 15, fx + 15, fy + 15), fill=(255, 220, 60, 255))
    return layer, bounce


# ------------------------------------------------------------------ latar & efek
_bgcache = {}


def bikin_bg(spec):
    if spec in _bgcache: return _bgcache[spec]
    if spec.startswith("#"):
        im = Image.new("RGB", (W, H), hex_rgb(spec))
    else:
        try:
            im = Image.open(ASSETS / spec).convert("RGB")
            s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
            im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        except FileNotFoundError:
            print("PERINGATAN: gambar latar tidak ditemukan:", spec); im = Image.new("RGB", (W, H), (90, 90, 120))
    _bgcache[spec] = im
    return im


def bg_gerak(bg, p, arah):
    z = 1.0 + .12 * (p if arah else 1 - p)
    cw, ch = W / z, H / z
    x0 = (W - cw) * (.5 + .35 * (p - .5) * 2 * (1 if arah else -1)); y0 = (H - ch) * .5
    return bg.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)


_r = random.Random(7)
BINTANG = [(_r.randint(0, W), _r.randint(80, 1100)) for _ in range(45)]
PARTIKEL = [(_r.randint(0, W), _r.randint(0, H), _r.random()) for _ in range(30)]
WARNA_K = [(255, 80, 100), (255, 210, 60), (80, 190, 255), (120, 220, 120), (200, 120, 255)]


def efek(d, jenis, t):
    if "awan" in jenis:
        for k, (y, sz, sp) in enumerate([(260, 1.0, 40), (500, .7, 25), (170, 1.3, 55)]):
            x = (t * sp + k * 430) % (W + 500) - 250
            for dx, dy, r in [(-60, 10, 50), (0, -15, 65), (65, 10, 50), (20, 20, 55)]:
                d.ellipse((x + (dx - r) * sz, y + (dy - r * .7) * sz, x + (dx + r) * sz, y + (dy + r * .7) * sz), fill=(255, 255, 255))
    if "bintang" in jenis:
        for k, (x, y) in enumerate(BINTANG):
            s = 3 + 4 * (math.sin(t * 3 + k) * .5 + .5)
            d.line((x - s, y, x + s, y), fill=(255, 255, 220), width=2); d.line((x, y - s, x, y + s), fill=(255, 255, 220), width=2)
    if "sakura" in jenis:
        for k, (x, y, r) in enumerate(PARTIKEL):
            px = x + 60 * math.sin(t * .9 + k); py = (y + t * (70 + 50 * r)) % (H + 60) - 30
            d.ellipse((px - 11, py - 7, px + 11, py + 7), fill=(255, 183, 197))
    if "konfeti" in jenis:
        for k, (x, y, r) in enumerate(PARTIKEL):
            px = x + 40 * math.sin(t * 2 + k); py = (y + t * (150 + 80 * r)) % H
            d.rectangle((px, py, px + 14, py + 8), fill=WARNA_K[k % 5])


# ------------------------------------------------------------------ suara
async def tts(teks, info, path):
    for suara in (info["suara"], "en-US-GuyNeural"):
        try:
            await edge_tts.Communicate(teks, suara, rate=info.get("rate", "+0%"), pitch=info.get("pitch", "+0Hz")).save(str(path))
            return
        except Exception as e:
            print("TTS gagal untuk", suara, "->", e)
    raise RuntimeError("TTS gagal")


def ffmpeg_pcm(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16)


def potong_hening(pcm, ambang=400):
    idx = np.where(np.abs(pcm.astype(np.int32)) > ambang)[0]
    if len(idx) == 0: return pcm
    pad = int(.03 * SR)
    return pcm[max(0, idx[0] - pad): idx[-1] + pad]


def cari_rekaman(i):
    for ext in ("mp3", "wav", "m4a", "ogg"):
        p = ASSETS / "suara" / f"adegan{i + 1}.{ext}"
        if p.exists(): return p
    return None


def subtitle(d, teks):
    f = font(60); baris = textwrap.wrap(teks, 26); y0 = 1550
    d.rounded_rectangle((50, y0 - 35, W - 50, y0 + 82 * len(baris) + 15), 40, fill=(0, 0, 0))
    for i, bs in enumerate(baris):
        d.text((W // 2, y0 + 38 + i * 82), bs, font=f, fill="white", anchor="mm")


# ------------------------------------------------------------------ utama
def main():
    data = json.load(open("naskah.json", encoding="utf-8"))
    karakter, adegan = data["karakter"], data["adegan"]
    nama_list = list(karakter.keys()); n = len(nama_list)
    TMP.mkdir(parents=True, exist_ok=True)

    pcms = []
    for i, ad in enumerate(adegan):
        rek = cari_rekaman(i)
        if rek: pcm = ffmpeg_pcm(rek)
        else:
            mp3 = TMP / f"s{i}.mp3"; asyncio.run(tts(ad["teks"], karakter[ad["karakter"]], mp3)); pcm = ffmpeg_pcm(mp3)
        pcms.append(potong_hening(pcm))

    starts, pos = [], 0
    for i, pcm in enumerate(pcms):                                 # dialog bersambung rapat; "tumpang" = saling menyela
        st = 0 if i == 0 else max(0, pos - int(adegan[i].get("tumpang", 0) * SR))
        starts.append(st); pos = st + len(pcm) + int(JEDA * SR)
    total = max(s + len(p) for s, p in zip(starts, pcms)) + int(.5 * SR)
    mix = np.zeros(total, dtype=np.int32)
    for s, p in zip(starts, pcms): mix[s:s + len(p)] += p
    musik = ASSETS / "musik.mp3"
    if musik.exists():
        m = ffmpeg_pcm(musik); m = np.tile(m, total // len(m) + 1)[:total]; mix += (m * .12).astype(np.int32)
    audio = np.clip(mix, -32768, 32767).astype(np.int16)
    wav = TMP / "audio.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio.tobytes())

    shot, shot_id = [], -1                                         # kelompok adegan berlatar sama -> kamera bergerak kontinu
    for i, ad in enumerate(adegan):
        if i == 0 or ad["bg"] != adegan[i - 1]["bg"]: shot_id += 1
        shot.append(shot_id)
    shot_t = {}
    for i, sid in enumerate(shot):
        a = starts[i]; b_ = starts[i + 1] if i + 1 < len(starts) and shot[i + 1] != sid else total
        lo, hi = shot_t.get(sid, (a, b_)); shot_t[sid] = (min(lo, a), max(hi, b_))

    bentuk = {k: BENTUK[v.get("bentuk", "bulat")] for k, v in karakter.items()}
    sprites = {k: bikin_sprite(v, bentuk[k]) for k, v in karakter.items()}
    s_dasar = min(1.0, (W / n - 24) / 410)
    cxs = {k: int(W * (j + .5) / n) for j, k in enumerate(nama_list)}
    fokus = {k: 0.0 for k in nama_list}

    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(OUT / "video.mp4")], stdin=subprocess.PIPE)
    per = SR // FPS
    for f in range(math.ceil(total / SR * FPS)):
        ts = f * SR // FPS; t = f / FPS
        i = max(0, bisect.bisect_right(starts, ts) - 1); ad = adegan[i]
        off = ts - starts[i]; seg = pcms[i][off:off + per].astype(np.float32)
        amp = float(min(1.0, np.sqrt(np.mean(seg ** 2)) / 6000)) if len(seg) else 0.0
        bicara_ = off < len(pcms[i])
        lo, hi = shot_t[shot[i]]; p = min(1.0, max(0.0, (ts - lo) / max(1, hi - lo)))
        img = bg_gerak(bikin_bg(ad["bg"]), p, shot[i] % 2 == 0); d = ImageDraw.Draw(img)
        efek(d, ad.get("efek", ""), t)
        d.text((W // 2, 120), data.get("judul", ""), font=font(56), fill="white", anchor="mm", stroke_width=5, stroke_fill="black")
        pembicara = ad["karakter"]; urut = sorted(nama_list, key=lambda k: k == pembicara)
        for k in urut:
            idx = nama_list.index(k)
            fokus[k] += ((1.0 if k == pembicara else 0.0) - fokus[k]) * .4
            lihat = 0.0 if k == pembicara else max(-1.0, min(1.0, (cxs[pembicara] - cxs[k]) / 400))
            ekspr = ad.get("ekspresi", {}).get(k, "normal")
            layer, bounce = render_karakter(karakter[k], sprites[k], bentuk[k], k == pembicara and bicara_, amp if k == pembicara else 0,
                                            t, idx, ekspr, lihat)
            tilt = math.sin(t * 6) * 3 * amp if k == pembicara else 0
            if tilt: layer = layer.rotate(tilt, resample=Image.BICUBIC, center=(OX, OY + bentuk[k]["bot"]))
            s = s_dasar * (1 + .07 * fokus[k])
            if abs(s - 1) > 1e-3: layer = layer.resize((int(LW * s), int(LH * s)), Image.BILINEAR)
            img.paste(layer, (int(cxs[k] - OX * s), int(FEET_Y - (OY + bentuk[k]["bot"] + 58) * s + bounce * s)), layer)
        for k in nama_list:
            d.text((cxs[k], FEET_Y + 28), karakter[k].get("nama_tampil", k), font=font(max(34, int(48 * s_dasar + 8))), fill="white",
                   anchor="mm", stroke_width=4, stroke_fill="black")
        subtitle(d, ad["teks"])
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    print("Selesai:", OUT / "video.mp4")


if __name__ == "__main__":
    main()
