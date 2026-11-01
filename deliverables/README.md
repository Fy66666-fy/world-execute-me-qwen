# 交付物 / Deliverables

本目录是《world.execute (me);》**千问版**（Qwen 重制）的发布用素材。视频本体太大，没有放进仓库：

| 文件 | 说明 |
|---|---|
| `cover/cover_16x9.png` | 封面 3840×2160（原图） |
| `cover/cover_1920x1080.jpg` | 封面 1080p |
| `cover/cover_1280x720.jpg` | 封面 720p（平台缩略图） |
| `发布文案.md` | 标题候选 + 三档长度正文 + 标签 + 置顶评论 |
| `发布声明.md` | 版权、素材来源、AI 使用说明、转载条款、免责 |
| `stills/` | 关键帧（1:58 侧脸 / 2:10 突脸 / 2:48 瞳孔 / 抽查拼图） |

## 视频

- `千问版_全片_4K60.mp4` — 3840×2160 @60fps，2.18 GB，3:36.95
- `千问版_全片_1080p60.mp4` — 1920×1080 @60fps，834 MB

两者都超过 GitHub 单文件 100 MB 限制，请从 [Releases](../../releases) 下载，或自行用下面的命令重新渲染：

```bash
# 1080p60（约 18 分钟）
node export/export.mjs --width 1920 --height 1080 --fps 60 --out out/qwen_1080p60.mp4

# 4K60（约 70 分钟）
node export/export.mjs --width 3840 --height 2160 --fps 60 --out out/qwen_4K60.mp4

# 封面（4K 静帧）
node export/export.mjs --lab cover --sheet out/cover.png --times 0 --cols 1 --width 3840 --height 2160
```
