// Renders the official Qwen mark (the three verbatim blade paths of motif.js) to a transparent PNG,
// white on nothing, so tools/qwen_bust.py can composite it as the hair ornament.
const { chromium } = require('playwright-core');
const path = require('path');
const BLADES = [
  'M16.4317 2.35157H11.5088C11.5088 2.14167 11.453 1.93176 11.3448 1.74482L10.6855 0.60346C10.4691 0.229567 10.0689 -0.0032959 9.63601 -0.0032959H8.31755C7.88462 -0.0032959 7.48449 0.226288 7.26803 0.60346L5.25097 4.09641C5.03451 4.4703 5.03451 4.93275 5.25097 5.30664L5.9102 6.448C6.12667 6.82189 6.5268 7.05476 6.95973 7.05476H16.4284C16.8613 7.05476 17.2615 6.82517 17.4779 6.448L18.1372 5.30664C18.3536 4.93275 18.3536 4.4703 18.1372 4.09641L17.4779 2.95505C17.2615 2.58116 16.8613 2.34829 16.4284 2.34829L16.4317 2.35157Z',
  'M13.4077 19.3932L15.8675 15.1295C16.0479 15.2345 16.2578 15.2935 16.4743 15.2935H17.7927C18.2257 15.2935 18.6258 15.0639 18.8423 14.6868L19.5015 13.5454C19.718 13.1715 19.718 12.7091 19.5015 12.3352L17.4844 8.84223C17.268 8.46834 16.8678 8.23547 16.4349 8.23547H15.1164C14.6835 8.23547 14.2834 8.46506 14.0669 8.84223L9.33422 17.0416C9.11776 17.4155 9.11776 17.878 9.33422 18.2519L9.99346 19.3932C10.2099 19.7671 10.6101 20 11.043 20H12.3614C12.7944 20 13.1945 19.7704 13.411 19.3932H13.4077Z',
  'M0.164057 8.25187L2.62388 12.5156C2.44349 12.6205 2.28934 12.7714 2.18111 12.9583L1.52188 14.0997C1.30542 14.4736 1.30542 14.936 1.52188 15.3099L2.18111 16.4513C2.39758 16.8252 2.79771 17.058 3.23064 17.058H7.26475C7.69767 17.058 8.09781 16.8284 8.31427 16.4513L8.9735 15.3099C9.18997 14.936 9.18997 14.4736 8.9735 14.0997L4.2408 5.90027C4.02434 5.52638 3.62421 5.29352 3.19128 5.29352H1.87281C1.43989 5.29352 1.03975 5.5231 0.82329 5.90027L0.164057 7.04163C-0.0524071 7.41553 -0.0524071 7.87797 0.164057 8.25187Z',
];
const html = `<!DOCTYPE html><canvas id="c" width="512" height="512"></canvas><script>
  const g = document.getElementById('c').getContext('2d');
  const S = 22.4;                                   // 512 / 2 / 10.3 = the mark's circumradius -> ~229 px
  g.translate(256, 256); g.scale(S, S); g.translate(-9.8328, -10);
  g.fillStyle = '#fff';
  for (const d of ${JSON.stringify(BLADES)}) g.fill(new Path2D(d));
</script>`;
(async () => {
  const b = await chromium.launch({ channel: 'chrome' });
  const p = await b.newPage();
  await p.setContent(html);
  await p.waitForTimeout(200);
  await p.locator('#c').screenshot({ path: path.resolve('out/qwen_mark.png'), omitBackground: true });
  await b.close();
  console.log('wrote out/qwen_mark.png');
})().catch((e) => { console.error(e.message); process.exit(1); });
