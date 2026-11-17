# -*- coding: utf-8 -*-
"""哈绩咪宣传视频 · 芯片风 BGM 生成器
方波主旋律 + 三角波贝斯 + 噪音镲片，numpy 合成直写 WAV。
调式：C 大调，C-G-Am-F 经典循环，温和轻快，不抢画面。
"""
import math
import wave
import numpy as np

SR = 44100
BPM = 124
BEAT = 60.0 / BPM          # 一拍秒数
OUT = '/tmp/hiscore_video/bgm.wav'

# 音高（十二平均律）
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def note(name, octave):
    """如 note('A', 3) -> 220Hz"""
    midi = 12 * (octave + 1) + NAMES[name]
    return 440.0 * 2 ** ((midi - 69) / 12)


def square(freq, dur, duty=0.25, vib=0.0):
    t = np.arange(int(dur * SR)) / SR
    if vib:
        freq = freq * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * 0.01)
    phase = (t * freq) % 1.0
    return np.where(phase < duty, 1.0, -1.0)


def triangle(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    phase = (t * freq) % 1.0
    return 2 * np.abs(2 * phase - 1) - 1


def noise(dur):
    rng = np.random.RandomState(42)   # 固定种子，每次生成一致
    return rng.uniform(-1, 1, int(dur * SR))


def env_ad(sig, attack=0.01, decay=0.12, sustain=0.6, release=0.08):
    """简易 ADSR 尾巴，让音符不咔哒"""
    n = len(sig)
    a, d, r = int(attack * SR), int(decay * SR), int(release * SR)
    e = np.ones(n) * sustain
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    if d > 0 and a + d <= n:
        e[a:a + d] = np.linspace(1, sustain, d)
    if r > 0:
        e[-r:] *= np.linspace(1, 0, r)
    return sig * e


def place(buf, sig, at_sec, gain=1.0):
    i = int(at_sec * SR)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[:j - i] * gain


# ---------- 乐曲结构 ----------
# 和弦循环：C G Am F（每和弦 2 拍 = 半小节，4 和弦 = 2 小节一循环）
CHORDS = [
    ('C', ['C', 'E', 'G'], note('C', 2)),
    ('G', ['G', 'B', 'D'], note('G', 2)),
    ('A', ['A', 'C', 'E']),   # Am
    ('F', ['F', 'A', 'C'], note('F', 2)),
]
CHORDS[2] = ('Am', ['A', 'C', 'E'], note('A', 2))

# 主旋律：C 大调五声音阶动机，(音名, 八度, 拍数)
MELODY_A = [
    ('E', 4, 0.5), ('G', 4, 0.5), ('A', 4, 1.0), ('G', 4, 0.5), ('E', 4, 0.5),
    ('D', 4, 1.0), ('C', 4, 1.0), ('D', 4, 0.5), ('E', 4, 0.5), ('G', 4, 1.0),
    ('A', 4, 1.5), ('G', 4, 0.5), ('E', 4, 1.0), ('D', 4, 1.0), ('C', 4, 2.0),
]
MELODY_B = [
    ('G', 4, 0.5), ('A', 4, 0.5), ('C', 5, 1.0), ('A', 4, 0.5), ('G', 4, 0.5),
    ('E', 4, 1.0), ('D', 4, 1.0), ('E', 4, 0.5), ('G', 4, 0.5), ('A', 4, 2.0),
    ('G', 4, 0.5), ('E', 4, 0.5), ('D', 4, 1.0), ('C', 4, 2.0),
]

TOTAL_SEC = 82.0


def render():
    n_total = int(TOTAL_SEC * SR)
    buf = np.zeros(n_total)

    bars = int(TOTAL_SEC / (BEAT * 4)) + 1   # 小节数

    for bar_i in range(bars):
        t0 = bar_i * BEAT * 4
        if t0 >= TOTAL_SEC:
            break
        ci = bar_i % 4
        _, tones, root = CHORDS[ci][0], CHORDS[ci][1], CHORDS[ci][2]

        # ---- 贝斯：每拍根音，前段轻后段满 ----
        for b in range(4):
            dur = BEAT * 0.9
            sig = triangle(root, dur)
            sig = env_ad(sig, 0.005, 0.05, 0.8, 0.06)
            g = 0.20 if t0 > 4 else 0.12
            place(buf, sig, t0 + b * BEAT, g)

        # ---- 琶音：16 分音符和弦音循环 ----
        arp_seq = [tones[0], tones[1], tones[2], tones[1]] * 4   # 16 个 16 分
        for k, tn in enumerate(arp_seq):
            oc = 4 if tn in ('C', 'D', 'E') else 4
            f = note(tn, oc)
            dur = BEAT * 0.25 * 0.9
            sig = square(f, dur, duty=0.125)
            sig = env_ad(sig, 0.003, 0.02, 0.35, 0.03)
            g = 0.06 if t0 > 4 else 0.045
            place(buf, sig, t0 + k * BEAT * 0.25, g)

        # ---- 主旋律：A 段/B 段交替，前 4 小节只有伴奏 ----
        if bar_i >= 4:
            mel = MELODY_A if (bar_i // 2) % 2 == 0 else MELODY_B
            # 每 2 小节放一段旋律（8 拍）
            if bar_i % 2 == 0:
                cursor = 0.0
                for nm, oc, beats in mel:
                    dur = beats * BEAT * 0.95
                    sig = square(note(nm, oc), dur, duty=0.25, vib=1.0)
                    sig = env_ad(sig, 0.008, 0.08, 0.55, 0.08)
                    place(buf, sig, t0 + cursor * BEAT, 0.16)
                    cursor += beats

        # ---- 镲片：八分音符轻响，每小节偶数拍加一点 ----
        for k in range(8):
            dur = BEAT * 0.2
            sig = noise(dur)
            sig = env_ad(sig, 0.001, 0.02, 0.15, 0.02)
            g = 0.05 if k % 2 == 0 else 0.028
            place(buf, sig, t0 + k * BEAT * 0.5, g)

    # ---- 淡入淡出 ----
    fade_in = int(1.5 * SR)
    fade_out = int(5.0 * SR)
    buf[:fade_in] *= np.linspace(0, 1, fade_in)
    buf[-fade_out:] *= np.linspace(1, 0, fade_out)

    # 归一化到 -12dBFS 左右，留动态给画面感
    peak = np.max(np.abs(buf)) or 1.0
    buf = buf / peak * 0.55

    # 立体声：轻微左右摆（琶音偏右 12ms）
    delay = int(0.012 * SR)
    left = buf
    right = np.concatenate([np.zeros(delay), buf[:-delay]]) * 0.97 + buf * 0.03
    stereo = np.stack([left, right], axis=1)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype('<i2')

    with wave.open(OUT, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('OK ->', OUT, f'{TOTAL_SEC:.0f}s')


if __name__ == '__main__':
    render()
