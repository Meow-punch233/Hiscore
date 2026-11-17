# -*- coding: utf-8 -*-
"""哈绩咪 Hiscore 宣传视频 · 渲染引擎
调色板 / 字体 / 缓动 / 像素组件，全部在 960x540 画布绘制，输出时 2x 最近邻放大到 1080p。
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540
FPS = 30

# ---------- 调色板（取自 Hiscore_v2.2 界面色） ----------
PAL = {
    'paper':       (255, 250, 240),   # #fffaf0 暖纸
    'paper2':      (255, 249, 233),   # #fff9e9
    'ink':         (24,  62,  53),    # #183e35 森林绿（主文字）
    'green':       (62, 124,  79),    # #3E7C4F 品牌绿
    'green_bright':(12, 163,  12),    # #0ca30c 亮绿
    'sage':        (114, 128, 108),   # #72806c 灰绿
    'sage_light':  (179, 205, 160),   # #b3cda0 浅绿
    'sage_pale':   (203, 212, 194),   # #cbd4c2
    'tan':         (223, 181, 112),   # #dfb570 暖棕
    'clay':        (227, 160, 139),   # #e3a08b 陶土
    'clay_d':      (209, 138, 117),   # #d18a75
    'cream':       (240, 238, 220),   # #f0eedc
    'white':       (255, 255, 255),
    'shadow':      (224, 216, 198),
}

# ---------- 字体 ----------
_fonts = {}
TTC = '/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc'


def font(size, weight='Regular'):
    """weight: Regular / Medium / Bold"""
    key = (size, weight)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(TTC % weight, size, index=2)  # SC
    return _fonts[key]


# ---------- 数学与缓动 ----------
def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def ease_out_back(t):
    """轻微回弹，适合卡片弹出"""
    t = clamp01(t)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def stepped(t, hz=8):
    """把连续时间量化成低帧率（精灵动画感）"""
    return math.floor(t * hz) / hz


def hash01(x, y, seed=0):
    """稳定的伪随机 0~1（像素溶解转场用）"""
    h = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


# ---------- 文字 ----------
def text_size(d, s, f):
    box = d.textbbox((0, 0), s, font=f)
    return box[2] - box[0], box[3] - box[1]


def draw_text(d, xy, s, f, fill, shadow=None, shadow_off=(3, 3), anchor='lt'):
    """anchor: PIL 的锚点字符串，常用 lt / mt / mm"""
    x, y = xy
    if shadow:
        d.text((x + shadow_off[0], y + shadow_off[1]), s, font=f, fill=shadow, anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def typewriter(s, t, cps=12, start=0.0):
    """打字机效果，返回当前应显示的文字"""
    n = int((t - start) * cps)
    return s[:max(0, n)]


# ---------- 像素组件 ----------
def panel(d, box, fill=PAL['white'], border=PAL['ink'], border_w=2, shadow=True):
    """方角面板 + 像素投影（右下 4px）"""
    x0, y0, x1, y1 = box
    if shadow:
        d.rectangle((x0 + 4, y0 + 4, x1 + 4, y1 + 4), fill=PAL['shadow'])
    d.rectangle(box, fill=fill, outline=border, width=border_w)


def pill(d, box, text, fill=PAL['green'], fg=PAL['white'], f=None):
    """圆角胶囊标签（近似：两端半圆用小圆点拼）"""
    f = f or font(20, 'Bold')
    x0, y0, x1, y1 = box
    h = y1 - y0
    r = h // 2
    d.rounded_rectangle(box, radius=r, fill=fill)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.text((cx, cy), text, font=f, fill=fg, anchor='mm')


def button(d, box, text, f=None, fill=PAL['green'], fg=PAL['white']):
    f = f or font(22, 'Bold')
    x0, y0, x1, y1 = box
    d.rectangle((x0 + 3, y0 + 3, x1 + 3, y1 + 3), fill=PAL['shadow'])
    d.rectangle(box, fill=fill, outline=PAL['ink'], width=2)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=f, fill=fg, anchor='mm')


def bar(d, box, ratio, fill=PAL['green'], back=PAL['cream'], border=PAL['ink']):
    """进度条 / 得分条"""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=back, outline=border, width=2)
    inner = (x0 + 3, y0 + 3, x0 + 3 + (x1 - x0 - 6) * clamp01(ratio), y1 - 3)
    if inner[2] > inner[0]:
        d.rectangle(inner, fill=fill)


def check(d, cx, cy, s=10, color=PAL['green_bright'], w=4):
    """像素对勾"""
    d.line((cx - s, cy, cx - s // 3, cy + s // 2), fill=color, width=w)
    d.line((cx - s // 3, cy + s // 2, cx + s, cy - s), fill=color, width=w)


def cross(d, cx, cy, s=10, color=PAL['clay_d'], w=4):
    d.line((cx - s, cy - s, cx + s, cy + s), fill=color, width=w)
    d.line((cx - s, cy + s, cx + s, cy - s), fill=color, width=w)


def star(d, cx, cy, r, color=PAL['tan']):
    """简单四角星（像素风闪光）"""
    d.polygon([(cx, cy - r), (cx + r // 3, cy - r // 3), (cx + r, cy),
               (cx + r // 3, cy + r // 3), (cx, cy + r), (cx - r // 3, cy + r // 3),
               (cx - r, cy), (cx - r // 3, cy - r // 3)], fill=color)


def table_row(d, box, cells, widths, f=None, bg=PAL['white'], fg=PAL['ink'],
              highlight=None, t=1.0):
    """表格行：cells 为文字列表，widths 为列宽比例（总和<=1），t 为滑入进度"""
    f = f or font(18)
    x0, y0, x1, y1 = box
    slide = (1 - ease_out_cubic(t)) * 60
    x0 += slide
    x1 += slide
    d.rectangle((x0, y0, x1, y1), fill=bg, outline=PAL['sage_pale'], width=2)
    if highlight:
        d.rectangle((x0, y0, x0 + 6, y1), fill=highlight)
    x = x0 + 12
    for cell, wfrac in zip(cells, widths):
        d.text((x, (y0 + y1) / 2), cell, font=f, fill=fg, anchor='lm')
        x += (x1 - x0) * wfrac


def radar(d, cx, cy, r, values, color=PAL['green'], labels=None,
          base=PAL['sage_pale'], poly_alpha=200):
    """学科雷达图：values 为 0~1 列表（<=8 边）"""
    n = len(values)
    # 网格
    for ring in (0.33, 0.66, 1.0):
        pts = [(cx + math.cos(-math.pi / 2 + 2 * math.pi * i / n) * r * ring,
                cy + math.sin(-math.pi / 2 + 2 * math.pi * i / n) * r * ring)
               for i in range(n)]
        d.polygon(pts, outline=base)
    # 轴线
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        d.line((cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=base, width=2)
    # 数据多边形
    pts = [(cx + math.cos(-math.pi / 2 + 2 * math.pi * i / n) * r * clamp01(v),
            cy + math.sin(-math.pi / 2 + 2 * math.pi * i / n) * r * clamp01(v))
           for i, v in enumerate(values)]
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon(pts, fill=color + (poly_alpha,), outline=color)
    d._image.paste(overlay, (0, 0), overlay)
    # 数据点
    for x, y in pts:
        d.rectangle((x - 3, y - 3, x + 3, y + 3), fill=color)
    if labels:
        for i, lab in enumerate(labels):
            a = -math.pi / 2 + 2 * math.pi * i / n
            lx, ly = cx + math.cos(a) * (r + 18), cy + math.sin(a) * (r + 18)
            d.text((lx, ly), lab, font=font(14), fill=PAL['ink'], anchor='mm')


# ---------- 吉祥物 ----------
_MASCOT = None
MASCOT_PATH = '/mnt/usb-LEGION_PSSD_DD56419883A64-0:0-part1/产物/网页工具/哈绩咪 Hiscore/吉祥物-哈绩咪-第1版.png'


def mascot_img(size=256):
    """像素吉祥物（坐在书堆上的橙猫），整数缩放保持像素感"""
    global _MASCOT
    if _MASCOT is None:
        _MASCOT = Image.open(MASCOT_PATH).convert('RGBA')
    if size != _MASCOT.width:
        return _MASCOT.resize((size, size), Image.NEAREST)
    return _MASCOT


def draw_mascot(img, cx, cy, size=256, t=0.0):
    """放在 (cx, cy) 中心；t 用于上下浮动精灵动画（8fps 步进）"""
    sp = mascot_img(size)
    bob = -int((math.floor(t * 4) % 2)) * max(2, size // 96)
    x, y = int(cx - size / 2), int(cy - size / 2) + bob
    img.paste(sp, (x, y), sp)


# ---------- 转场：像素溶解 ----------
def pixel_dissolve(img_new, img_old, p, cell=8, seed=7):
    """p=0 全是旧画面，p=1 全是新画面；按 cell 像素块哈希揭开"""
    p = clamp01(p)
    if p <= 0:
        return img_old
    if p >= 1:
        return img_new
    out = img_old.copy()
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    for y in range(0, H, cell):
        for x in range(0, W, cell):
            if hash01(x // cell, y // cell, seed) < p:
                md.rectangle((x, y, x + cell - 1, y + cell - 1), fill=255)
    out.paste(img_new, (0, 0), mask)
    return out


def fade_to(img, color, p):
    """单色淡入盖板"""
    p = clamp01(p)
    if p <= 0:
        return img
    overlay = Image.new('RGB', (W, H), color)
    out = img.copy()
    if p >= 1:
        out.paste(overlay)
        return out
    flat = Image.blend(out.convert('RGB'), overlay, p)
    return flat


def vignette(img, strength=0.18):
    """极轻的暗角，聚焦中央"""
    import numpy as np
    arr = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    mask = np.clip((d - 0.62) / 0.8, 0, 1)[:, :, None] * strength
    arr = arr * (1 - mask)
    return Image.fromarray(arr.astype(np.uint8))


# ---------- 画布 ----------
def new_canvas():
    img = Image.new('RGB', (W, H), PAL['paper'])
    return img, ImageDraw.Draw(img)


# ---------- 像素图标组件（场景专用小件） ----------
def hand_cursor(d, x, y, s=1.0, click=False):
    """像素箭头光标，(x,y) 为箭头尖端"""
    k = 3 * s
    if click:
        x, y = x + k * 0.5, y + k * 0.5
    pts = [(x, y), (x, y + 12 * k), (x + 3 * k, y + 9 * k), (x + 5.5 * k, y + 14 * k),
           (x + 8 * k, y + 12.5 * k), (x + 5.5 * k, y + 8 * k), (x + 9 * k, y + 8 * k)]
    d.polygon(pts, fill=PAL['white'], outline=PAL['ink'])
    d.line(pts + [pts[0]], fill=PAL['ink'], width=max(2, int(k * 0.8)))


def file_icon(d, cx, cy, s=48, code=True):
    """白纸文件图标，s=宽度"""
    w, h = s, int(s * 4 / 3)
    x0, y0 = cx - w // 2, cy - h // 2
    fold = w // 4
    d.polygon([(x0, y0), (x0 + w - fold, y0), (x0 + w, y0 + fold),
               (x0 + w, y0 + h), (x0, y0 + h)], fill=PAL['white'], outline=PAL['ink'])
    d.line((x0 + w - fold, y0, x0 + w - fold, y0 + fold, x0 + w, y0 + fold),
           fill=PAL['ink'], width=2)
    if code:
        f = font(max(10, s // 4), 'Bold')
        d.text((cx, cy + h // 8), '</>', font=f, fill=PAL['green'], anchor='mm')


def browser_frame(d, box, label=''):
    """浏览器窗口框"""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=PAL['white'], outline=PAL['ink'], width=2)
    d.rectangle((x0, y0, x1, y0 + 24), fill=PAL['ink'])
    for i, c in enumerate([(220, 80, 60), (223, 181, 112), (12, 163, 12)]):
        d.rectangle((x0 + 10 + i * 16, y0 + 9, x0 + 16 + i * 16, y0 + 15), fill=c)
    if label:
        d.text(((x0 + x1) / 2 + 40, y0 + 12), label, font=font(11), fill=PAL['sage_pale'], anchor='mm')


def trophy(d, cx, cy, s=28):
    """像素奖杯"""
    g = PAL['tan']
    o = PAL['ink']
    w = s * 3 // 4
    d.rectangle((cx - w // 2, cy - s // 2, cx + w // 2, cy - s // 2 + s * 2 // 3), fill=g, outline=o)
    d.rectangle((cx - w // 6, cy + s // 6, cx + w // 6, cy + s // 2), fill=g, outline=o)
    d.rectangle((cx - w // 2, cy + s // 2, cx + w // 2, cy + s // 2 + s // 6), fill=g, outline=o)
    d.arc((cx - w, cy - s // 2, cx - w // 4, cy + s // 6), 90, 270, fill=o, width=3)
    d.arc((cx + w // 4, cy - s // 2, cx + w, cy + s // 6), 270, 90, fill=o, width=3)


def pc_icon(d, cx, cy, w=64):
    """像素台式电脑"""
    h = w * 3 // 4
    x0, y0 = cx - w // 2, cy - h // 2
    d.rectangle((x0, y0, x0 + w, y0 + h - h // 5), fill=PAL['white'], outline=PAL['ink'], width=2)
    d.rectangle((x0 + 6, y0 + 6, x0 + w - 6, y0 + h - h // 5 - 6), fill=PAL['sage_pale'])
    d.rectangle((cx - w // 6, y0 + h - h // 5, cx + w // 6, y0 + h), fill=PAL['sage'])
    d.rectangle((cx - w // 3, y0 + h, cx + w // 3, y0 + h + 6), fill=PAL['ink'])


def phone_icon(d, cx, cy, w=60, h=110):
    """像素手机"""
    x0, y0 = cx - w // 2, cy - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PAL['white'], outline=PAL['ink'], width=2)
    d.rectangle((x0 + 6, y0 + 12, x0 + w - 6, y0 + h - 24), fill=PAL['sage_pale'])
    d.rectangle((x0 + w // 2 - 6, y0 + h - 16, x0 + w // 2 + 6, y0 + h - 10), fill=PAL['sage'])


def json_icon(d, cx, cy, w=28):
    """{} JSON 文件小图标"""
    h = int(w * 1.3)
    x0, y0 = cx - w // 2, cy - h // 2
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=PAL['white'], outline=PAL['ink'], width=2)
    f = font(max(9, w // 2), 'Bold')
    d.text((cx, cy), '{ }', font=f, fill=PAL['green'], anchor='mm')


def book(d, cx, y, w=120, h=24, color=None, i=0):
    """一本书（侧视）"""
    c = color or [PAL['ink'], PAL['green'], PAL['tan']][i % 3]
    x0 = cx - w // 2
    d.rectangle((x0, y, x0 + w, y + h), fill=c, outline=PAL['ink'], width=2)
    d.rectangle((x0 + w - 8, y + 3, x0 + w - 4, y + h - 3), fill=PAL['paper'])


def pdf_icon(d, cx, cy, w=32):
    """PDF 文档图标"""
    h = int(w * 1.25)
    x0, y0 = cx - w // 2, cy - h // 2
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=PAL['white'], outline=PAL['ink'], width=2)
    d.rectangle((x0 + 3, y0 + h - h // 3, x0 + w - 3, y0 + h - 3), fill=PAL['clay'])
    f = font(max(9, w // 3), 'Bold')
    d.text((cx, y0 + h - h // 6), 'PDF', font=f, fill=PAL['white'], anchor='mm')


def glow(img, cx, cy, r, color, alpha=70):
    """同心圆光晕（台灯）"""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    steps = 5
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(alpha * (1 - i / (steps + 1)))
        od.ellipse((cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7),
                   fill=color + (a,))
    img.paste(overlay, (0, 0), overlay)


def roll_text(d, xy, v_from, v_to, p, f, fill, suffix='', anchor='lm'):
    """数字滚动文本"""
    v = v_from + (v_to - v_from) * ease_out_cubic(p)
    if isinstance(v_to, int):
        s = str(int(round(v)))
    else:
        s = f'{v:.1f}'
    d.text(xy, s + suffix, font=f, fill=fill, anchor=anchor)


def fade_color(bg, fg, p):
    """文字淡入：颜色从 bg 混到 fg"""
    p = clamp01(p)
    return tuple(int(bg[i] + (fg[i] - bg[i]) * p) for i in range(3))


def shake(img, dx, dy, bg):
    """整屏抖动（dx,dy 为 ±2 级别）"""
    if dx == 0 and dy == 0:
        return
    out = Image.new('RGB', img.size, bg)
    out.paste(img, (dx, dy))
    img.paste(out)


def mascot_draw(img, cx, cy, size=256, t=0.0, blink=False, tired=False, bob=True, cat_only=False):
    """吉祥物 + 眨眼/疲惫眼睑（用脸部底色覆盖眼睛后补画）"""
    sp = mascot_img(size).copy()
    if blink or tired:
        # 眼睛在素材 512 坐标系里的相对位置
        fx0, fy0, fx1, fy1 = 0.245, 0.325, 0.35, 0.425
        gx0, gy0, gx1, gy1 = 0.495, 0.325, 0.60, 0.425
        face = sp.getpixel((int(sp.width * 0.42), int(sp.height * 0.30)))
        face = face[:3]
        sd = ImageDraw.Draw(sp)
        for (ax0, ay0, ax1, ay1) in [(fx0, fy0, fx1, fy1), (gx0, gy0, gx1, gy1)]:
            box = (int(sp.width * ax0) - 2, int(sp.height * ay0) - 2,
                   int(sp.width * ax1) + 2, int(sp.height * ay1) + 2)
            sd.rectangle(box, fill=face)
            cy_eye = int((sp.height * ay0 + sp.height * ay1) / 2)
            sd.line((box[0] + 3, cy_eye, box[2] - 3, cy_eye), fill=(90, 110, 130), width=max(3, size // 64))
    if cat_only:
        sp = sp.crop((0, 0, sp.width, int(sp.height * 0.66)))
    off = -int((math.floor(t * 4) % 2)) * max(2, size // 96) if bob else 0
    x, y = int(cx - size / 2), int(cy - size / 2) + off
    img.paste(sp, (x, y), sp)


_MASCOT_CAT = None


def mascot_cat_img(size=128):
    """裁出猫本体（去掉素材自带的书堆），放在动画书堆上用"""
    global _MASCOT_CAT
    if _MASCOT_CAT is None:
        full = Image.open(MASCOT_PATH).convert('RGBA')
        _MASCOT_CAT = full.crop((0, 0, full.width, int(full.height * 0.66)))
    if size != _MASCOT_CAT.width:
        return _MASCOT_CAT.resize((size, int(size * _MASCOT_CAT.height / _MASCOT_CAT.width)), Image.NEAREST)
    return _MASCOT_CAT
