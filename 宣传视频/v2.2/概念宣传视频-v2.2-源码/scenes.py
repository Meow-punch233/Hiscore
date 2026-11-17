# -*- coding: utf-8 -*-
"""哈绩咪宣传视频 · 场景表（按合成定稿分镜逐帧实现）
场景 1 深夜的 Excel → 2 双击就能用 → 3 粘贴就导入 → 4 自动算分 →
5 重点关注名单 → 6 学生诊断页 → 7 班级对比 → 8 你的数据你做主 → 9 落版
总长 73s @30fps。
"""
from engine import *

NIGHT = (28, 32, 56)          # #1c2038 深夜底
RED_PEN = (192, 57, 43)       # #c0392b
CLAY_TAG = (201, 106, 79)     # #c96a4f
RING_GRAY = (224, 213, 192)   # #e0d5c0


# ---------- 通用小件 ----------
def _fade(d, xy, s, t, t0, f, fg, bg, anchor='lt', dur=0.5):
    p = clamp01((t - t0) / dur)
    if p <= 0:
        return
    d.text(xy, s, font=f, fill=fade_color(bg, fg, p), anchor=anchor)


def _pop_y(t, t0, dur=0.4, amp=12):
    """弹入：返回 y 偏移（负=在下方）"""
    p = clamp01((t - t0) / dur)
    return int((1 - ease_out_back(p)) * amp) if p < 1 else 0


def _glow_rect(d, box, fill, alpha=60):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle(box, fill=fill + (alpha,))
    d._image.paste(ov, (0, 0), ov)


# ============================================================
# 场景 1（0–7s）深夜的 Excel
# ============================================================
def scene1(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=NIGHT)
    # 月亮
    d.ellipse((892, 32, 924, 64), fill=(255, 244, 214))
    d.ellipse((884, 26, 912, 54), fill=NIGHT)
    # 台灯光晕
    lamp_on = not (4.3 <= t < 4.5)   # 闪烁一次
    if lamp_on:
        glow(img, 850, 430, 130, (223, 181, 112), 70)
    # 台灯
    d.polygon([(820, 400), (880, 400), (895, 445), (805, 445)], fill=PAL['tan'], outline=(120, 90, 40))
    d.rectangle((842, 445, 858, 500), fill=(120, 90, 40))
    d.rectangle((825, 500, 875, 512), fill=(90, 66, 30))
    # 挂钟（24x24，21:30 → 22:10 跳变）
    cx, cy = 60, 52
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=PAL['paper'], outline=(90, 100, 130), width=3)
    if t < 5.5:   # 21:30
        d.line((cx, cy, cx - 7, cy + 3), fill=NIGHT, width=3)   # 时针
        d.line((cx, cy, cx, cy + 11), fill=NIGHT, width=2)      # 分针
    else:          # 22:10
        d.line((cx, cy, cx - 3, cy - 8), fill=NIGHT, width=3)
        d.line((cx, cy, cx + 9, cy - 4), fill=NIGHT, width=2)

    # Excel mock 表格
    tx, ty, tw, th = 200, 110, 560, 300
    d.rectangle((tx, ty, tx + tw, ty + th), fill=(245, 245, 240), outline=(150, 150, 150), width=2)
    cols = ['语文', '数学', '英语', '总分', '排名']
    cw = tw / 5
    scroll_i = int(t / 0.2)
    frac = (t / 0.2) % 1
    row_h = 33
    for ri in range(-1, 9):
        y = ty + 34 + ri * row_h - frac * row_h
        if y < ty + 34 - row_h or y > ty + th:
            continue
        if (ri + scroll_i) % 2 == 0:
            d.rectangle((tx + 2, y, tx + tw - 2, y + row_h), fill=(232, 232, 226))
        for ci in range(5):
            v = int(37 + hash01(ri + scroll_i, ci, 5) * 61)
            s = str(v) if ci < 3 else (str(v * 3) if ci == 3 else str(v + 30))
            d.text((tx + cw * ci + cw / 2, y + row_h / 2), s, font=font(15),
                   fill=(60, 60, 60), anchor='mm')
        d.line((tx, y + row_h, tx + tw, y + row_h), fill=(200, 200, 195), width=1)
    for ci in range(1, 5):
        d.line((tx + cw * ci, ty, tx + cw * ci, ty + th), fill=(200, 200, 195), width=1)
    # 表头最后画，滚动行不遮挡
    d.rectangle((tx, ty, tx + tw, ty + 34), fill=(70, 120, 80))
    for ci, c in enumerate(cols):
        d.text((tx + cw * ci + cw / 2, ty + 17), c, font=font(14), fill=PAL['white'], anchor='mm')

    # 教师剪影 + 哈绩咪（2s 起）
    if t >= 2:
        dy = 4 if (2 <= t < 2.4) else 0   # 低头叹气
        sx, sy = 85, 388 + dy
        d.rectangle((sx - 10, sy + 30, sx + 10, sy + 78), fill=(44, 74, 82))   # 身体
        d.ellipse((sx - 13, sy, sx + 13, sy + 26), fill=(44, 74, 82))          # 头
        d.line((sx + 8, sy + 45, sx + 30, sy + 30), fill=(44, 74, 82), width=6)  # 手臂
        d.line((sx + 28, sy + 28, sx + 38, sy + 18), fill=RED_PEN, width=4)      # 红笔
        mascot_draw(img, 185, 462, 96, t, tired=(2 <= t < 4), bob=False)
        # 「…」气泡
        if 2 <= t < 4:
            bx, by = 148, 372
            d.rounded_rectangle((bx, by, bx + 46, by + 26), radius=8, fill=PAL['paper'])
            for k in range(3):
                if (t * 1.25) % 1 > k * 0.25:
                    d.rectangle((bx + 10 + k * 10, by + 11, bx + 15 + k * 10, by + 16), fill=NIGHT)

    # 数字溢出飘落（4–5.5s）
    if 4 <= t < 5.5:
        for k in range(16):
            sp = (t - 4 - k * 0.06) * 90
            if sp < 0:
                continue
            px = 220 + hash01(k, 0, 9) * 500 - sp * 0.3
            py = 130 + sp
            if py < 540:
                d.rectangle((px, py, px + 4, py + 4), fill=(180, 200, 180))

    # 烦躁抖动（5.5–7s，每 0.5s 两帧）
    if t >= 5.5 and int((t - 5.5) / 0.5) != int((t - 5.5 - 0.07) / 0.5):
        shake(img, 2, -2, NIGHT)
        d = ImageDraw.Draw(img)

    # 文案（浅色）
    _fade(d, (W / 2, 452), '月考出分的晚上', t, 0.5, font(32, 'Bold'), PAL['paper'], NIGHT, anchor='mm')
    _fade(d, (W / 2, 494), 'Excel 拉到手软，算分算到头大', t, 1.5, font(32, 'Bold'), PAL['paper'], NIGHT, anchor='mm')

    # 入场暗绿罩 0–0.5s
    if t < 0.5:
        img.paste(Image.new('RGB', (W, H), PAL['ink']), (0, 0),
                  Image.eval(Image.new('L', (W, H), int(255 * (1 - t / 0.5))), lambda x: x))
        d = ImageDraw.Draw(img)
    # 出场白闪（最后 2 帧）
    if t >= 6.93:
        d.rectangle((0, 0, W, H), fill=PAL['paper'])


# ============================================================
# 场景 2（7–13s）双击就能用
# ============================================================
def scene2(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    # 文件图标弹入（0–1.5s）
    oy = _pop_y(t, 0.0, 0.6, 40)
    if 0.6 <= t < 0.8:
        oy += 4
    cx, cy = 480, 250 + oy
    scale_up = clamp01((t - 3.5) / 0.8)   # 3.5–4.3s 放大
    if scale_up <= 0:
        file_icon(d, cx, cy, 48)
        d.text((480, cy + 58), 'Hiscore_v2.2.html', font=font(13), fill=PAL['sage'], anchor='mm')
    else:
        if scale_up < 0.55:
            s = int(48 + ease_in_out(scale_up) * 700)
            file_icon(d, 480, 260, min(s, 700))
        if scale_up >= 0.55:
            # 渐变成浏览器窗口
            a = clamp01((scale_up - 0.55) / 0.45)
            browser_frame(d, (int(lerp(340, 20, a)), int(lerp(180, 40, a)),
                              int(lerp(620, 940, a)), int(lerp(340, 520, a))),
                          'Hiscore_v2.2.html')
    # 光点扩散（1.5–3.5s）
    for wave in range(2):
        wt = t - 1.5 - wave * 1.0
        if 0 <= wt < 1.0:
            for k in range(12):
                ang = k * math.pi / 6
                r = lerp(40, 120, wt)
                gx, gy = 480 + math.cos(ang) * r, 250 + math.sin(ang) * r
                d.rectangle((gx, gy, gx + 4, gy + 4), fill=fade_color(PAL['paper'], PAL['green_bright'], 1 - wt))
    # 手形光标（1.5–3.5s）+ 双击（3.0 / 3.3s）
    if t >= 1.5 and scale_up <= 0:
        hp = clamp01((t - 1.5) / 0.5)
        hx = lerp(860, 520, ease_out_cubic(hp))
        hy = lerp(500, 290, ease_out_cubic(hp))
        click = (3.0 <= t < 3.15) or (3.3 <= t < 3.45)
        hand_cursor(d, hx, hy, 1.0, click)
        for tt in (3.0, 3.3):
            if tt <= t < tt + 0.2:
                fade = 1 - (t - tt) / 0.2
                for k in range(4):
                    ang = k * math.pi / 2 + 0.4
                    x1, y1 = 480 + math.cos(ang) * 12, 250 + math.sin(ang) * 12
                    x2, y2 = 480 + math.cos(ang) * 22, 250 + math.sin(ang) * 22
                    d.line((x1, y1, x2, y2), fill=fade_color(PAL['paper'], PAL['tan'], fade), width=3)
    # 双击回弹
    if (3.0 <= t < 3.15) or (3.3 <= t < 3.45):
        pass  # 缩放含在上面
    # 文案
    _fade(d, (W / 2, 436), '不用安装、不用联网', t, 0.5, font(32, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')
    _fade(d, (W / 2, 478), '一个 HTML 文件，双击就能用', t, 1.5, font(32, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')


# ============================================================
# 场景 3（13–21s）粘贴就导入
# ============================================================
def scene3(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    browser_frame(d, (20, 30, 940, 520), 'Hiscore_v2.2.html')
    # 文案（避开浏览器标题栏）
    _fade(d, (W / 2, 86), 'Excel / WPS 里复制，粘贴进来', t, 0.2, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')
    _fade(d, (W / 2, 118), '模板 → 预览 → 确认，三步搞定', t, 0.8, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')

    # 左侧 WPS 表格
    lx, ly, lw, lh = 40, 150, 300, 220
    panel(d, (lx, ly, lx + lw, ly + lh), PAL['white'], PAL['sage'], 2, shadow=False)
    d.rectangle((lx, ly, lx + lw, ly + 26), fill=PAL['sage'])
    names = ['林晓', '周航', '李明', '王芳', '张宇', '陈雨', '赵一', '孙琪']
    d.text((lx + lw / 2, ly + 13), '成绩表.xlsx', font=font(12), fill=PAL['white'], anchor='mm')
    for i, nm in enumerate(names):
        ry = ly + 26 + i * 24
        d.text((lx + 40, ry + 12), nm, font=font(13), fill=PAL['ink'], anchor='mm')
        for ci in range(3):
            d.text((lx + 120 + ci * 58, ry + 12), str(int(70 + hash01(i, ci, 3) * 30)),
                   font=font(13), fill=(90, 90, 90), anchor='mm')
        d.line((lx, ry + 24, lx + lw, ry + 24), fill=PAL['sage_pale'], width=1)
    # 选区高亮扫描（0–2s）
    if 0 <= t < 2:
        sy = ly + 26 + clamp01(t / 0.6) * 192
        _glow_rect(d, (lx + 8, ly + 26, lx + lw - 8, min(sy, ly + 218)), PAL['tan'], 90)
        if 1.2 <= t < 1.8 and int(t / 0.15) % 2 == 0:
            d.rectangle((lx + 8, ly + 26, lx + lw - 8, ly + 218), outline=PAL['white'], width=2)
    # 复制按钮
    b_press = 2 if (1.8 <= t < 2.1) else 0
    button(d, (lx + 90, ly + lh + 14 + b_press, lx + 210, ly + lh + 44 + b_press), '复制', font(16))
    if t >= 1.8:
        hand_cursor(d, lx + 215, ly + lh + 48, 0.8, click=(1.8 <= t < 2.1))

    # 右侧导入面板
    px0, py0, px1, py1 = 500, 130, 900, 430
    panel(d, (px0, py0, px1, py1), PAL['white'], PAL['tan'], 2)
    d.rectangle((px0, py0, px1, py0 + 28), fill=PAL['tan'])
    d.text(((px0 + px1) / 2, py0 + 14), '导入成绩', font=font(14, 'Bold'), fill=PAL['ink'], anchor='mm')
    # 粘贴输入框
    ib = (px0 + 20, py0 + 40, px1 - 20, py0 + 96)
    flash = int(t / 0.25) % 2 == 0 if 4 <= t < 4.5 else False
    d.rectangle(ib, fill=PAL['paper2'], outline=PAL['green_bright'] if flash else PAL['sage_pale'], width=2)
    d.text((ib[0] + 12, (ib[1] + ib[3]) / 2), '粘贴成绩数据…', font=font(14), fill=PAL['sage'], anchor='lm')
    # 飞入数据块（2–4s）
    for k in range(12):
        st = 2 + k * 0.1
        if st <= t < st + 0.6:
            q = ease_out_cubic((t - st) / 0.6)
            x = lerp(lx + lw / 2, ib[0] + 60 + k * 22, q)
            y = lerp(ly + 120, (ib[1] + ib[3]) / 2, q) - math.sin(q * math.pi) * 80
            c = PAL['green_bright'] if k % 2 == 0 else PAL['tan']
            d.rectangle((x, y, x + 8, y + 8), fill=c)
    # 3 张步骤卡
    steps = ['① 模板', '② 预览', '③ 确认']
    for si, s in enumerate(steps):
        st = 4 + si * 0.6
        on = t >= st + 0.3
        border = PAL['green_bright'] if on else PAL['sage_pale']
        card = (px0 + 20, py0 + 112 + si * 68, px1 - 20, py0 + 112 + si * 68 + 56)
        if st <= t < st + 0.15:
            d.rectangle(card, fill=PAL['cream'], outline=border, width=2)
        else:
            d.rectangle(card, fill=PAL['white'], outline=border, width=2)
        d.text((card[0] + 16, (card[1] + card[3]) / 2), s, font=font(18, 'Bold'),
               fill=PAL['ink'] if on else PAL['sage'], anchor='lm')
        if on:
            check(d, card[2] - 26, (card[1] + card[3]) / 2, 8, PAL['green_bright'], 3)
    # 确认导入按钮（6.5–8s）
    bp = 2 if (6.7 <= t < 7.0) else 0
    button(d, (620, 452 + bp, 780, 492 + bp), '确认导入', font(18))
    if 7.0 <= t < 7.12:
        _glow_rect(d, (20, 30, 940, 520), PAL['white'], 140)   # 全窗白闪 2 帧
    if t >= 7.0:
        check(d, 652, 508, 9, PAL['green_bright'], 4)
        d.text((672, 508), '导入成功', font=font(15, 'Bold'), fill=PAL['green'], anchor='lm')


# ============================================================
# 场景 4（21–30s）自动算分
# ============================================================
STUDENTS = [
    ('林晓', 108, 122, 119, 88, 91, 85, 613, 47),
    ('周航', 115, 108, 125, 82, 86, 90, 606, 52),
    ('李明', 102, 95, 110, 79, 84, 88, 558, 128),
    ('王芳', 121, 117, 128, 85, 89, 92, 632, 31),
    ('张宇', 98, 125, 105, 91, 88, 79, 586, 84),
    ('陈雨', 112, 101, 132, 76, 82, 94, 597, 68),
]
FEN = [82, 79, 84, 88, 76, 81]   # 赋分列翻牌值


def scene4(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    d.rectangle((0, 0, W, 40), fill=PAL['ink'])
    _fade(d, (W / 2, 52), '总分、赋分、一本二本上线率', t, 0.3, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')
    _fade(d, (W / 2, 84), '自动算好，讲评心里有数', t, 0.8, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')

    # 750 分刻度条
    sx0, sx1, sy = 200, 760, 126
    d.rectangle((sx0, sy, sx1, sy + 10), fill=PAL['cream'], outline=PAL['sage_pale'])
    fill_w = (sx1 - sx0) * (620 / 750) * ease_in_out(clamp01(t / 1.2))
    d.rectangle((sx0 + 2, sy + 2, sx0 + 2 + fill_w, sy + 8), fill=PAL['green_bright'])
    d.text((sx1 + 8, sy + 5), '新高考 750 分制', font=font(11), fill=PAL['sage'], anchor='lm')
    if t >= 1.2:
        for val, lab, c, dy in [(521, '一本线', PAL['green'], -18), (448, '二本线', PAL['tan'], 24)]:
            mx = sx0 + (sx1 - sx0) * (val / 750)
            q = ease_out_back(clamp01((t - 1.2) / 0.3))
            d.rectangle((mx - 2, sy - 6, mx + 2, sy + 16), fill=c)
            d.text((mx, sy + dy * q), f'{lab} {val}', font=font(11), fill=c, anchor='mm')

    # 成绩表
    headers = ['姓名', '语文', '数学', '英语', '物理', '化学', '政治', '赋分', '总分', '排名']
    tx, ty = 40, 150
    colw = 70
    d.rectangle((tx, ty, tx + colw * 10, ty + 30), fill=PAL['sage'])
    for ci, h in enumerate(headers):
        hc = PAL['clay'] if (ci == 7 and 3.0 <= t < 3.6) else PAL['sage']
        if ci == 7:
            d.rectangle((tx + colw * ci, ty, tx + colw * (ci + 1), ty + 30), fill=hc)
        d.text((tx + colw * ci + colw / 2, ty + 15), h, font=font(13, 'Bold'), fill=PAL['white'], anchor='mm')
    for ri, stu in enumerate(STUDENTS):
        st = 0.2 + ri * 0.35   # 每 0.35s 一行
        if t < st:
            continue
        slide = (1 - ease_out_cubic(clamp01((t - st) / 0.4))) * 60
        ry = ty + 30 + ri * 36
        if (ri % 2) == 0:
            d.rectangle((tx, ry + slide * 0, tx + colw * 10, ry + 36), fill=PAL['paper2'])
        if t < st + 0.2:
            _glow_rect(d, (tx, ry, tx + colw * 10, ry + 36), PAL['green_bright'], 55)
        name, *nums = stu
        d.text((tx + colw / 2, ry + 18), name, font=font(14), fill=PAL['ink'], anchor='mm')
        # 赋分列（第 7 列）翻牌
        fx = tx + colw * 7 + colw / 2
        ft = 3.0 + ri * 0.06
        fv = FEN[ri] if t >= ft else FEN[ri] - 9
        d.text((fx, ry + 18), str(fv), font=font(14), fill=PAL['clay_d'], anchor='mm')
        for ci, v in enumerate(nums):
            if ci == 6:      # 总分（第 8 列）滚动
                cx = tx + colw * 8 + colw / 2
                roll_text(d, (cx, ry + 18), 0, v, clamp01((t - st) / 0.3), font(14, 'Bold'), PAL['ink'], anchor='mm')
            elif ci == 7:    # 排名（第 9 列）
                cx = tx + colw * 9 + colw / 2
                d.text((cx, ry + 18), '年排 ' + str(v), font=font(13), fill=(70, 70, 70), anchor='mm')
            else:
                cx = tx + colw * (ci + 1) + colw / 2
                d.text((cx, ry + 18), str(v), font=font(14), fill=(70, 70, 70), anchor='mm')
        d.line((tx, ry + 36, tx + colw * 10, ry + 36), fill=PAL['sage_pale'], width=1)
    # 统计卡（5.5–9s）
    for ci, (lab, val, suf) in enumerate([('一本上线率', 42, '%'), ('二本上线率', 81, '%')]):
        st = 5.5 + ci * 0.3
        if t < st:
            continue
        q = ease_out_back(clamp01((t - st) / 0.5))
        y0 = 150 + ci * 100 + int((1 - q) * 20)
        panel(d, (756, y0, 916, y0 + 80), PAL['white'], PAL['tan'], 2)
        d.text((836, y0 + 22), lab, font=font(13), fill=PAL['sage'], anchor='mm')
        roll_text(d, (836, y0 + 55), 0, val, clamp01((t - st) / 0.5), font(28, 'Bold'), PAL['green'], suffix=suf, anchor='mm')

    # 哈绩咪探头 + 点赞（9–10s 段）
    if t >= 8.7:
        q = clamp01((t - 8.7) / 0.3)
        mascot_draw(img, 886, 500 - int(q * 20), 96, t, bob=True)
        d.polygon([(822, 430), (828, 418), (834, 430), (846, 430), (836, 438), (840, 450),
                   (828, 443), (818, 450), (822, 438)], fill=PAL['tan'])   # 竖大拇指


# ============================================================
# 场景 5（30–39s）重点关注名单
# ============================================================
def scene5(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    _fade(d, (W / 2, 48), '偏科、连续退步、一本临界，合成一人一行', t, 0.3, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')
    _fade(d, (W / 2, 84), '明天该找谁谈心，一眼就知道', t, 0.8, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')

    # 右侧面板
    panel(d, (300, 130, 920, 470), PAL['white'], PAL['ink'], 2)
    d.rectangle((300, 130, 920, 162), fill=PAL['ink'])
    d.text((318, 146), '重点关注', font=font(16, 'Bold'), fill=PAL['paper'], anchor='lm')
    rows_y = [178, 250, 322, 394]
    for ry in rows_y:
        d.rectangle((316, ry, 904, ry + 60), fill=PAL['paper2'], outline=PAL['sage_pale'], width=1)

    # 3 张标签卡（飞行合并进第一行，3.6s 后只显示行内徽章）
    tags = [('偏科', PAL['tan'], '数学 -22', 170), ('连续退步', CLAY_TAG, '退步 3 次', 250), ('一本临界', PAL['green_bright'], '差 8 分', 330)]
    for ti, (name, c, sub, ty0) in enumerate(tags):
        st = ti * 0.3
        if t < st or t >= 3.6:
            continue
        fly = clamp01((t - st) / 0.7)
        tx0 = 450 + ti * 66          # 与行内徽章同位
        tyt = 186
        x = lerp(40, tx0, ease_out_cubic(fly))
        y = lerp(ty0, tyt, ease_out_cubic(fly))
        if 2.5 <= t < 3.1:
            q = clamp01((t - 2.5) / 0.6)
            x = lerp(x, tx0, q)
            y = lerp(y, tyt, q)
        w_now = lerp(120, 58, clamp01((t - 2.5) / 0.6))
        h_now = lerp(48, 26, clamp01((t - 2.5) / 0.6))
        rebound = 4 if (st + 0.55 <= t < st + 0.75) else 0
        d.rectangle((x, y + rebound, x + w_now, y + h_now + rebound), fill=c, outline=PAL['ink'], width=2)
        f = font(13 if w_now > 80 else 11, 'Bold')
        label = name if w_now > 80 else name[:2]
        d.text((x + w_now / 2, y + h_now / 2 + rebound), label, font=f, fill=PAL['white'], anchor='mm')
        if w_now > 80:
            d.text((x + w_now / 2, y + h_now - 10 + rebound), sub, font=font(10), fill=PAL['white'], anchor='mm')
    # 合并白光
    if 3.0 <= t < 3.15:
        _glow_rect(d, (420, 180, 700, 218), PAL['white'], 160)

    # 第一行成型（3.1s 起）
    if t >= 3.1:
        ry = rows_y[0]
        d.rectangle((332, ry + 14, 364, ry + 46), fill=PAL['tan'], outline=PAL['ink'], width=2)  # 头像
        d.text((378, ry + 18), '李明', font=font(15, 'Bold'), fill=PAL['ink'], anchor='lm')
        d.text((378, ry + 46), '数学偏弱，离一本线差 8 分', font=font(12), fill=PAL['sage'], anchor='lm')
        for bi, (nm, c) in enumerate([('偏科', PAL['tan']), ('退步', CLAY_TAG), ('临界', PAL['green_bright'])]):
            pill(d, (450 + bi * 66, ry + 8, 450 + bi * 66 + 58, ry + 34), nm, c, PAL['white'], font(11))
    # 其余行（4.5s 起每 0.6s 一行）
    rest = [('王芳', '连退 3 次，问问最近状态', [('退步', CLAY_TAG)]),
            ('张宇', '差 8 分，冲一冲有希望', [('临界', PAL['green_bright'])]),
            ('陈雨', '英语拖后腿，每天补 20 分钟', [('偏科', PAL['tan'])])]
    for ri, (nm, act, bl) in enumerate(rest):
        st = 4.5 + ri * 0.6
        if t < st:
            continue
        q = ease_out_cubic(clamp01((t - st) / 0.5))
        ry = rows_y[ri + 1]
        xoff = (1 - q) * 80
        d.rectangle((332 + xoff, ry + 14, 364 + xoff, ry + 46), fill=PAL['sage_light'], outline=PAL['ink'], width=2)
        d.text((378 + xoff, ry + 18), nm, font=font(15, 'Bold'), fill=PAL['ink'], anchor='lm')
        d.text((378 + xoff, ry + 46), act, font=font(12), fill=PAL['sage'], anchor='lm')
        for bi, (bname, c) in enumerate(bl):
            pill(d, (450 + xoff + bi * 66, ry + 8, 450 + xoff + bi * 66 + 58, ry + 34), bname, c, PAL['white'], font(11))
        if t >= st + 0.5:
            pulse = 0.6 + 0.4 * abs(math.sin((t - st - 0.5) * 6)) if t < st + 1.1 else 1.0
            fc = fade_color(PAL['paper2'], PAL['green'], pulse)
            d.text((874, ry + 30), '查看详情', font=font(12, 'Bold'), fill=fc, anchor='rm')
            d.polygon([(882, ry + 24), (882, ry + 36), (892, ry + 30)], fill=fc)   # 像素三角箭头
    # 哈绩咪点头（8–9s）
    if t >= 8:
        nod = -4 if int((t - 8) * 4) % 2 == 0 else 0
        mascot_draw(img, 322, 146 + nod, 32, t, bob=False)


# ============================================================
# 场景 6（39–48s）学生诊断页
# ============================================================
def scene6(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    _fade(d, (W / 2, 48), '雷达图看偏科，复习建议直接给', t, 0.3, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')
    _fade(d, (W / 2, 84), '一键导出 PDF，家长会带着走', t, 0.8, font(28, 'Bold'), PAL['ink'], PAL['paper'], anchor='mm')

    if t < 7.5:
        # 学生身份条
        panel(d, (48, 112, 288, 160), PAL['white'], PAL['sage'], 2, shadow=False)
        d.rectangle((58, 122, 86, 150), fill=PAL['tan'], outline=PAL['ink'], width=2)
        d.text((98, 136), '李明 · 高三(2)班', font=font(15, 'Bold'), fill=PAL['ink'], anchor='lm')
        # 雷达图
        cx, cy, r = 230, 330, 105
        axes = ['语文', '数学', '英语', '物理', '化学', '政治']
        vals = [0.78, 0.42, 0.88, 0.62, 0.7, 0.66]
        if t >= 0.3:
            ring_a = clamp01((t - 0.3) / 0.3)
            # 网格（随时间淡入：用底色混合）
            gc = fade_color(PAL['paper'], RING_GRAY, ring_a)
            for ring in (0.33, 0.66, 1.0):
                pts = [(cx + math.cos(-math.pi / 2 + 2 * math.pi * i / 6) * r * ring,
                        cy + math.sin(-math.pi / 2 + 2 * math.pi * i / 6) * r * ring) for i in range(6)]
                d.polygon(pts, outline=gc)
            for i in range(6):
                a = -math.pi / 2 + 2 * math.pi * i / 6
                d.line((cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=gc, width=2)
                d.text((cx + math.cos(a) * (r + 16), cy + math.sin(a) * (r + 16)),
                       axes[i], font=font(12), fill=PAL['ink'], anchor='mm')
        # 数据多边形逐轴（0.6–2.5s，每轴 0.3s）
        pts = []
        for i in range(6):
            a = -math.pi / 2 + 2 * math.pi * i / 6
            st = 0.6 + i * 0.3
            v = vals[i] if t >= st else 0
            pts.append((cx + math.cos(a) * r * v, cy + math.sin(a) * r * v))
        if t >= 0.6:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).polygon(pts, fill=PAL['green_bright'] + (90,), outline=PAL['green'])
            img.paste(ov, (0, 0), ov)
            d = ImageDraw.Draw(img)
            for i in range(6):
                if t >= 0.6 + i * 0.3:
                    x, y = pts[i]
                    d.rectangle((x - 4, y - 4, x + 4, y + 4), fill=PAL['green_bright'])

        # 评估卡（2.5–5s）
        evs = [('数学待提升', PAL['tan']), ('英语优势', PAL['green_bright']), ('物理稳定', PAL['clay_d'])]
        for ei, (name, c) in enumerate(evs):
            st = 2.5 + ei * 0.3
            if t < st:
                continue
            q = ease_out_cubic(clamp01((t - st) / 0.5))
            x0 = 560 + int((1 - q) * 120)
            y0 = 130 + ei * 80
            panel(d, (x0, y0, x0 + 180, y0 + 60), PAL['white'], PAL['sage_pale'], 2, shadow=False)
            d.rectangle((x0, y0, x0 + 8, y0 + 60), fill=c)
            d.text((x0 + 22, y0 + 30), name, font=font(15, 'Bold'), fill=PAL['ink'], anchor='lm')
        # 复习建议卡
        if t >= 4.2:
            panel(d, (560, 372, 830, 452), PAL['white'], PAL['sage_pale'], 2, shadow=False)
            d.text((576, 392), '复习建议', font=font(13, 'Bold'), fill=PAL['green'], anchor='lm')
            w1 = 240 * ease_out_cubic(clamp01((t - 4.4) / 0.4))
            w2 = 150 * ease_out_cubic(clamp01((t - 4.8) / 0.4))
            d.rectangle((576, 410, 576 + w1, 420), fill=PAL['sage_pale'])
            d.rectangle((576, 430, 576 + w2, 440), fill=PAL['sage_pale'])

        # 导出 PDF（5–7.5s）
        if t >= 5:
            bp = 2 if (5.2 <= t < 5.5) else 0
            button(d, (700, 112 + bp, 830, 152 + bp), '导出 PDF', font(15))
            if 5 <= t < 5.5:
                hand_cursor(d, 835, 155, 0.8, click=(5.2 <= t < 5.5))
            if t >= 5.5:
                pdf_icon(d, 455, 350, 32 if t < 6.5 else 48)
                bar(d, (355, 392, 555, 414), clamp01((t - 5.5) / 1.0), PAL['green_bright'])
                if t >= 6.5:
                    check(d, 497, 350, 12, PAL['green_bright'], 4)
    else:
        # A4 打印成品（7.5–9s）
        d.rectangle((0, 0, W, H), fill=PAL['cream'])
        q = ease_out_cubic(clamp01((t - 7.5) / 0.5))
        pw, ph = int(280 * lerp(0.6, 1, q)), int(370 * lerp(0.6, 1, q))
        x0, y0 = W // 2 - pw // 2, H // 2 - ph // 2
        panel(d, (x0, y0, x0 + pw, y0 + ph), PAL['white'], PAL['sage'], 2)
        d.text((W / 2, y0 + 36), '谈话提纲', font=font(22, 'Bold'), fill=PAL['ink'], anchor='mm')
        d.line((x0 + 20, y0 + 56, x0 + pw - 20, y0 + 56), fill=PAL['green'], width=2)
        for i in range(3):
            d.rectangle((x0 + 20, y0 + 90 + i * 46, x0 + pw - 20 - i * 40, y0 + 104 + i * 46), fill=PAL['sage_pale'])
        mascot_draw(img, x0 + pw - 30, y0 + ph - 30, 48, t)


# ============================================================
# 场景 7（48–56s）班级对比
# ============================================================
def scene7(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['ink'])
    d.line((W // 2, 40, W // 2, 500), fill=PAL['paper'], width=2)
    # 横幅
    panel(d, (380, 20, 580, 56), PAL['tan'], PAL['paper'], 2, shadow=False)
    d.text((480, 38), '两班擂台', font=font(18, 'Bold'), fill=PAL['ink'], anchor='mm')
    _fade(d, (W / 2, 76), '班级擂台、选科组合对比', t, 0.3, font(28, 'Bold'), PAL['paper'], PAL['ink'], anchor='mm')
    _fade(d, (W / 2, 110), '讲评有数据，说话有底气', t, 0.8, font(28, 'Bold'), PAL['paper'], PAL['ink'], anchor='mm')

    # 班级卡
    for side, (nm, c) in enumerate([('高三(2)班', PAL['green_bright']), ('高三(5)班', PAL['tan'])]):
        x0 = 60 + side * 500
        panel(d, (x0, 140, x0 + 320, 200), PAL['paper'], c, 2, shadow=False)
        d.text((x0 + 160, 170), nm, font=font(20, 'Bold'), fill=PAL['ink'], anchor='mm')

    # 条形图（0–2.5s 长出，4.5s 后换数据重排）
    heights = [[40, 90, 130, 160, 110], [70, 120, 95, 140, 80]]
    h2 = [[110, 150, 90, 130, 60], [60, 100, 145, 85, 115]]
    for side in range(2):
        base_x = 120 + side * 500
        for bi in range(5):
            st = bi * 0.2 + side * 0.1
            grow = ease_out_cubic(clamp01((t - st) / 0.8))
            hgt = heights[side][bi] * grow
            if 4.5 <= t < 5.5:
                q = clamp01((t - 4.5 - bi * 0.08) / 0.6)
                hgt = lerp(heights[side][bi], h2[side][bi], ease_in_out(q))
            elif t >= 5.5:
                hgt = h2[side][bi]
            c = PAL['green_bright'] if side == 0 else PAL['tan']
            if 2.5 <= t < 3.5 and int((t - 2.5) * 4) % 2 == 0:
                c = PAL['white']
            bx = base_x + bi * 48
            d.rectangle((bx, 430 - hgt, bx + 32, 430), fill=c, outline=PAL['paper'])

    # 奖杯弹跳（2.5–4.5s）
    bounce = 0
    if 2.5 <= t < 3.5:
        bounce = -int(abs(math.sin((t - 2.5) * math.pi * 2)) * 18)
    trophy(d, 480, 290 + bounce, 52)
    if 3.0 <= t < 4.2:
        q = ease_out_back(clamp01((t - 3.0) / 0.3))
        pill(d, (410, 340 + int((1 - q) * 14), 550, 372 + int((1 - q) * 14)), '均分 +6.2', PAL['tan'], PAL['ink'], font(14))

    # 选科 chips（4.5–7s）
    chips = ['物化政', '物化生', '物化地', '史地政', '史生政']
    for ci, ch in enumerate(chips):
        x0 = 160 + ci * 136
        active = ci == 0 and t >= 5.2
        fill = PAL['green_bright'] if active else PAL['paper']
        fg = PAL['white'] if active else PAL['ink']
        pill(d, (x0, 448, x0 + 100, 476), ch, fill, fg, font(13))
        if active:
            d.rectangle((x0 + 14, 478, x0 + 86, 481), fill=PAL['white'])
    if 5.0 <= t < 5.5:
        hand_cursor(d, 275, 452, 0.8, click=True)

    # 班级阵列九宫格（7–8s）
    if t >= 7:
        for gi in range(9):
            gx = 820 + (gi % 3) * 26
            gy = 452 + (gi // 3) * 26
            c = [PAL['green_bright'], PAL['tan'], PAL['clay'], PAL['sage_light']][int(hash01(gi, 0, 4) * 4)]
            d.rectangle((gx, gy, gx + 20, gy + 20), fill=c, outline=PAL['paper'])


# ============================================================
# 场景 8（56–64s）你的数据你做主
# ============================================================
def scene8(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    # 文案三拍替换
    cur = '每页看什么，自己拖'
    if t >= 3.5:
        cur = '数据只存在你的电脑里'
    if t >= 6.0:
        cur = '备份一个文件带走，手机也能用'
    d.text((W / 2, 70), cur, font=font(28, 'Bold'), fill=PAL['ink'], anchor='mm')

    titles = ['定制信息板', '本地数据', '手机也能用']
    for ci in range(3):
        x0 = 40 + ci * 300
        panel(d, (x0, 160, x0 + 280, 380), PAL['white'], PAL['sage'], 2)
        d.text((x0 + 140, 182), titles[ci], font=font(14, 'Bold'), fill=PAL['green'], anchor='mm')

    # 卡 1：模块拖动（0–2.5s）
    blocks = ['成绩表', '雷达图', '提醒', '统计']
    order = [0, 1, 2, 3]
    if t >= 1.0:   # 拖动「提醒」到第 2 位
        order = [0, 2, 1, 3]
    for bi, idx in enumerate(order):
        bx = 66 + bi * 60
        by = 216
        lift = 0
        if 0.5 <= t < 1.5 and idx == 2:
            lift = -6 if t < 1.0 else 0
            q = clamp01((t - 1.0) / 0.5)
            bx = int(lerp(66 + 2 * 60, 66 + 1 * 60, ease_in_out(q)))
        d.rectangle((bx, by + lift, bx + 52, by + 44 + lift), fill=PAL['cream'], outline=PAL['sage'], width=2)
        d.text((bx + 26, by + 22 + lift), blocks[idx], font=font(11), fill=PAL['ink'], anchor='mm')
    if 0.5 <= t < 1.5:
        hand_cursor(d, 210, 250, 0.7, click=(t < 1.0))

    # 卡 2：JSON 进电脑（2.5–5.5s）
    pc_icon(d, 430, 260, 64)
    if 2.5 <= t < 3.3:
        q = ease_in_out(clamp01((t - 2.5) / 0.8))
        x = lerp(560, 430, q)
        y = lerp(330, 242, q) - math.sin(q * math.pi) * 50
        json_icon(d, int(x), int(y), 28)
    elif 3.3 <= t < 4.3:
        json_icon(d, 430, 242, 28)
        d.rectangle((446, 232, 470, 252), fill=PAL['green_bright'], outline=PAL['ink'], width=2)
        check(d, 458, 242, 6, PAL['white'], 3)
    elif t >= 4.3:
        # 反向飞到第二台电脑（错开放右下）
        q = ease_in_out(clamp01((t - 4.3) / 0.6))
        pc_icon(d, 560, 330, 44)
        x = lerp(430, 560, q)
        y = lerp(242, 312, q) - math.sin(q * math.pi) * 30
        json_icon(d, int(x), int(y), 28)
        if t >= 4.9:
            d.rectangle((576, 302, 600, 322), fill=PAL['green_bright'], outline=PAL['ink'], width=2)
            check(d, 588, 312, 6, PAL['white'], 3)
    if t >= 3.4:
        _fade(d, (430, 340), '数据只在这台电脑', t, 3.4, font(12), PAL['sage'], PAL['white'], anchor='mm')

    # 卡 3：手机（5.5–8s）
    if t >= 5.5:
        q = ease_out_cubic(clamp01((t - 5.5) / 0.4))
        pw = int(lerp(60, 80, q))
        ph = int(lerp(110, 148, q))
        phone_icon(d, 780, 282, pw, ph)
        for li in range(3):
            d.rectangle((752, 240 + li * 20, 808, 252 + li * 20), fill=PAL['white'], outline=PAL['sage_pale'])
        for ti2 in range(4):
            if t >= 5.9 + ti2 * 0.2:
                c = PAL['green_bright'] if ti2 == 0 else PAL['sage']
                d.rectangle((748 + ti2 * 18, 336, 762 + ti2 * 18, 350), fill=c)
    # 尾巴彩蛋（7.8s）
    if t >= 7.8:
        q = clamp01((t - 7.8) / 0.4)
        d.arc((830, 420, 950, 520), 200, 340, fill=(239, 157, 86), width=10)


# ============================================================
# 场景 9（64–73s）落版
# ============================================================
def scene9(img, d, t, p):
    d.rectangle((0, 0, W, H), fill=PAL['paper'])
    # 3 本书升起（0–0.6s）+ 回弹，顶面 y=250
    for bi in range(3):
        st = bi * 0.12
        q = ease_out_back(clamp01((t - st) / 0.6))
        y = int(lerp(560, 298 - bi * 24, q))
        book(d, 480, y, 120, 24, i=bi)
    # 哈绩咪（裁去素材自带书堆）落到书堆上（0.6–1.0s）
    if t >= 0.6:
        q = ease_in_out(clamp01((t - 0.6) / 0.4))
        cy = int(lerp(148, 232, q))
        blink = (t % 1.2) < 0.12
        mascot_draw(img, 480, cy, 128, t, blink=blink, bob=False, cat_only=True)
    # 品牌字（2–5s）
    if t >= 2:
        oy = _pop_y(t, 2.0, 0.4, 16)
        d.text((480, 372 + oy), '哈绩咪', font=font(48, 'Bold'), fill=PAL['ink'],
               anchor='mm', stroke_width=2, stroke_fill=PAL['tan'])
    if t >= 2.4:
        oy = _pop_y(t, 2.4, 0.3, 12)
        d.text((480, 416 + oy), 'Hiscore v2.2', font=font(28, 'Bold'), fill=PAL['green'], anchor='mm')
    if t >= 2.8:
        tag = typewriter('把出分的夜晚，还给你', t, cps=12, start=2.8)
        d.text((480, 456), tag, font=font(26, 'Bold'), fill=PAL['ink'], anchor='mm',
               stroke_width=1, stroke_fill=PAL['tan'])
    # 徽章（5–7.5s）
    for bi, name in enumerate(['单文件', '离线可用', '免安装']):
        st = 5 + bi * 0.3
        if t < st:
            continue
        oy = _pop_y(t, st, 0.3, 10)
        x0 = 330 + bi * 110
        d.rectangle((x0, 488 + oy, x0 + 90, 518 + oy), outline=PAL['green'], width=2)
        d.text((x0 + 45, 503 + oy), name, font=font(14, 'Bold'), fill=PAL['green'], anchor='mm')
    # 收尾：微降亮 + 飘光点（7.5–9s）
    if t >= 7.5:
        q = clamp01((t - 7.5) / 0.5)
        ov = Image.new('RGB', (W, H), (20, 24, 18))
        img.paste(ov, (0, 0), Image.eval(Image.new('L', (W, H), int(13 * q)), lambda x: x))
        d = ImageDraw.Draw(img)
        for k in range(5):
            fy = (560 - ((t - 7.5) * 8 + k * 110)) % 560
            fx = 100 + hash01(k, 0, 11) * 760
            d.rectangle((fx, fy, fx + 3, fy + 3), fill=PAL['tan'])


# ============================================================
SCENES = [
    {'name': '1深夜的Excel',  'dur': 7, 'draw': scene1, 'trans': 'fade'},
    {'name': '2双击就能用',    'dur': 6, 'draw': scene2, 'trans': 'cut'},
    {'name': '3粘贴就导入',    'dur': 8, 'draw': scene3, 'trans': 'pixel'},
    {'name': '4自动算分',      'dur': 9, 'draw': scene4, 'trans': 'fade'},
    {'name': '5重点关注名单',  'dur': 9, 'draw': scene5, 'trans': 'cut'},
    {'name': '6学生诊断页',    'dur': 9, 'draw': scene6, 'trans': 'pixel'},
    {'name': '7班级对比',      'dur': 8, 'draw': scene7, 'trans': 'pixel'},
    {'name': '8你的数据你做主', 'dur': 8, 'draw': scene8, 'trans': 'fade'},
    {'name': '9落版',          'dur': 9, 'draw': scene9, 'trans': 'pixel'},
]
