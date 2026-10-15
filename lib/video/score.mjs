// The film's score, synthesized (no samples, no dependency): 96 BPM in D major, a chord a bar (2.5 s), shaped to the story
// on the picture's marks (window.MUSIC of intro.html, in seconds). No kick: the groove is a plucked bass, finger snaps on
// two and four, a shaker and the arpeggio.
//   open      Bm · G · D: a pad and an electric piano; "from your source" lands on D
//   brand     a bloom: the chord rolled, a shimmer of glass; the arpeggio wakes
//   groove    the request is sent: bass and snaps come in
//   tension   NOT FOUND: the groove stops, Em, the filter closes, a clock ticks, a swell rises
//   release   FOUND: back on D, brighter
//   build     prove, review, commit: the filter opens, the last bar doubles, a riser
//   climax    Done: the hook on the piano over the full groove, through under the hood and the numbers
//   outro     the groove falls away; rolled chords, the last D ringing out
// The interface sounds (keys, tool calls, results, steps, camera moves) sit under the music, pitched to the chord playing.
// score(music) → a 48 kHz stereo 16-bit WAV, as a Buffer.
const SR = 48000;
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const V = { D: [50, 57, 61, 64, 66], Bm: [47, 54, 57, 61, 62], G: [43, 50, 54, 57, 59], A: [45, 52, 57, 61, 64], Em: [40, 47, 55, 62, 66] };
const BASS = { D: 38, Bm: 35, G: 43, A: 45, Em: 40 };
const BARS = 'Bm G D G A D Bm G A D Em D Bm G A D G A D Bm G A D Bm G A D G A Bm G D'.split(' ');
// the hook, per chord: [beat, note, beats]
const HOOK = { D: [[0, 78, 1], [1, 81, 1], [2, 78, .5], [2.5, 76, .5], [3, 74, 1]], Bm: [[0, 71, 1], [1, 74, 1], [2, 78, 1], [3, 76, 1]],
  G: [[0, 74, 1], [1, 71, 1], [2, 74, .5], [2.5, 76, .5], [3, 78, 1]], A: [[0, 76, 2], [2, 73, 1], [3, 69, 1]] };
const ARP = [0, 2, 4, 1, 3, 2, 4, 3];
const BASSLINE = [0, 0, 12, 0, 7, 0, 12, 7];
let seed = 7;
const noise = () => ((seed = (seed * 16807) % 2147483647) / 1073741823.5) - 1;

function saw(p, dt) {
  let v = 2 * p - 1;
  if (p < dt) { const x = p / dt; v -= x + x - x * x - 1; } else if (p > 1 - dt) { const x = (p - 1) / dt; v -= x * x + x + x + 1; }
  return v;
}
/** A piecewise-linear curve through [t, value] points. */
const curve = (pts) => (t) => {
  if (t <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) if (t < pts[i][0]) { const [a, x] = pts[i - 1], [b, y] = pts[i]; return x + (y - x) * (t - a) / (b - a); }
  return pts[pts.length - 1][1];
};

export function score({ duration, bpm, sfx = [], marks }) {
  const n = Math.ceil((duration + .5) * SR);
  const L = new Float32Array(n), R = new Float32Array(n), send = new Float32Array(n), echo = new Float32Array(n);
  const at = (t) => Math.max(0, Math.round(t * SR));
  const add = (i, l, r = l, s = 0, e = 0) => { if (i >= 0 && i < n) { L[i] += l; R[i] += r; send[i] += s; echo[i] += e; } };
  const beat = 60 / bpm, bar = 4 * beat;
  const chordAt = (t) => BARS[clamp(Math.floor(t / bar + 1e-6), 0, BARS.length - 1)];
  const tone = (t, p, oct) => V[chordAt(t)][p % 5] + 12 * oct;
  const { brand, session, groove, tension, release, build, climax, outro, last } = marks;
  const quiet = (t) => t >= tension && t < release;

  // ---------------- voices ----------------
  /** A warm pad: each note two saws a few cents apart, through a two-pole lowpass that drifts. */
  const pad = (t0, t1, chord, lvl, cutAt) => {
    const i0 = at(t0), i1 = Math.min(n, at(t1 + 1));
    chord.forEach((m, k) => {
      for (const [d, pan] of [[-.07, -.45], [.07, .45]]) {
        const dt = hz(m + d) / SR;
        let p = (k * .37 + d * 5) % 1, lp = 0, lp2 = 0;
        for (let i = i0; i < i1; i++) {
          const t = i / SR, e = clamp((t - t0) / .5) * (t > t1 ? Math.max(0, 1 - (t - t1)) : 1);
          p += dt; if (p >= 1) p -= 1;
          const a = 1 - Math.exp(-2 * Math.PI * cutAt(t) * (1 + .15 * Math.sin(.8 * t + k)) / SR);
          lp += a * (saw(p, dt) - lp); lp2 += a * (lp - lp2);
          const v = .05 * lvl(t) * e * lp2;
          add(i, v * (1 - pan), v * (1 + pan), v * .7);
        }
      }
    });
  };
  /** An electric piano: a sine modulating itself, bright on the attack, a tine on top; low notes ring longer. */
  const ep = (t0, m, g, len = 2.4) => {
    const f = hz(m), i0 = at(t0), dec = clamp(2.6 - (m - 48) * .045, .9, 2.6), pan = clamp((m - 66) / 30, -.5, .5);
    for (let j = 0; j < SR * (len + .4); j++) {
      const t = j / SR, w = 2 * Math.PI * f * t;
      const v = Math.sin(w + (.25 + 1.6 * Math.exp(-t / .3)) * Math.sin(w)) + .12 * Math.sin(4.02 * w) * Math.exp(-t / .06);
      const s = g * v * Math.min(1, t / .004) * Math.exp(-t / dec) * (t > len ? Math.max(0, 1 - (t - len) / .4) : 1);
      add(i0 + j, s * (1 - pan), s * (1 + pan), s * .55, s * .22);
    }
  };
  /** The arpeggio's pluck: a soft FM bell, bright for a moment. */
  const pluck = (t0, m, g, bright = 1) => {
    const f = hz(m), i0 = at(t0), pan = .35 * Math.sin(m * 1.7);
    for (let j = 0; j < SR * .9; j++) {
      const t = j / SR, w = 2 * Math.PI * f * t;
      const s = g * Math.sin(w + (.3 + .9 * bright * Math.exp(-t / .08)) * Math.sin(2 * w)) * Math.min(1, t / .003) * Math.exp(-t / .28);
      add(i0 + j, s * (1 - pan), s * (1 + pan), s * .4, s * .35);
    }
  };
  /** A plucked bass: a saw and a sine through a lowpass that snaps shut. */
  const bass = (t0, m, g, dur) => {
    const f = hz(m), i0 = at(t0);
    let p = 0, lp = 0, lp2 = 0;
    for (let j = 0; j < SR * (dur + .05); j++) {
      const t = j / SR;
      p = (p + f / SR) % 1;
      const a = 1 - Math.exp(-2 * Math.PI * (180 + 1300 * Math.exp(-t / .05)) / SR);
      lp += a * (.6 * saw(p, f / SR) + Math.sin(2 * Math.PI * p) - lp); lp2 += a * (lp - lp2);
      const v = g * lp2 * Math.min(1, t / .003) * Math.exp(-t / .25) * (t > dur ? Math.max(0, 1 - (t - dur) / .05) : 1);
      add(i0 + j, v, v, v * .08);
    }
  };
  const sub = (t0, t1, m, g, rise = .5) => {
    const f = hz(m), i1 = Math.min(n, at(t1 + .8));
    for (let i = at(t0); i < i1; i++) {
      const t = i / SR, e = clamp((t - t0) / rise) * (t > t1 ? Math.max(0, 1 - (t - t1) / .8) : 1), v = g * e * Math.tanh(1.5 * Math.sin(2 * Math.PI * f * t));
      add(i, v, v, v * .05);
    }
  };
  const burst = (t0, dur, f, q, g, decay, pan = 0, wet = .2) => {
    const i0 = at(t0), F = 2 * Math.sin(Math.PI * Math.min(f, SR / 6) / SR);
    let lo = 0, bp = 0;
    for (let j = 0; j < dur * SR; j++) {
      const x = noise(), hp = x - lo - q * bp;
      bp += F * hp; lo += F * bp;
      const v = g * bp * Math.exp(-j / SR / decay);
      add(i0 + j, v * (1 - pan), v * (1 + pan), v * wet);
    }
  };
  const snap = (t0, g) => { burst(t0, .05, 2400, .35, g, .012, .1, .35); burst(t0 + .004, .12, 1300, .5, g * .5, .03, -.1, .5); };
  const shaker = (t0, g, pan) => {
    const i0 = at(t0);
    let prev = 0;
    for (let j = 0; j < SR * .06; j++) {
      const x = noise(), hp = x - prev, v = g * hp * Math.min(1, j / (SR * .004)) * Math.exp(-j / SR / .018);
      prev = x;
      add(i0 + j, v * (1 - pan), v * (1 + pan), v * .15);
    }
  };
  const glass = (t0, m, g) => {
    const f = hz(m), i0 = at(t0);
    for (let j = 0; j < SR * .9; j++) {
      const t = j / SR, v = g * (Math.sin(2 * Math.PI * f * t) * Math.exp(-t / .3) + .2 * Math.sin(6 * Math.PI * f * t) * Math.exp(-t / .05)) * Math.min(1, t / .002);
      add(i0 + j, v * .9, v * 1.1, v * .7, v * .3);
    }
  };
  /** Air through a band-pass gliding from f0 to f1: 'rise', 'fall' or 'bell' shaped. */
  const sweep = (t0, dur, f0, f1, g, shape = 'bell', wet = .5, p0 = -.3, p1 = .3) => {
    const i0 = at(t0);
    let lo = 0, bp = 0;
    for (let j = 0; j < dur * SR; j++) {
      const k = j / (dur * SR), f = f0 * (f1 / f0) ** k, pan = p0 + (p1 - p0) * k;
      const F = 2 * Math.sin(Math.PI * Math.min(f, SR / 6) / SR), x = noise(), hp = x - lo - .4 * bp;
      bp += F * hp; lo += F * bp;
      const e = shape === 'rise' ? k ** 2.2 : shape === 'fall' ? (1 - k) ** 2 : Math.sin(Math.PI * k) ** 2;
      add(i0 + j, g * bp * e * (1 - pan), g * bp * e * (1 + pan), g * bp * e * wet);
    }
  };
  const roll = (t, chord, g, len = 3, gap = .07) => chord.forEach((m, i) => ep(t + i * gap, m, g, len));

  // ---------------- the music ----------------
  const padLvl = curve([[0, 0], [1.5, .7], [brand, .8], [brand + 1.5, 1.05], [session, .85], [groove, .85], [tension, .5], [release - .1, .5], [release, .85], [build, .9],
    [climax - .1, 1.05], [climax + 1, 1.3], [outro, .85], [last, 1], [duration, .9]]);
  const padCut = curve([[0, 900], [brand, 1300], [brand + 1.5, 2400], [session, 1600], [groove, 1700], [tension, 700], [release - .6, 1000], [release, 2400],
    [build, 1800], [climax - .2, 3600], [climax + .5, 3200], [outro, 2000], [last, 2600]]);
  BARS.forEach((c, b) => pad(b * bar, b === BARS.length - 1 ? duration + 1 : (b + 1) * bar, V[c].map((m) => m + 12), padLvl, padCut));
  // the open: the piano answers the words
  [[.5, 78, .05], [1.6, 74, .045], [2.6, 71, .04], [5, 74, .05], [5.03, 81, .035], [6, 78, .04]].forEach(([t, m, g]) => ep(t, m, g));
  // the brand: a rolled chord, glass above it
  roll(brand, V[chordAt(brand)].map((m) => m + 12), .04, 3.2, .06);
  V[chordAt(brand)].forEach((m, i) => glass(brand + .1 + i * .09, m + 36, .018));
  // the sub, from the brand on; under NOT FOUND it holds a low E
  const subLvl = curve([[brand, .03], [session, .04], [groove, .045], [climax, .055], [outro, .04]]);
  for (let b = Math.floor(brand / bar); b < BARS.length; b++) {
    const t0 = Math.max(brand, b * bar), t1 = b === BARS.length - 1 ? duration : (b + 1) * bar;
    sub(t0, t1, BASS[BARS[b]] <= 40 ? BASS[BARS[b]] : BASS[BARS[b]] - 12, quiet(t0) ? .035 : subLvl(t0), quiet(t0) ? 1.2 : .5);
  }
  // the arpeggio: eighths, sixteenths in the bar before the climax; silent under NOT FOUND
  const arpLvl = curve([[session, 0], [session + 2.5, .028], [groove, .03], [climax - .1, .034], [climax, .04], [outro, .04], [outro + 2.5, 0]]);
  for (let t = session, k = 0; t < outro + 2.5; k++) {
    const fast = t >= climax - bar && t < climax, step = fast ? beat / 4 : beat / 2;
    if (!quiet(t)) pluck(t, V[chordAt(t + .001)][ARP[k % 8]] + 24, arpLvl(t) * (k % 2 ? .7 : 1) * (fast ? .8 : 1), t >= climax ? 1.6 : t >= release ? 1.2 : 1);
    t += step;
  }
  // the groove: the bass in eighths, snaps on two and four, the shaker in sixteenths
  for (let t = groove, k = 0; t < outro - .01; t += beat / 2, k++) {
    if (quiet(t)) continue;
    const c = chordAt(t + .001);
    bass(t, BASS[c] + BASSLINE[k % 8], (k % 8 ? .08 : .1) * (t >= climax ? 1.25 : 1), beat * .42);
    if (k % 4 === 2) snap(t, t >= climax ? .065 : .05);
    if (t >= climax - bar && t < climax && k % 2) snap(t, .015 + .03 * (t - climax + bar) / bar);
  }
  for (let t = session + 2.5, k = 0; t < outro - .5; t += beat / 4, k++) {
    if (quiet(t)) continue;
    shaker(t, (t >= climax ? .012 : t >= groove ? .01 : .007) * [1, .4, .7, .4][k % 4], k % 2 ? .3 : -.3);
  }
  // NOT FOUND: a clock ticks, a swell rises into FOUND; FOUND rolls D with glass on top
  for (let t = tension; t < release - .01; t += beat) burst(t, .015, 6000, .5, .03, .004, .4, .2);
  sweep(release - 1.3, 1.35, 300, 5000, .05, 'rise', .7);
  roll(release, V.D.map((m) => m + 12), .03, 2.4, .05);
  // the build: a riser into the climax, which blooms with the hook on the piano
  sweep(climax - bar, bar, 250, 7000, .06, 'rise', .7);
  roll(climax, [62, 66, 69, 74, 78], .04, 3, .05);
  for (let b = Math.round(climax / bar); b * bar < outro - .01; b++) {
    for (const [bt, m, len] of HOOK[BARS[b]] ?? []) ep(b * bar + bt * beat, m, .055, len * beat * .95);
  }
  // the outro: rolled chords, the last D ringing out
  sweep(outro - 1.3, 1.4, 300, 3500, .035, 'rise', .7);
  for (let b = Math.round(outro / bar); b * bar < last - .01; b++) roll(b * bar, V[BARS[b]].map((m) => m + 12), .03, 3.2);
  roll(last, [50, 57, 62, 66, 69, 73, 76], .045, 4, .08);
  glass(last + .7, 90, .015); glass(last + .85, 93, .012);

  // ---------------- the picture's sounds ----------------
  for (const { t, k, g, p } of [...sfx].sort((a, b) => a.t - b.t)) {
    if (k === 'key') { burst(t, .012, 3200, .5, .035 * g, .003, (p % 5 - 2) * .08, .05); burst(t + .004, .03, 900, .6, .025 * g, .01, 0, .05); }
    else if (k === 'enter') { burst(t, .016, 2600, .5, .06 * g, .004, 0, .08); burst(t + .006, .05, 700, .6, .045 * g, .016, 0, .08); }
    else if (k === 'tool') burst(t, .02, 5200, .5, .02 * g, .004, .2, .1);
    else if (k === 'done') glass(t, tone(t, p, 2), .02 * g);
    else if (k === 'fail') { glass(t, tone(t, 1, 1), .03 * g); glass(t + .14, tone(t, 0, 1) - 2, .028 * g); }
    else if (k === 'step') { glass(t, tone(t, p, 3), .016 * g); glass(t + .07, tone(t, p + 2, 3), .012 * g); }
    else if (k === 'glass') glass(t, tone(t, p, 2), .03 * g);
    else if (k === 'shimmer') for (let j = 0; j < 5; j++) glass(t + j * .08, tone(t, j, 3), .014 * g);
    else if (k === 'bloom') sweep(t - .4, 1.4, 600, 6000, .03 * g, 'bell', .8);
    else if (k === 'whoosh') sweep(t - .3, 1, 6000, 400, .05 * g, 'bell', .6, .5, -.5);
    else if (k === 'air') sweep(t - .3, .9, 3000, 800, .025 * g, 'bell', .5, -.4, .4);
    else if (k === 'strike') sweep(t, .5, 2200, 700, .03 * g, 'fall', .3);
    else if (k === 'resolve') [0, 2, 4].forEach((q, j) => glass(t + j * .09, tone(t, q, 3), .016 * g));
  }

  // ---------------- the delay, the reverb, the master ----------------
  const D = Math.round(beat * .75 * SR), dl = new Float32Array(n), dr = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    dl[i] = echo[i] + (i >= D ? .38 * dr[i - D] : 0); dr[i] = i >= D ? .38 * dl[i - D] : 0;
    add(i, .3 * (dl[i] - echo[i]), .3 * dr[i], 0);
  }
  const verb = (x, offs) => {
    const out = new Float32Array(n);
    for (const d0 of [1557, 1617, 1491, 1422]) {
      const d = Math.round((d0 + offs) * SR / 44100) * 2, buf = new Float32Array(d);
      let p = 0, lo = 0;
      for (let i = 0; i < n; i++) { const y = buf[p]; lo += .3 * (y - lo); buf[p] = x[i] + .85 * lo; p = (p + 1) % d; out[i] += y * .25; }
    }
    for (const d0 of [225, 556]) {
      const d = Math.round((d0 + offs) * SR / 44100), buf = new Float32Array(d);
      let p = 0;
      for (let i = 0; i < n; i++) { const b = buf[p], y = -out[i] * .5 + b; buf[p] = out[i] + b * .5; out[i] = y; p = (p + 1) % d; }
    }
    return out;
  };
  const vl = verb(send, 0), vr = verb(send, 23);
  let peak = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR, f = Math.min(1, t / .02) * (1 - clamp((t - duration + 2) / 2));
    L[i] = Math.tanh((L[i] + .4 * vl[i]) * 1.1) * f;
    R[i] = Math.tanh((R[i] + .4 * vr[i]) * 1.1) * f;
    peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  }
  const gain = .89 / (peak || 1);
  const wav = Buffer.alloc(44 + n * 4);
  wav.write('RIFF', 0); wav.writeUInt32LE(36 + n * 4, 4); wav.write('WAVEfmt ', 8);
  wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(2, 22); wav.writeUInt32LE(SR, 24);
  wav.writeUInt32LE(SR * 4, 28); wav.writeUInt16LE(4, 32); wav.writeUInt16LE(16, 34); wav.write('data', 36); wav.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) {
    wav.writeInt16LE(Math.round(clamp(L[i] * gain, -1, 1) * 32767), 44 + i * 4);
    wav.writeInt16LE(Math.round(clamp(R[i] * gain, -1, 1) * 32767), 46 + i * 4);
  }
  return wav;
}
