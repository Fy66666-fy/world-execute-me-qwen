# Qwen 版配色重映射：Claude 橙 → 千问蓝紫（靛紫系），暖棕底 → 冷靛底
# 对 config.json 做机械替换，替换后校验 JSON 可解析。
import json, sys

MAPPING = {
    # me 主色（on/error 共用）
    "#d97757": "#5f6cf0", "#ee8f66": "#8590ff", "#8a4b36": "#3a4494",
    # me 主色（warm/errWarm 共用）
    "#ee8552": "#7d89ff", "#ffa066": "#9aa6ff", "#a05636": "#4a55b0",
    # bloom
    "#ffb08a": "#aab4ff", "#ffba90": "#b9c4ff",
    # errRed 的 me
    "#ffd9c6": "#d6dcff", "#fff0e6": "#e8ecff", "#e09a80": "#96a2e8",
    # errCream 的 me
    "#a95234": "#3d4bb0", "#8a3a20": "#2a3690", "#dfa58d": "#a3aef0",
    # ash 的 me / bloom
    "#b5765d": "#8a90c8", "#d38d6e": "#a8ade0", "#61493f": "#454a75", "#d9b9a9": "#c3c8e8",
    # warm 底（暖棕 → 冷靛）
    "#2c2520": "#262633", "#241d19": "#1e1e2a", "#3b312a": "#32334a", "#5e4b3f": "#4d4e6e",
    "#fffaf1": "#f8f7ff", "#dccbb9": "#c9c7e6", "#917d6d": "#807fa6",
    # error 底（暗红棕 → 暗靛紫）
    "#1d1413": "#191521", "#160e0d": "#130f1a", "#2d1c1a": "#271d33", "#553331": "#4b3360",
    "#cbb5af": "#c0b7cf", "#80625d": "#77698a",
    # on 底（中性灰 → 冷灰）
    "#262624": "#24262e", "#1f1e1d": "#1d1f26", "#30302e": "#2e3140", "#4a4844": "#474a5c",
    "#faf9f5": "#f7f8fc", "#c2c0b6": "#bfc3d6", "#7d7b73": "#7a7e93",
    # errCream 纸底
    "#efece3": "#eef0f8", "#e2ded3": "#e0e3f0", "#bdb8aa": "#b4b7c9",
    # ash 底
    "#1c1b1a": "#1b1b1f", "#161514": "#151518", "#282624": "#26262d", "#3e3b37": "#3b3b45",
    "#cfccc4": "#ccced8", "#96938a": "#93959f", "#6a6862": "#676870",
}

path = "config.json"
s = open(path, encoding="utf-8").read()
n = 0
for old, new in MAPPING.items():
    c = s.count(old)
    if c:
        s = s.replace(old, new)
        n += c
# 文档串里的品牌描述同步（仅 config 的 _doc 文本）
s = s.replace("orange", "indigo").replace("Orange", "Indigo")
json.loads(s)  # 校验
open(path, "w", encoding="utf-8", newline="\n").write(s)
print(f"replaced {n} hex occurrences, doc words updated, JSON valid")
