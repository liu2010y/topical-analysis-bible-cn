#!/usr/bin/env python3
"""生成 PWA 图标：护眼绿底＋白色翻开的书。
用法：python3 tools/make_icons.py
输出：assets/icons/icon-192.png / icon-512.png / apple-touch-icon.png (180)
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons"

BG = (47, 125, 70)        # --accent 绿
PAGE = (247, 251, 247)    # 近白的纸色
SPINE = (222, 238, 224)


def make_icon(size):
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    s = size

    def pt(x, y):
        return (x * s, y * s)

    # 翻开的书：左右两页（略呈梯形），中缝留底色
    # 左页
    d.polygon([pt(.18, .34), pt(.475, .30), pt(.475, .70), pt(.18, .74)], fill=PAGE)
    # 右页
    d.polygon([pt(.82, .34), pt(.525, .30), pt(.525, .70), pt(.82, .74)], fill=PAGE)
    # 页面上的"文字行"
    lw = max(1, round(s * 0.018))
    for i, y in enumerate((.40, .47, .54, .61)):
        d.line([pt(.225, y + .01), pt(.435, y)], fill=SPINE, width=lw)
        d.line([pt(.565, y), pt(.775, y + .01)], fill=SPINE, width=lw)
    # 书脊下的"底座"弧线
    d.line([pt(.18, .74), pt(.5, .78), pt(.82, .74)], fill=PAGE, width=max(2, round(s * .02)))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for size, name in [(192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")]:
        make_icon(size).save(OUT / name)
        print(f"生成 assets/icons/{name}")


if __name__ == "__main__":
    main()
