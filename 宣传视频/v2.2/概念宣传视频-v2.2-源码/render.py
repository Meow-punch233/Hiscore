# -*- coding: utf-8 -*-
"""哈绩咪宣传视频 · 渲染管线
读取 scenes.py 的场景表，逐帧绘制 → 管道送 ffmpeg（2x 最近邻放大到 1080p）→ 混入 BGM。
用法：python3 render.py [输出文件名]
"""
import subprocess
import sys
import os
from PIL import Image
from engine import (W, H, FPS, PAL, new_canvas, pixel_dissolve, fade_to, vignette)
import scenes as SC

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TMP_VIDEO = '/tmp/hiscore_video/video_silent.mp4'
BGM = '/tmp/hiscore_video/bgm.wav'
DEFAULT_OUT = ('/mnt/usb-LEGION_PSSD_DD56419883A64-0:0-part1/产物/网页工具/'
               '哈绩咪 Hiscore/宣传视频-像素风-第1版.mp4')

TRANS = 0.45   # 转场时长（秒）


def render_frames():
    """逐帧绘制并送入 ffmpeg 管道"""
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
        '-i', '-',
        '-vf', 'scale=1920:1080:flags=neighbor',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        TMP_VIDEO,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_frames = sum(int(s['dur'] * FPS) for s in SC.SCENES)
    done = 0
    prev_last = None   # 上一场景最后一帧（转场用）

    for si, scene in enumerate(SC.SCENES):
        dur = scene['dur']
        n_frames = int(dur * FPS)
        draw_fn = scene['draw']
        trans = scene.get('trans', 'pixel')   # pixel / fade / cut

        for i in range(n_frames):
            t = i / FPS
            p = i / max(1, n_frames - 1)
            img, d = new_canvas()
            draw_fn(img, d, t, p)

            # 转场：新场景开头与上一场景末帧混合
            if prev_last is not None and i < TRANS * FPS and trans != 'cut':
                tp = i / (TRANS * FPS)
                if trans == 'fade':
                    img = fade_to_fade(prev_last, img, tp)
                else:
                    img = pixel_dissolve(img, prev_last, tp, cell=8, seed=si + 1)

            proc.stdin.write(img.tobytes())
            done += 1

        # 重画最后一帧作为下一段转场底图
        img, d = new_canvas()
        draw_fn(img, d, (n_frames - 1) / FPS, 1.0)
        prev_last = img
        pct = done / total_frames * 100
        print(f'[{si + 1}/{len(SC.SCENES)}] {scene["name"]} 完成 ({pct:.0f}%)', flush=True)

    proc.stdin.close()
    proc.wait()
    print('视频帧渲染完成 ->', TMP_VIDEO)


def fade_to_fade(img_old, img_new, p):
    """两张图交叉淡化"""
    if p <= 0:
        return img_old
    if p >= 1:
        return img_new
    return Image.blend(img_old, img_new, p)


def mux(out_path):
    """混入 BGM，输出最终文件"""
    cmd = [
        'ffmpeg', '-y', '-i', TMP_VIDEO, '-i', BGM,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-movflags', '+faststart',
        out_path,
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('最终视频 ->', out_path)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    render_frames()
    mux(out)
