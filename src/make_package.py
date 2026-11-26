# -*- coding: utf-8 -*-
"""把灾厄助手项目打包成可移植的干净副本（不含备份/截图/缓存）。"""
import shutil, json, zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parent          # calamity-assistant
ROOT = SRC.parent                              # 工作目录
STAGE = ROOT / "dist" / "灾厄助手-项目源码"
ZIP = ROOT / "灾厄助手-项目源码-20261126.zip"

if STAGE.exists():
    shutil.rmtree(STAGE)
for d in ("src", "raw"):
    (STAGE / d).mkdir(parents=True)
(STAGE / "site").mkdir()

# ---------- 1. src：构建必需 + 全部脚本 ----------
SKIP_JSON = ("wikitext_cache.json", "icon_download_report.json", "icon_retry_report.json")
n_json = n_py = 0
for f in SRC.glob("*.json"):
    if ".bak" in f.name or f.name in SKIP_JSON:
        continue
    shutil.copy2(f, STAGE / "src" / f.name)
    n_json += 1
for f in SRC.glob("*.py"):
    shutil.copy2(f, STAGE / "src" / f.name)
    n_py += 1
shutil.copy2(SRC / "app_template.html", STAGE / "src" / "app_template.html")

# 图标：只收真 PNG/GIF，跳过被限流存下的错误响应
IMG = STAGE / "src" / "images"
IMG.mkdir()
n_img = bad = 0
for f in (SRC / "images").glob("*"):
    if not f.is_file():
        continue
    head = f.open("rb").read(4)
    if head in (b"\x89PNG", b"GIF8"):
        shutil.copy2(f, IMG / f.name)
        n_img += 1
    else:
        bad += 1

# ---------- 2. raw：原始抓取物料 ----------
for sub in ("source_pages", "zh_hjson"):
    p = SRC / sub
    if p.exists():
        shutil.copytree(p, STAGE / "raw" / sub)
n_raw = sum(1 for _ in (STAGE / "raw").rglob("*") if _.is_file())

# ---------- 3. 成品 ----------
shutil.copy2(ROOT / "灾厄助手.html", STAGE / "灾厄助手.html")
shutil.copy2(ROOT / "灾厄助手.html", STAGE / "site" / "index.html")

# 说明文档 + 一键重建（bat 必须 GBK，否则 cmd 下中文乱码）
shutil.copy2(SRC / "PACKAGE_README.md", STAGE / "README.md")
BAT = """@echo off
chcp 936 >nul
cd /d "%~dp0src"
echo ================ 正在构建单文件 HTML ================
python build_html.py
if errorlevel 1 goto fail
echo.
echo 构建完成，产物已写入项目根目录的 灾厄助手.html
echo 如需更新托管副本，请把该文件复制覆盖 site\\index.html
goto end
:fail
echo.
echo [失败] 请确认已安装 Python 3.9+ 且已加入 PATH（命令行执行 python --version 验证）
:end
echo.
pause
"""
(STAGE / "重新构建.bat").write_bytes(BAT.replace("\n", "\r\n").encode("gbk"))

print("json", n_json, "py", n_py, "images", n_img, "(skip %d)" % bad, "raw", n_raw)

# ---------- 4. 打包 ----------
if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in STAGE.rglob("*"):
        if f.is_file():
            z.write(f, Path("灾厄助手-项目源码") / f.relative_to(STAGE))
print(ZIP, "%.2f MB" % (ZIP.stat().st_size / 1048576))
