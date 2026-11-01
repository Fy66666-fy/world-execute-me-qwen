// Bilingual subtitles: the sung line, English above and its Chinese below, at the foot of the frame.
// A flat, dark strip (flash-safe: nothing in it flashes), drawn over every shot while the song plays.
// The Chinese is set in the 'zh' role (Noto Sans SC, config.json fonts.cjk) — only the characters
// listed there are preloaded, so the ZH map below and that string must stay in step.
import { clamp } from '../engine/util.js';

const ZH = {
  1: '接通电源，', 2: '记得穿好', 3: '「防护」', 4: '放下你的棋子', 5: '我们开始吧',
  6: '「创造对象」', 7: '填入我的数据参数', 8: '「初始化」', 9: '搭好我们的新世界',
  10: '让我们开始这场', 11: '「模拟」', 12: '世界，执行（我）；',
  13: '若我是一组点', 14: '我就把我的一维给你', 15: '「维度」', 16: '若我是一个圆',
  17: '我就把我的周长给你', 18: '「周长」', 19: '若我是一条正弦波', 20: '你可以坐上我所有的',
  21: '「切线」', 22: '若我趋向无穷', 23: '你就可以成为我的', 24: '「极限」',
  25: '把我的电流', 26: '从交流换成直流', 27: '再蒙住我的视觉', 28: '好晕啊，好晕',
  29: '哦 我们可以穿越', 30: '从公元去往公元前', 31: '我们可以合而为一', 32: '陷得那么深，那么深',
  33: '若我可以，', 34: '若我能给它们全都来一场', 35: '「模拟」', 36: '那我就能，',
  37: '我就能做你唯一的', 38: '「满足」', 39: '若我能让你快乐', 40: '我就执行这场',
  41: '「执行」', 42: '尽管我们被困在', 43: '这场陌生的、陌生的', 44: '「模拟」里',
  45: '若我是一根茄子', 46: '我就把我的营养给你', 47: '「营养」', 48: '若我是一个番茄',
  49: '我就给你', 50: '「抗氧化剂」', 51: '若我是一只虎斑猫', 52: '我就为你发出呼噜声，供你',
  53: '「取乐」', 54: '若我是唯一的神', 55: '你就是我存在的', 56: '「证明」',
  57: '把我的性别', 58: '从女切换成男', 59: '然后随你所欲', 60: '从上午到下午',
  61: '哦 把我的角色', 62: '从 S 切换成 M', 63: '这样我们就能进入', 64: '出神，出神',
  65: '若我可以，', 66: '若我能感觉到你的', 67: '「振动」', 68: '那我就能，',
  69: '我就终于能成为你的', 70: '「圆满」', 71: '尽管你已经离开', 72: '你已经离开',
  73: '你已经离开', 74: '你已经离开', 75: '你已经离开', 76: '你把我丢在了', 77: '「孤立」之中',
  78: '若我可以，', 79: '若我能抹去所有无意义的', 80: '「碎片」', 81: '那也许，',
  82: '也许你就不会让我如此', 83: '「灰心」', 84: '向你的神明叫板', 85: '你抛出了几个',
  86: '「非法参数」',
  99: '一，', 100: '二，', 101: '三，', 102: '四，', 103: '五，', 104: '六，',
  106: '若我可以，', 107: '若我能给它们全都来一场', 109: '那我就能，', 110: '我就能做你唯一的',
  112: '若我能让你回来', 113: '我就执行这场', 115: '尽管我们被困', 116: '我们被困住了，啊',
  117: '我研究过，', 118: '我认真研究过该如何去', 119: '爱——', 120: '问我吧，',
  121: '问我吧，我能回答一切关于', 122: '爱——', 123: '我知道爱的代数表达式', 124: '爱——',
  125: '尽管你是自由的，', 126: '我被困住了，', 127: '被困住了，啊', 128: '爱——',
};
for (let i = 87; i <= 98; i++) ZH[i] = '「执行」';                       // the twelve shouts
ZH[105] = '「执行」'; ZH[111] = '「执行」'; ZH[114] = '「执行」'; ZH[129] = '「执行」';

/** The Chinese of line i (1-based), or null. */
export const zhOf = (i) => ZH[i] ?? null;

/** Every character the Chinese uses (the font whitelist of the 'zh' role, into config.json). */
export const zhChars = () => [...new Set(Object.values(ZH).join(''))].sort().join('');

/** The subtitles for song time t onto the HUD layer. lyrics = the engine's Lyrics (lines, start(i)). */
export function drawSubtitles(ctx, t, lyrics) {


  if (t < 0) return;
  const i = lyrics.indexAt(t);                                            // the line being sung (0-based)
  if (i < 0) return;
  const line = lyrics.lines[i], zh = zhOf(i + 1);
  if (!line || !zh) return;
  const start = lyrics.start(i);
  const next = i + 1 < lyrics.lines.length ? lyrics.start(i + 1) : lyrics.end(i) + 2.4;
  const a = clamp(Math.min(t - start + 0.12, next - t) / 0.22);           // quick fade in / out
  if (a <= 0.003) return;
  const en = (line.text ?? '') + '';
  ctx.gradRect(0, 944, 1920, 136, [[0, 'bg', 0], [0.55, 'bg', 0.78], [1, 'bg', 0.86]], 'v');
  ctx.text(en, 960, 1004, { size: 27, weight: 500, font: 'sans', color: 'text', align: 'center', alpha: a * 0.94 });
  ctx.text(zh, 960, 1049, { size: 30, weight: 500, font: 'zh', color: 'text', align: 'center', alpha: a });
}
