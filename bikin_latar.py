"""Membuat semua gambar latar (1080x1920) ke folder assets/. Jalankan: python bikin_latar.py"""
import random, math
from pathlib import Path
from PIL import Image, ImageDraw
W, H = 1080, 1920
OUT = Path("assets"); OUT.mkdir(exist_ok=True)

def grad(top, bot):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))
    return im, ImageDraw.Draw(im)

def awan(d, x, y, s=1.0, c=(255, 255, 255)):
    for dx, dy, r in [(-60, 10, 50), (0, -15, 65), (65, 10, 50), (20, 20, 55)]:
        d.ellipse((x + (dx - r) * s, y + (dy - r * .7) * s, x + (dx + r) * s, y + (dy + r * .7) * s), fill=c)

def palem(d, x, y, h, lean=40):
    d.polygon([(x - 14, y), (x + 14, y), (x + lean + 8, y - h), (x + lean - 8, y - h)], fill=(120, 80, 40))
    tx, ty = x + lean, y - h
    for ang in (-160, -125, -90, -55, -20):
        a = math.radians(ang)
        d.line((tx, ty, tx + math.cos(a) * 150, ty + math.sin(a) * 90 + 50), fill=(30, 140, 60), width=26)
    d.ellipse((tx - 18, ty - 10, tx + 18, ty + 26), fill=(90, 60, 30))

def bintang(d, n, seed, ymax=1250):
    r = random.Random(seed)
    for _ in range(n):
        x, y, s = r.randint(0, W), r.randint(0, ymax), r.choice([2, 3, 4, 5])
        d.ellipse((x, y, x + s, y + s), fill=(255, 255, 230))

def bulan(d, cx, cy, r):
    d.ellipse((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40), fill=(70, 80, 125))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 244, 214))
    for dx, dy, rr in [(-.3, -.2, .18), (.25, .1, .25), (-.1, .45, .12), (.35, -.35, .1)]:
        d.ellipse((cx + dx * r - rr * r, cy + dy * r - rr * r, cx + dx * r + rr * r, cy + dy * r + rr * r), fill=(228, 220, 186))

def malam():
    im, d = grad((10, 15, 45), (40, 60, 110)); bintang(d, 120, 1); bulan(d, 790, 330, 150)
    d.ellipse((-400, 1250, W + 400, 2400), fill=(22, 60, 45)); d.ellipse((-200, 1330, W + 700, 2500), fill=(30, 80, 55)); return im

def angkasa():
    im, d = grad((5, 0, 25), (45, 10, 85)); bintang(d, 220, 2, 1400); bulan(d, 780, 420, 210)
    d.ellipse((130, 330, 270, 470), fill=(40, 120, 210)); d.ellipse((165, 360, 215, 410), fill=(70, 170, 90))
    for i in range(14):
        t0, t1 = i / 14, (i + .5) / 14
        d.line((290 + 270 * t0, 400 + 20 * t0, 290 + 270 * t1, 400 + 20 * t1), fill=(255, 255, 255), width=6)
    d.rectangle((0, 1250, W, H), fill=(30, 12, 60)); return im

def jalan():
    im, d = grad((135, 206, 250), (225, 242, 255))
    d.polygon([(0, 1000), (200, 700), (380, 960), (600, 640), (850, 960), (1080, 760), (1080, 1250), (0, 1250)], fill=(130, 150, 190))
    d.ellipse((-300, 1050, 800, 1500), fill=(90, 170, 100)); d.ellipse((400, 1100, 1500, 1550), fill=(70, 150, 90))
    d.rectangle((0, 1300, W, H), fill=(80, 85, 95))
    for x in range(40, W, 200): d.rectangle((x, 1640, x + 110, 1660), fill=(245, 245, 245))
    for tx in (90, 960):
        d.rectangle((tx - 22, 1000, tx + 22, 1300), fill=(110, 75, 40)); d.ellipse((tx - 120, 760, tx + 120, 1060), fill=(40, 140, 60))
    return im

def indonesia():
    im, d = grad((255, 170, 90), (255, 236, 180))
    d.ellipse((700, 260, 900, 460), fill=(255, 244, 200)); awan(d, 250, 330); awan(d, 820, 580, .7)
    d.polygon([(40, 1200), (500, 560), (960, 1200)], fill=(88, 110, 90))
    d.polygon([(500, 560), (545, 640), (520, 625), (500, 655), (475, 625), (455, 640)], fill=(150, 165, 150))
    for x, y, r in [(500, 520, 40), (540, 470, 50), (590, 410, 60)]: d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 200, 205))
    for i, y in enumerate(range(1150, 1920, 90)):
        d.ellipse((-300 - i * 40, y, W + 300 + i * 40, y + 260), fill=(110, 190, 70) if i % 2 == 0 else (80, 160, 60))
    palem(d, 120, 1300, 420, 40); palem(d, 960, 1280, 380, -40); return im

def jepang():
    im, d = grad((255, 205, 220), (255, 243, 236))
    d.ellipse((780, 300, 980, 500), fill=(230, 40, 60))
    d.polygon([(-80, 1200), (540, 600), (1160, 1200)], fill=(100, 120, 175))
    d.polygon([(430, 720), (540, 600), (650, 720), (610, 700), (570, 745), (540, 705), (500, 750), (470, 705)], fill=(255, 255, 255))
    d.rectangle((0, 1200, W, H), fill=(120, 180, 120))
    d.rectangle((760, 980, 790, 1250), fill=(210, 40, 40)); d.rectangle((900, 980, 930, 1250), fill=(210, 40, 40))
    d.rectangle((735, 950, 955, 985), fill=(210, 40, 40)); d.rectangle((750, 1020, 940, 1040), fill=(210, 40, 40))
    for tx in (110, 960):
        d.rectangle((tx - 18, 1050, tx + 18, 1300), fill=(100, 70, 50))
        for dx, dy, r in [(0, 980, 150), (-90, 1040, 100), (90, 1040, 100), (0, 900, 100)]:
            d.ellipse((tx + dx - r, dy - r * .8, tx + dx + r, dy + r * .8), fill=(255, 182, 200))
    return im

def prancis():
    im, d = grad((120, 190, 255), (230, 245, 255)); sky = im.getpixel((540, 1190))
    awan(d, 200, 360); awan(d, 850, 520, .8)
    c = (88, 78, 70)
    d.polygon([(390, 1250), (540, 520), (690, 1250)], fill=c)
    d.rounded_rectangle((455, 1120, 625, 1260), 70, fill=sky); d.rectangle((455, 1190, 625, 1260), fill=sky)
    d.rectangle((455, 1000, 625, 1025), fill=c); d.rectangle((495, 790, 585, 808), fill=c); d.rectangle((536, 450, 544, 530), fill=c)
    d.rectangle((0, 1250, W, H), fill=(110, 180, 110))
    d.polygon([(450, 1250), (630, 1250), (900, 1920), (180, 1920)], fill=(232, 216, 190))
    for x in range(40, W, 90): d.ellipse((x, 1300 + (x * 7) % 90, x + 26, 1326 + (x * 7) % 90), fill=((230, 60, 90), (255, 210, 60))[(x // 90) % 2])
    return im

def brasil():
    im, d = grad((110, 200, 255), (255, 238, 200)); d.ellipse((700, 230, 920, 450), fill=(255, 225, 60)); awan(d, 220, 380)
    d.ellipse((100, 760, 520, 1250), fill=(90, 115, 100)); d.ellipse((470, 880, 920, 1250), fill=(105, 130, 112))
    d.rectangle((0, 1180, W, 1380), fill=(40, 150, 210))
    for x in range(0, W, 120): d.arc((x, 1230, x + 90, 1280), 200, 340, fill=(255, 255, 255), width=5)
    d.rectangle((0, 1380, W, H), fill=(240, 220, 160)); palem(d, 120, 1450, 430, 40); palem(d, 950, 1420, 400, -40); return im

def italia():
    im, d = grad((255, 190, 120), (255, 232, 190)); d.ellipse((120, 250, 300, 430), fill=(255, 244, 210)); awan(d, 800, 380, .9)
    d.ellipse((110, 800, 970, 910), fill=(222, 190, 140)); d.rectangle((110, 850, 970, 1240), fill=(222, 190, 140))
    for y in (880, 985, 1090):
        for x in range(150, 960, 100):
            d.rectangle((x, y + 30, x + 50, y + 95), fill=(120, 85, 55)); d.ellipse((x, y, x + 50, y + 60), fill=(120, 85, 55))
    for x in (50, 1030): d.ellipse((x - 45, 780, x + 45, 1240), fill=(30, 90, 50))
    d.rectangle((0, 1240, W, H), fill=(200, 180, 150))
    for y in range(1260, H, 70): d.line((0, y, W, y), fill=(180, 160, 130), width=3)
    return im

def jerman():
    im, d = grad((150, 190, 230), (230, 240, 250)); awan(d, 220, 330); awan(d, 840, 470, .8)
    d.ellipse((-200, 1000, 1280, 1600), fill=(90, 140, 90))
    for x0, x1, top, rt in [(300, 390, 700, 520), (480, 600, 560, 340), (700, 790, 760, 590)]:
        d.rectangle((x0, top, x1, 1130), fill=(240, 238, 228))
        d.polygon([(x0 - 15, top), ((x0 + x1) // 2, rt), (x1 + 15, top)], fill=(50, 90, 150))
        for wy in range(top + 50, 1100, 110): d.rounded_rectangle(((x0 + x1) // 2 - 12, wy, (x0 + x1) // 2 + 12, wy + 45), 10, fill=(70, 80, 110))
    d.rectangle((390, 850, 700, 1130), fill=(232, 230, 220))
    for x in (60, 170, 900, 1010):
        for k in range(3): d.polygon([(x - 60 + k * 8, 1250 - k * 90), (x, 1120 - k * 90 - 40), (x + 60 - k * 8, 1250 - k * 90)], fill=(30, 100, 60))
    d.rectangle((0, 1400, W, H), fill=(80, 150, 80)); return im

def india():
    im, d = grad((255, 200, 150), (255, 240, 215)); d.rectangle((0, 1200, W, H), fill=(110, 170, 100))
    d.rectangle((180, 1120, 900, 1200), fill=(235, 230, 220)); d.rectangle((330, 880, 750, 1120), fill=(252, 248, 240))
    d.ellipse((415, 650, 665, 900), fill=(255, 252, 245)); d.rectangle((535, 590, 545, 655), fill=(210, 170, 40)); d.ellipse((530, 578, 550, 598), fill=(210, 170, 40))
    d.ellipse((345, 820, 415, 890), fill=(255, 252, 245)); d.ellipse((665, 820, 735, 890), fill=(255, 252, 245))
    d.rectangle((500, 960, 580, 1120), fill=(90, 110, 130)); d.ellipse((500, 925, 580, 995), fill=(90, 110, 130))
    for x in (215, 825):
        d.rectangle((x, 760, x + 40, 1120), fill=(252, 248, 240)); d.ellipse((x - 10, 720, x + 50, 780), fill=(255, 252, 245))
    d.polygon([(490, 1200), (590, 1200), (690, 1700), (390, 1700)], fill=(90, 170, 220))
    for x in (320, 760): d.ellipse((x - 60, 1260, x + 60, 1480), fill=(40, 110, 60))
    return im

def belanda():
    im, d = grad((130, 200, 255), (230, 245, 255)); awan(d, 250, 330); awan(d, 820, 450, .8)
    d.rectangle((0, 1160, W, H), fill=(110, 190, 90))
    def kincir(x, y, s):
        d.polygon([(x - 70 * s, y), (x + 70 * s, y), (x + 45 * s, y - 260 * s), (x - 45 * s, y - 260 * s)], fill=(240, 235, 225))
        d.polygon([(x - 55 * s, y - 260 * s), (x + 55 * s, y - 260 * s), (x, y - 340 * s)], fill=(170, 50, 40))
        hx, hy = x, y - 250 * s
        for a in (35, 125, 215, 305):
            r = math.radians(a); d.line((hx, hy, hx + 190 * s * math.cos(r), hy + 190 * s * math.sin(r)), fill=(110, 80, 50), width=int(22 * s))
        d.ellipse((hx - 18 * s, hy - 18 * s, hx + 18 * s, hy + 18 * s), fill=(80, 55, 35))
    kincir(270, 1230, 1.0); kincir(810, 1190, .8)
    cols = [(230, 50, 70), (255, 200, 40), (255, 120, 190), (170, 80, 200)]
    for row in range(8):
        for x in range(10, W, 44): d.ellipse((x, 1320 + row * 75, x + 28, 1350 + row * 75), fill=cols[row % 4])
    return im

def meksiko():
    im, d = grad((255, 150, 110), (255, 222, 150)); d.ellipse((780, 300, 960, 480), fill=(255, 235, 170))
    cs = [(230, 50, 70), (60, 170, 90), (250, 200, 40), (70, 120, 220), (230, 100, 180)]
    pts = [(x, 210 + 70 * math.sin(math.pi * x / W)) for x in range(0, W + 1, 20)]; d.line(pts, fill=(90, 60, 40), width=5)
    for k in range(14):
        x = 30 + k * 76; y = 210 + 70 * math.sin(math.pi * x / W); d.polygon([(x - 30, y), (x + 30, y), (x, y + 75)], fill=cs[k % 5])
    for i in range(5):
        w = 700 - i * 120; y = 1180 - (i + 1) * 110
        d.rectangle((540 - w / 2, y, 540 + w / 2, y + 110), fill=(205, 185, 135) if i % 2 == 0 else (190, 168, 118))
    d.polygon([(500, 1180), (580, 1180), (560, 630), (520, 630)], fill=(225, 208, 160))
    d.rectangle((480, 540, 600, 630), fill=(200, 180, 130)); d.rectangle((520, 570, 560, 630), fill=(80, 55, 40))
    d.rectangle((0, 1180, W, H), fill=(232, 205, 150))
    for x, y in ((140, 1380), (950, 1350)):
        d.rounded_rectangle((x - 25, y - 300, x + 25, y), 25, fill=(50, 140, 70))
        d.rounded_rectangle((x - 90, y - 220, x - 60, y - 110), 15, fill=(50, 140, 70)); d.rectangle((x - 90, y - 125, x - 25, y - 95), fill=(50, 140, 70))
        d.rounded_rectangle((x + 60, y - 250, x + 90, y - 140), 15, fill=(50, 140, 70)); d.rectangle((x + 25, y - 155, x + 90, y - 125), fill=(50, 140, 70))
    return im

def mesir():
    im, d = grad((255, 170, 100), (255, 230, 170)); d.ellipse((560, 280, 840, 560), fill=(255, 240, 190))
    for pts, sh in [([(-100, 1250), (130, 960), (360, 1250)], [(130, 960), (360, 1250), (160, 1250)]),
                    ([(60, 1250), (380, 780), (700, 1250)], [(380, 780), (700, 1250), (430, 1250)]),
                    ([(420, 1250), (720, 620), (1020, 1250)], [(720, 620), (1020, 1250), (760, 1250)])]:
        d.polygon(pts, fill=(222, 184, 110)); d.polygon(sh, fill=(190, 150, 85))
    d.ellipse((-300, 1200, 700, 1700), fill=(235, 200, 130)); d.ellipse((300, 1260, 1400, 1800), fill=(225, 185, 115))
    d.rectangle((0, 1600, W, H), fill=(215, 175, 105)); palem(d, 150, 1420, 380, 30); return im

for nama, f in [("malam", malam), ("angkasa", angkasa), ("jalan", jalan), ("indonesia", indonesia), ("jepang", jepang),
                ("prancis", prancis), ("brasil", brasil), ("italia", italia), ("jerman", jerman), ("india", india),
                ("belanda", belanda), ("meksiko", meksiko), ("mesir", mesir)]:
    f().save(OUT / f"{nama}.png")
print("selesai")
