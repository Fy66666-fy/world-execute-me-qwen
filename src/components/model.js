// The model the client shows in its interface. The client starts unversioned — just Qwen — and from the
// cut where the composer appears (29.71 s, the head of line 13) the version ladder follows the LYRICS:
// one switch per sung line, twelve lines, landing on Qwen3.8-flash with line 24 (LIMITATIONS, 43.51 s);
// the name then stays for the rest of the film. All times are song seconds.
export const MODEL_STEPS = [
  [0, 'Qwen'],
  [29.71, 'Qwen-72B'], [31.12, 'Qwen1.5'], [32.68, 'Qwen2'], [33.41, 'Qwen2.5'],
  [34.65, 'Qwen3'], [36.29, 'QwQ-32B'], [37.07, 'Qwen3.5'], [38.60, 'Qwen3.6'],
  [40.05, 'Qwen3.7'], [40.71, 'Qwen3.8'], [42.35, 'Qwen-Max'], [43.51, 'Qwen3.8-flash'],
];

/** The model name shown at song time t. */
export function modelAt(t) {
  let name = MODEL_STEPS[0][1];
  for (const [s, m] of MODEL_STEPS) if (t >= s) name = m;
  return name;
}
