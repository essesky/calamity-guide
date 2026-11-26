# 灾厄助手 · 项目源码包

泰拉瑞亚灾厄（Calamity Mod）手机端离线查询助手。单文件 HTML，无服务器、无网络依赖，图标全部 base64 内嵌。

**当前数据版本**：v2.2.4（2026-11-23 数据快照）
**成品体积**：3.03 MB（单文件）
**打包日期**：2026-11-25

---

## 一、先看这里：只是想用

双击根目录的 **`灾厄助手.html`** 就行。手机端的话把这个文件传到手机（微信文件传输 / 数据线 / 网盘都行），用浏览器打开，建议「添加到主屏幕」。

不需要装任何东西，不需要联网。

`site/index.html` 是同一份文件的重命名副本，专门给静态托管（Nginx / 对象存储 / 各种 Pages）用的，内容完全一样。

---

## 二、目录结构

```
灾厄助手-项目源码/
├── 灾厄助手.html          ← 成品，双击即用（3.03 MB）
├── 重新构建.bat           ← Windows 双击重建（需要 Python）
├── README.md              ← 本文件
├── site/
│   └── index.html         ← 托管用副本（与成品字节一致）
├── src/                   ← 源码，重建所需的一切都在这里
│   ├── app_template.html  ← 页面模板：CSS + 全部 JS + 各 tab 渲染函数
│   ├── build_html.py      ← 构建脚本：把数据和图片塞进模板，产出单文件
│   ├── images/            ← 3226 张图标（PNG / GIF），构建时转 base64
│   ├── app_data_final.json← 主数据：装备 / 属性 / 配方 / Boss / NPC / 阶段
│   ├── materials.json     ← 材料大全 428 条（250 可用 + 178 装饰折叠；含原版熔炼配方 rc 字段）
│   ├── vanilla_final.json ← 原版合成表 220 条（套装部件、饰品链）
│   ├── vanilla_recipes.json ← 原版配方原始数据 3411 条（兜底查询用）
│   ├── newbie.json        ← 「新手推荐」页文案
│   ├── hardmode.json      ← 「肉后流程」页文案
│   ├── ranger.json        ← 「射手专线」数据（巨鲨四档 / 支线 / 熔炉合体 / 五个坑）
│   ├── melee.json         ← 「战士专线」（锤系五档 + 方舟三档 + 8 条短线）
│   ├── magic.json         ← 「法师专线」（始源三档 + 虚空三档 + 12 条短线）
│   ├── summon.json        ← 「召唤专线」（葱茏 + 天狼双线合流 + 8 条短线）
│   ├── rogue.json         ← 「盗贼专线」（回旋镖四档 + 投矛三档 + 8 条短线）
│   ├── gen_class_data.py  ← 上面四份 json 的生成脚本（配方自动取自 items，文案手写）
│   ├── icon_alias.json    ← 抽象原料名 → 图名（Any Lead Bar → Lead Bar 等）
│   ├── zh_alias.json      ← 中文原料名 → 英文图名
│   └── *.py               ← 其余 84 个脚本：抓取 / 解析 / 逐条修补（历史沿革）
└── raw/                   ← 原始抓取物料，重建时用不到，改数据时可能有用
    ├── source_pages/      ← wiki 页面原文缓存（165 份 txt）
    └── zh_hjson/          ← 官方简中语言包 hjson（60 份）
```

---

## 三、重建（改完数据后必做）

**环境要求：Python 3.9+，只用标准库，不用 pip 装任何东西。**

Windows 双击 `重新构建.bat`，或手动：

```bash
cd src
python build_html.py
```

终端会打印：

```
hardmode steps 6
embedded images 3226
ingredient aliases 63 of 63
zh aliases 95 of 95
<项目根目录>/灾厄助手.html
bytes 3181369
```

产物写到 **项目根目录** 的 `灾厄助手.html`（不是 src 里）。构建脚本用 `__file__` 定位目录，放到任何路径都能跑，不依赖固定盘符；图标遍历做了排序，换机器重建结果一致（同字节数，md5 也一致）。

改完记得把新产物再复制一份到 `site/index.html` 覆盖旧的：

```bash
cp 灾厄助手.html site/index.html
```

---

## 四、常见修改怎么下手

| 想改的东西 | 改哪个文件 | 说明 |
|---|---|---|
| 界面样式、布局、颜色 | `src/app_template.html` 里的 `<style>` | 深色主题，CSS 变量在 `:root` |
| 某个 tab 的渲染逻辑 | `src/app_template.html` 里的 `renderXxx()` | 入口是 `function render(q)`，按 `state.tab` 分发 |
| 装备 / Boss / NPC 数据 | `src/app_data_final.json` | 结构调整要同步改渲染函数 |
| 材料大全条目 | `src/materials.json` | 字段：`z` 中文名 `c` 分类 `h` 获取方式 `s` 来源 `l` 位置 `p` 价格 `r` 用途 `u` 用途备注 `rc` 原版配方；开采前提 `pkv` 镐力% `pkn` 最短镐 `dep` 层深 `risk` 风险；锭类 `ore` 指回矿石键（详情页据此带出开采前提）。`c` 取值：`ore/bar/gem/drop/plant/bag/mat` 正常显示，`sub` 建材、`boss` 召唤物、`perk` 永久增益、`deco` 装饰（默认折叠） |
| 套装 / 原版饰品配方 | `src/vanilla_final.json` | `{s: 来源, r: 配方[{s:工作站, i:[[原料,量]], a:产量}], parts: 部件}` |
| 新手 / 肉后页文案 | `newbie.json` / `hardmode.json` | 每个步骤的物品用英文键引用，必须存在于 `app_data_final.json` 的 `items` |
| 射手专线 | `ranger.json` | 结构：`main.tiers`（四档主线）/ `side.rows`（两档短线）/ `fusion.rows`（熔炉合体）/ `kit.groups` / `traps.rows`；材料写成 `[英文键, 数量, 可选中文名]`，第三项只在数据里查不到该键时才需要 |
| 其余四职业专线 | `melee.json` / `magic.json` / `summon.json` / `rogue.json` | 与 `ranger.json` 同构，多一个可选 `alt.tiers`（第二条完整线，结构同 `main`）。**改完请跑 `python gen_class_data.py` 重新生成**，它会把 `tiers` 里的 `mats` 按 `app_data_final.json` 的真实配方自动填好，手改 `mats` 会被覆盖 |
| 图标 | `src/images/<英文名>.png` | 文件名 = 英文名，空格转下划线；构建会自动生成大小写别名 |
| 图标缺失报错 | `src/icon_alias.json` / `zh_alias.json` | 抽象名或中文名指向真实图名 |

**改数据的铁律**：物品键一律用英文键（`Frostspark Boots`），中文只是显示层，靠 `app_data_final.json` 的 `names` 字段映射。往 JSON 里塞中文键会导致点不开。

---

## 五、当前数据规模

| 项目 | 数量 |
|---|---|
| 装备条目 | 3174 |
| 灾厄配方 | 2310 |
| Boss | 53 |
| NPC | 26 |
| 职业阶段 | 19（含肉后 8 段） |
| 材料大全 | 428（250 可用 / 178 装饰折叠） |
| 原版套装 / 合成链 | 220 |
| 原版配方原始条目 | 3411 |
| 内嵌图标 | 3226 |

数据源：`calamitymod.wiki.gg`（Cargo API）+ `terraria.wiki.gg` + CalamityCN 官方简中语言包。

---

## 六、已知遗留问题（不影响主要使用）

1. **43 个纯中文饰品名点不开**（云朵气球、天界石一类）：原版配方表里缺它们的前置（Sun Stone / Moon Charm / Poison Staff），不是漏做，需要先补前置数据。
2. **76 条装备 tooltip 仍是英文原文**，未翻译，功能正常。
3. **NPC「Trapper」的居住条件存疑**，来自 wiki 数据本身，待人工核对。
4. **Boss「至尊超法师」未实装**（wiki 缺数据）。

---

## 七、重新抓取数据（一般用不到）

`src/` 里的 `fetch_*.py` 是抓取脚本，需要额外装依赖：

```bash
pip install requests
```

它们会往 wiki 的 API 发请求，**注意频率**，被限流会返回错误 JSON 而不是图片。`build_html.py` 已经有防护：文件头不是 PNG/GIF 魔数的一律跳过，所以坏文件不会污染构建产物。

抓取顺序（有依赖关系）：`fetch_items` → `fetch_cargo` → `fetch_langpack` → `parse_*` → `finalize_data` → `build_html`。逐条修补脚本（`fix_*` / `add_*` / `norm_*` / `patch_*`）是按发现问题的时间顺序写的，重复执行前先看脚本里有没有幂等判断。

---

## 八、部署

`site/index.html` 可以直接扔到：
- 静态托管：Cloudflare Pages / Vercel / GitHub Pages / 腾讯云 COS 静态网站
- 自己的 Nginx：放进 web 根目录，改个 `index.html` 就行
- 内网共享：直接放 SMB 共享，同事用浏览器打开

单文件无外部请求，不存在 CORS、跨域、离线失效的问题。
