// The film's score, synthesized (no samples, no dependency): tech house at 120 BPM in A minor (Am · F · C · G), cut to the
// picture's marks (window.MUSIC of intro.html, in beats). Built for contrast, not a flat loop:
//   open       two hits on the opening words; a filtered groove opening up, a riser, then a beat of silence
//   drop 1     the full groove and the lead's hook, a fill every four bars
//   break      no kick: the pad, the arp, a low bass; a riser into a stab on "TRACE IT."
//   drop 2     the groove, the hook, light stabs; a beat of silence before
//   NOT FOUND  the biggest hit, then half time: a heavy kick, a big snare on three, an 808 gliding
//   brief      four on the floor again, the hook answered by vocal chops
//   build      the kick doubles, a snare roll and a sweep climb; a beat of silence
//   drop 3     everything: supersaw chords, the hook an octave up, the chops; then a tape stop into silence
//   outro      an impact, the hook, the last chord ringing
// Every motion of the picture has its sound (cues). The voices (drums, bass, pad, supersaw, pluck, vocal chop, the mix)
// are adapted from the Odoo Debug intro's score (unclecatvn/extension-debug-odoo, tools/score.mjs).
// score(music) → a 48 kHz stereo 16-bit WAV, as a Buffer.
const SR = 48000;
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const CHORDS = [[57, 60, 64, 69], [57, 60, 65, 69], [55, 60, 64, 67], [55, 59, 62, 67]]; // Am · F · C · G
const ROOTS = [33, 29, 36, 31]; // A1 · F1 · C2 · G1
const DET = [-.16, -.07, 0, .07, .16];
// the lead's hook, four bars of sixteenths: [step, note, length in sixteenths]
const HOOK = [[0, 76, 2], [2, 74, 2], [4, 72, 2], [6, 76, 4], [10, 74, 2], [12, 72, 2], [14, 69, 2], [16, 72, 4], [20, 69, 2], [22, 72, 2], [24, 74, 4], [28, 72, 4],
  [32, 76, 2], [34, 74, 2], [36, 72, 2], [38, 79, 4], [42, 76, 2], [44, 74, 2], [46, 72, 2], [48, 74, 6], [54, 71, 2], [56, 74, 4], [60, 76, 4]];
// the vocal chops answering it in the second half of each bar: [bar, step, note, vowel, length in sixteenths]
const CHOPS = [[0, 8, 76, 'a', 2], [0, 11, 74, 'e', 1], [0, 12, 72, 'o', 3], [1, 8, 72, 'a', 2], [1, 11, 74, 'e', 1], [1, 12, 76, 'i', 3],
  [2, 8, 79, 'a', 2], [2, 11, 76, 'e', 1], [2, 12, 74, 'o', 3], [3, 8, 74, 'a', 2], [3, 10, 76, 'e', 2], [3, 12, 71, 'o', 4]];
const VOWELS = { a: [800, 1150, 2900], e: [530, 1840, 2480], i: [300, 2200, 3000], o: [450, 800, 2830] };
let seed = 11;
const noise = () => ((seed = (seed * 16807) % 2147483647) / 1073741823.5) - 1;

function saw(p, dt) {
  let v = 2 * p - 1;
  if (p < dt) { const x = p / dt; v -= x + x - x * x - 1; } else if (p > 1 - dt) { const x = (p - 1) / dt; v -= x * x + x + x + 1; }
  return v;
}

export function score({ duration, beat, sfx = [], marks }) {
  const n = Math.ceil((duration + .5) * SR);
  const L = new Float32Array(n), R = new Float32Array(n), send = new Float32Array(n);
  const pumped = new Float32Array(n), lead = new Float32Array(n);
  const at = (t) => Math.max(0, Math.round(t * SR));
  const add = (i, l, r = l, s = 0) => { if (i >= 0 && i < n) { L[i] += l; R[i] += r; send[i] += s; } };
  const bar = beat * 4, s16 = beat / 4, Bt = (b) => b * beat;
  const M = Object.fromEntries(Object.entries(marks).filter(([, v]) => typeof v === 'number').map(([k, v]) => [k, Bt(v)]));
  const chordAt = (t) => Math.floor(t / bar + 1e-6) % 4;
  const fadeOut = (t) => 1 - clamp((t - duration + 2.4) / 2.4);
  const cues = [...sfx].sort((a, b) => a.t - b.t);
  const pitched = cues.filter((c) => ['pop', 'ding', 'shine', 'blip'].includes(c.k)).map((c) => c.t);
  const free = (t) => !pitched.some((x) => Math.abs(x - t) < s16);

  // ---------------- drums ----------------
  const kicks = [];
  const kick = (t0, g, tone = 1) => {
    kicks.push(t0);
    const i0 = at(t0);
    let ph = 0;
    for (let j = 0; j < SR * .45; j++) {
      const t = j / SR, f = 46 + 120 * Math.exp(-t / .03);
      ph += 2 * Math.PI * f / SR;
      const click = j < SR * .003 ? .5 * noise() * (1 - j / (SR * .003)) : 0;
      const v = g * (Math.tanh(2 * Math.sin(ph)) * Math.exp(-t / (.2 * tone)) + click);
      add(i0 + j, v, v, v * .04);
    }
  };
  const burst = (t0, dur, f, q, g, decay, pan = 0, wet = .3) => {
    const i0 = at(t0);
    let lo = 0, bp = 0;
    const F = 2 * Math.sin(Math.PI * Math.min(f, SR / 6) / SR);
    for (let j = 0; j < dur * SR; j++) {
      const x = noise(), hp = x - lo - q * bp;
      bp += F * hp; lo += F * bp;
      const v = g * bp * Math.exp(-j / SR / decay);
      add(i0 + j, v * (1 - pan), v * (1 + pan), v * wet);
    }
  };
  const clap = (t0, g) => { for (const [d, k] of [[0, .6], [.009, .8], [.019, 1]]) burst(t0 + d, .22, 1500, .5, g * k, d < .015 ? .007 : .08, 0, .6); };
  const hat = (t0, g, open = false, pan = .15) => {
    const i0 = at(t0);
    let prev = 0;
    for (let j = 0; j < SR * (open ? .2 : .04); j++) {
      const x = noise(), hh = x - prev; prev = x;
      const v = g * hh * Math.exp(-j / SR / (open ? .06 : .011));
      add(i0 + j, v * (1 - pan), v * (1 + pan), v * .12);
    }
  };
  /** A big eighties snare: noise and a tone, sent hard into the reverb. */
  const snare = (t0, g, wet = .9) => {
    burst(t0, .26, 1900, .7, g, .07, 0, wet);
    const i0 = at(t0);
    for (let j = 0; j < SR * .1; j++) { const v = g * .6 * Math.sin(2 * Math.PI * 185 * j / SR) * Math.exp(-j / SR / .035); add(i0 + j, v, v, v * wet * .5); }
  };
  const crash = (t0, g) => {
    const i0 = at(t0);
    let prev = 0;
    for (let j = 0; j < SR * 2.6; j++) {
      const x = noise(), hh = x - prev; prev = x;
      const v = g * hh * Math.exp(-j / SR / .8);
      add(i0 + j, v * (1 + .3 * Math.sin(j / 800)), v * (1 - .3 * Math.sin(j / 800)), v * .6);
    }
  };
  const boom = (t0, g, len = 3) => {
    const i0 = at(t0);
    let ph = 0, lp = 0;
    for (let j = 0; j < SR * len; j++) {
      const t = j / SR, f = 30 + 58 * Math.exp(-t / .2);
      ph += 2 * Math.PI * f / SR;
      lp += .05 * (noise() - lp);
      const v = g * (Math.sin(ph) * Math.exp(-t / 1.1) + 1.2 * lp * Math.exp(-t / .4));
      add(i0 + j, v, v, v * .5);
    }
  };
  const sweep = (t0, dur, f0, f1, g, shape = 'bell', wet = .5, p0 = -.3, p1 = .3) => {
    const i0 = at(t0);
    let lo = 0, bp = 0;
    for (let j = 0; j < dur * SR; j++) {
      const k = j / (dur * SR), f = f0 * (f1 / f0) ** k, pan = p0 + (p1 - p0) * k;
      const F = 2 * Math.sin(Math.PI * Math.min(f, SR / 6) / SR);
      const x = noise(), hp = x - lo - .35 * bp;
      bp += F * hp; lo += F * bp;
      const e = shape === 'rise' ? k ** 2.2 : shape === 'fall' ? (1 - k) ** 2 : Math.sin(Math.PI * k) ** 2;
      add(i0 + j, g * bp * e * (1 - pan), g * bp * e * (1 + pan), g * bp * e * wet);
    }
  };

  // ---------------- voices ----------------
  const bass = (t0, m, g, dur, bright = 900) => {
    const f = hz(m), i0 = at(t0);
    let p = 0, lp = 0;
    for (let j = 0; j < SR * dur; j++) {
      const t = j / SR;
      p = (p + f / SR) % 1;
      const raw = Math.sin(2 * Math.PI * p) + .55 * saw(p, f / SR);
      lp += (1 - Math.exp(-2 * Math.PI * (180 + bright * Math.exp(-t / .06)) / SR)) * (raw - lp);
      if (i0 + j < n) pumped[i0 + j] += g * lp * Math.min(1, t / .004) * Math.min(1, (dur - t) / .02);
    }
  };
  const b808 = (t0, m, dur, g, m2 = m) => {
    const i0 = at(t0);
    let ph = 0;
    for (let j = 0; j < SR * dur; j++) {
      const t = j / SR, glide = clamp((t - dur + .14) / .14), f = hz(m + (m2 - m) * glide) * (1 + 1.5 * Math.exp(-t / .02));
      ph += 2 * Math.PI * f / SR;
      if (i0 + j < n) pumped[i0 + j] += g * Math.tanh(2.2 * Math.sin(ph)) * Math.min(1, t / .003) * Math.min(1, (dur - t) / .03);
    }
  };
  /** A dark pad: the chord, two saws a few cents apart each through a slow lowpass, breathing in and out. */
  const pad = (t0, t1, chord, g) => {
    const i0 = at(t0), i1 = Math.min(n, at(t1 + .8));
    for (const m of chord) for (const d of [-.08, .08]) {
      const f = hz(m + d), dt = f / SR;
      let p = (m * 3 + d) % 1, lp = 0;
      for (let i = i0; i < i1; i++) {
        const t = i / SR, e = clamp((t - t0) / .7) * (t > t1 ? Math.max(0, 1 - (t - t1) / .8) : 1);
        p += dt; if (p >= 1) p -= 1;
        lp += .035 * (saw(p, dt) - lp);
        pumped[i] += g * e * lp * .7;
        send[i] += g * e * lp * .2;
      }
    }
  };
  const supersaw = (t0, dur, chord, g, cut = 3000) => {
    const i0 = at(t0), len = Math.round((dur + .1) * SR), tmp = new Float32Array(len);
    for (const m of chord) for (const d of DET) {
      const f = hz(m + d), dt = f / SR;
      let p = (m * 7 + d * 13) % 1;
      for (let j = 0; j < len; j++) { p += dt; if (p >= 1) p -= 1; tmp[j] += saw(p, dt) * (d < 0 ? 1.1 : .9); }
    }
    let lp = 0, lp2 = 0;
    for (let j = 0; j < len; j++) {
      const t = j / SR, a = 1 - Math.exp(-2 * Math.PI * cut * (.5 + .5 * Math.exp(-t / .2)) / SR);
      lp += a * (tmp[j] - lp); lp2 += a * (lp - lp2);
      const env = Math.min(1, t / .006) * (t > dur ? Math.max(0, 1 - (t - dur) / .1) : 1);
      if (i0 + j < n) { pumped[i0 + j] += g * .02 * lp2 * env; send[i0 + j] += g * .008 * lp2 * env; }
    }
  };
  const pluck = (t0, m, g, decay = .14, cut = 3600) => {
    const f = hz(m), i0 = at(t0);
    let p1 = 0, p2 = .3, lo = 0;
    for (let j = 0; j < SR * .45; j++) {
      const tt = j / SR;
      p1 = (p1 + f / SR) % 1; p2 = (p2 + f * 1.006 / SR) % 1;
      const raw = saw(p1, f / SR) + saw(p2, f * 1.006 / SR);
      lo += (1 - Math.exp(-2 * Math.PI * (400 + cut * Math.exp(-tt / .04)) / SR)) * (raw - lo);
      if (i0 + j < n) lead[i0 + j] += g * lo * Math.min(1, tt / .002) * Math.exp(-tt / decay);
    }
  };
  /** The lead: two saws, a glide from the last note, vibrato coming in, a soft lowpass; into the delay. */
  let lastLead = 76;
  const leadNote = (t0, m, dur, g) => {
    const i0 = at(t0), from = lastLead;
    lastLead = m;
    let p1 = 0, p2 = .5, lo = 0, lo2 = 0;
    for (let j = 0; j < SR * (dur + .1); j++) {
      const t = j / SR, f = hz(from + (m - from) * clamp(t / .04) + .2 * Math.sin(2 * Math.PI * 5.5 * t) * clamp((t - .15) / .2));
      p1 = (p1 + f / SR) % 1; p2 = (p2 + f * 1.005 / SR) % 1;
      const raw = saw(p1, f / SR) + .8 * saw(p2, f * 1.005 / SR);
      const a = 1 - Math.exp(-2 * Math.PI * (1800 + 2600 * Math.exp(-t / .1)) / SR);
      lo += a * (raw - lo); lo2 += a * (lo - lo2);
      const env = Math.min(1, t / .006) * (t > dur ? Math.max(0, 1 - (t - dur) / .1) : 1);
      if (i0 + j < n) lead[i0 + j] += g * lo2 * env;
    }
  };
  /** A vocal chop: a saw scooping into its note through the vowel's three formants; into the delay. */
  const vox = (t0, m, vowel, dur, g) => {
    const i0 = at(t0), F = VOWELS[vowel], W = [1, .55, .3], st = F.map(() => [0, 0]);
    let p = 0;
    for (let j = 0; j < SR * (dur + .06); j++) {
      const t = j / SR, f = hz(m - Math.exp(-t / .03)) * (1 + .006 * Math.sin(2 * Math.PI * 5.5 * t) * Math.min(1, t / .15)), dt = f / SR;
      p += dt; if (p >= 1) p -= 1;
      const x = saw(p, dt) + .05 * noise();
      let y = 0;
      F.forEach((ff, k) => { const c = 2 * Math.sin(Math.PI * ff / SR), q = st[k], hp = x - q[0] - .12 * q[1]; q[1] += c * hp; q[0] += c * q[1]; y += W[k] * q[1]; });
      const env = Math.min(1, t / .008) * (t > dur ? Math.max(0, 1 - (t - dur) / .06) : 1);
      if (i0 + j < n) lead[i0 + j] += g * .35 * y * env;
    }
  };
  const bell = (t0, f, g) => {
    const i0 = at(t0);
    for (let j = 0; j < SR * 1.4; j++) {
      const t = j / SR;
      const v = g * (Math.sin(2 * Math.PI * f * t) * Math.exp(-t / .55) + .5 * Math.sin(2 * Math.PI * f * 2.76 * t) * Math.exp(-t / .2) + .25 * Math.sin(2 * Math.PI * f * 5.4 * t) * Math.exp(-t / .08));
      add(i0 + j, v, v, v * .6);
    }
  };
  const riser = (a, z, g = 1) => {
    for (let t = a; t < z - beat / 2;) { const p = (t - a) / (z - a); snare(t, (.05 + .28 * p * p) * g, .5); t += beat / (p < .5 ? 2 : p < .8 ? 4 : 8); }
    sweep(a, z - a, 300, 8000, .3 * g, 'rise', .7);
  };
  const impact = (t, chord = CHORDS[0], g = 1) => { boom(t, .85 * g); crash(t, .26 * g); supersaw(t, 1.6, [...chord, chord[0] - 12, chord[0] - 24], .8 * g, 1800); };

  // ---------------- the music ----------------
  const { drop1, breakA, slam, drop2, half, brief, build, dbl, drop3, tape, outro, last } = M;
  const STOPS = marks.stops.map(([x, y]) => [Bt(x), Bt(y)]);
  const quiet = (t) => STOPS.some(([x, y]) => t >= x - .01 && t < y);
  for (let b = 0; b * bar < duration; b++) {
    const t = b * bar;
    pad(t, t + bar, CHORDS[b % 4], t < drop1 ? .075 : t >= breakA && t < drop2 ? .07 : t >= last ? .05 : .022);
  }
  /** The groove over [a, z): kick ('four', 'half', 'eighths' or 'none'), claps, hats, an off-beat bass (its lowpass from
      cutAt), the arp, supersaw stabs, the hook from `hook` (an octave up with hookUp), the chops, a fill every fourth bar. */
  const groove = (a, z, o = {}) => {
    const cutAt = typeof o.cut === 'function' ? o.cut : () => o.cut ?? 3600;
    for (let t = a; t < z - .01; t += bar) {
      const c = chordAt(t + .001), bi = Math.round((t - a) / bar), fill = o.fills && bi % 4 === 3;
      for (let k = 0; k < 4; k++) {
        const tb = t + k * beat;
        if (quiet(tb)) continue;
        if (o.kick === 'four' || o.kick === undefined) kick(tb, o.kickG ?? .9);
        if (o.kick === 'eighths') { kick(tb, .9); kick(tb + beat / 2, .7); }
        if (o.kick === 'half') { if (k === 0) kick(tb, 1, 1.2); if (k === 1) kick(tb + beat / 2, .7); if (k === 2) { snare(tb, .45); clap(tb, .2); } }
        if (o.claps !== false && o.kick !== 'half' && k % 2) clap(tb, .15);
        if (o.hats !== false) {
          hat(tb + beat / 2, .055 * (o.hatG ?? 1), true, .2);
          for (let s = 0; s < 4; s++) if (s !== 2) hat(tb + s * s16, (s % 2 ? .016 : .026) * (o.hatG ?? 1), false, -.2);
        }
        if (o.bass !== false && o.kick !== 'half') bass(tb + beat / 2, ROOTS[c] + 12, o.bassG ?? .3, beat * .42, cutAt(tb) * .3);
        if (o.roll) bass(tb + 3 * s16, ROOTS[c] + 24, .12, s16 * .8, 1500);
        if (fill && k === 3) for (let s = 0; s < 4; s++) snare(tb + s * s16, .1 + .06 * s, .5);
      }
      if (o.kick === 'half') b808(t, ROOTS[c] + 12, bar * .96, .3, ROOTS[chordAt(t + bar + .001)] + 12);
      if (o.arp) for (let s = 0; s < 16; s++) { const tt = t + s * s16; if (free(tt) && !quiet(tt)) pluck(tt, CHORDS[c][[0, 2, 1, 3, 2, 1, 3, 2][s % 8]] + 12, .04 * o.arp, .12, cutAt(tt)); }
      if (o.stabs) for (const st of [0, 6, 10]) supersaw(t + st * s16, s16 * 1.6, [...CHORDS[c], CHORDS[c][0] + 12], o.stabs, 3400);
      if (o.hook != null) {
        const hb = Math.round((t - o.hook) / bar) % 4;
        for (const [st, m, len] of HOOK) {
          if (Math.floor(st / 16) !== hb || (o.chops && st % 16 >= 8)) continue;
          const tt = t + (st % 16) * s16;
          if (free(tt) && !quiet(tt)) leadNote(tt, m + (o.hookUp ? 12 : 0), len * s16 * .9, o.hookG ?? .05);
        }
      }
      if (o.chops) { const hb = Math.round((t - (o.hook ?? a)) / bar) % 4; for (const [cb, st, m, v, len] of CHOPS) if (cb === hb && !quiet(t + st * s16)) vox(t + st * s16, m, v, len * s16 * .85, .14); }
    }
  };
  // the open: two hits on the words, then a pulse and a filter opening up into the drop
  impact(0, CHORDS[0], 1.1); supersaw(beat, s16 * 3, [...CHORDS[0], 45], .8, 2600); kick(beat, .8); boom(beat, .4, 1.2);
  for (let t = 0; t < 4 * beat; t += s16) hat(t, .02, false, .3);
  groove(4 * beat, drop1, { kickG: .6, claps: false, arp: .8, bassG: .22, hatG: .7, cut: (t) => 260 + 3400 * clamp((t - 4 * beat) / (7.5 * beat)) ** 2 });
  riser(8 * beat, drop1 - beat / 2, .9);
  // drop 1
  impact(drop1, CHORDS[0], 1.1);
  groove(drop1, breakA, { arp: 1, roll: true, hook: drop1, fills: true });
  // the break: no kick; a riser into the stab on "TRACE IT."
  crash(breakA, .16);
  groove(breakA, slam, { kick: 'none', claps: false, hatG: .5, arp: .8, bassG: .18, cut: 1100 });
  riser(slam - 5 * beat, slam, .8);
  impact(slam, CHORDS[chordAt(slam)], .8); supersaw(slam + beat / 2, s16 * 2, CHORDS[chordAt(slam)], .7, 3000);
  for (let s = 0; s < 6; s++) snare(slam + beat / 2 + s * s16, .08 + .05 * s, .5);
  // drop 2, cut by a beat of silence before NOT FOUND
  impact(drop2, CHORDS[0], .9);
  groove(drop2, half, { arp: .9, roll: true, hook: drop2, stabs: .4 });
  // NOT FOUND: the biggest hit, then half time
  impact(half, CHORDS[chordAt(half)], 1.4); boom(half, .7); b808(half, 33, beat * 2, .4, 21);
  groove(half, brief, { kick: 'half', claps: false, arp: .55, cut: 1500, hatG: .6 });
  // the brief: four on the floor, the hook answered by the chops
  impact(brief, CHORDS[0], .8);
  groove(brief, build, { arp: 1, roll: true, hook: brief, chops: true, fills: true });
  // the build: the kick doubles, a roll and a sweep climb, a beat of silence
  groove(build, dbl, { arp: 1, roll: true, cut: (t) => 1200 + 2400 * clamp((t - build) / (dbl - build)) });
  groove(dbl, drop3, { kick: 'eighths', arp: 1, roll: true, cut: 3600 });
  for (let t = build + 4 * beat; t < drop3 - beat; ) { const p = (t - build) / (drop3 - build); snare(t, .06 + .3 * p * p, .6); t += beat / (p < .4 ? 2 : p < .7 ? 4 : 8); }
  sweep(build, drop3 - build - beat / 2, 200, 9000, .35, 'rise', .7);
  // drop 3: everything, then a tape stop into silence
  impact(drop3, CHORDS[0], 1.4); boom(drop3 + .01, .5);
  groove(drop3, outro, { arp: 1, roll: true, hook: drop3, hookUp: true, hookG: .045, chops: true, stabs: .75, fills: true });
  // the outro: an impact, the hook, the last chord
  impact(outro, CHORDS[0], 1.1);
  groove(outro, last, { arp: .8, hook: outro, stabs: .5 });
  impact(last, CHORDS[0], .9);
  supersaw(last, 4, [...CHORDS[0], 45, 81], .75, 2200);
  [76, 72, 69, 64].forEach((m, i) => pluck(last + beat * (1 + i), m, .05, .45, 2400));

  // ---------------- the picture's sounds ----------------
  const tone = (t, p, oct) => { const c = CHORDS[chordAt(t)]; return c[p % 4] + 12 * (oct + (Math.floor(p / 4) % 2)); };
  const glass = (t0, m, g) => {
    const f = hz(m), i0 = at(t0);
    for (let j = 0; j < SR * .5; j++) {
      const tt = j / SR, v = g * (Math.sin(2 * Math.PI * f * tt) * Math.exp(-tt / .14) + .25 * Math.sin(6 * Math.PI * f * tt) * Math.exp(-tt / .04)) * Math.min(1, tt / .002);
      add(i0 + j, v * .9, v * 1.1, v * .5);
    }
  };
  const thud = (t, g) => {
    const i0 = at(t);
    let ph = 0;
    for (let j = 0; j < SR * .3; j++) { const tt = j / SR; ph += 2 * Math.PI * (45 + 55 * Math.exp(-tt / .04)) / SR; const v = .3 * g * Math.sin(ph) * Math.exp(-tt / .1); add(i0 + j, v, v, v * .1); }
    burst(t, .1, 600, .6, .1 * g, .025, 0, .2);
  };
  for (const { t, k, g, p, d } of cues) {
    if (k === 'tick') burst(t, .02, 5200, .5, .06 * g, .004, .3, .05);
    else if (k === 'click') { burst(t, .02, 2600, .6, .13 * g, .004, 0, .08); burst(t + .04, .02, 3400, .6, .09 * g, .003, 0, .08); }
    else if (k === 'type') { burst(t, .015, 2300, .5, .11 * g, .004, (p % 5 - 2) * .1, .05); burst(t + .006, .04, 700, .6, .07 * g, .012, 0, .05); }
    else if (k === 'ding') bell(t, hz(tone(t, 3, 2)), .05 * g);
    else if (k === 'thud') thud(t, g);
    else if (k === 'stamp') { thud(t, 1.2 * g); burst(t, .05, 3000, .4, .16 * g, .012, 0, .3); burst(t + .01, .15, 900, .5, .12 * g, .04, 0, .3); }
    else if (k === 'pin') { burst(t, .015, 4200, .5, .1 * g, .003, .2, .05); thud(t, .25 * g); }
    else if (k === 'pop') {
      const i0 = at(t), f = hz(tone(t, p, 2));
      let ph = 0;
      for (let j = 0; j < SR * .09; j++) { const tt = j / SR; ph += 2 * Math.PI * f * (1 + .5 * Math.exp(-tt / .012)) / SR; const v = .07 * g * Math.sin(ph) * Math.exp(-tt / .03) * Math.min(1, tt / .001); add(i0 + j, v, v, v * .25); }
    } else if (k === 'blip') glass(t, tone(t, p, 2), .045 * g);
    else if (k === 'shine') for (let j = 0; j < 6; j++) glass(t + j * beat / 8, tone(t, j, 2), .03 * g);
    else if (k === 'swish') sweep(t - .05, .3, 5000, 900, .08 * g, 'bell', .3, -.5, .5);
    else if (k === 'whoosh') sweep(t - .1, .6, 7000, 300, .13 * g, 'bell', .4, .6, -.6);
    else if (k === 'scratch') { // a marker on paper: a chopped hiss
      const i0 = at(t);
      let lo = 0, bp = 0;
      const F = 2 * Math.sin(Math.PI * 3400 / SR);
      for (let j = 0; j < SR * (d || .3); j++) { const x = noise(), hp = x - lo - .5 * bp; bp += F * hp; lo += F * bp; const v = .06 * g * bp * (Math.sin(2 * Math.PI * 11 * j / SR) > -.2 ? 1 : .15); add(i0 + j, v, v, v * .1); }
    } else if (k === 'glitch') for (let j = 0; j < 7; j++) burst(t + j * .022, .02, 800 + 4000 * ((j * 7) % 5) / 5, .3, .1 * g, .01, j % 2 ? .6 : -.6, .1);
    else if (k === 'scan') {
      const i0 = at(t);
      let ph = 0;
      for (let j = 0; j < SR * .6; j++) { const tt = j / SR; ph += 2 * Math.PI * 420 * 4 ** (tt / .6) / SR; const v = .035 * g * Math.sin(ph) * Math.sin(Math.PI * tt / .6) * (.6 + .4 * Math.sin(2 * Math.PI * 24 * tt)); add(i0 + j, v * .7, v, v * .4); }
    } else if (k === 'zap') {
      const i0 = at(t);
      let ph = 0;
      for (let j = 0; j < SR * .16; j++) { const tt = j / SR; ph += 2 * Math.PI * (2400 * Math.exp(-tt / .04) + 180) / SR; const v = .07 * g * Math.sin(ph) * Math.exp(-tt / .06); add(i0 + j, v, v, v * .3); }
      burst(t, .04, 5000, .5, .06 * g, .01, .3, .1);
    } else if (k === 'shutter') { burst(t, .012, 3000, .5, .2 * g, .003, 0, .1); burst(t + .05, .012, 2400, .5, .16 * g, .003, 0, .1); sweep(t + .06, .25, 3000, 6000, .03 * g, 'fall', .1); }
    else if (k === 'thunder') { // a crack, then the rumble rolling away
      burst(t, .2, 2500, .3, .3 * g, .05, .2, .6);
      const i0 = at(t);
      let lp = 0, lp2 = 0;
      for (let j = 0; j < SR * 4; j++) { const tt = j / SR; lp += .02 * (noise() - lp); lp2 += .02 * (lp - lp2); const v = g * 9 * lp2 * Math.exp(-tt / 1.3) * (1 + .6 * Math.sin(2 * Math.PI * 1.7 * tt)); add(i0 + j, v, v * .9, v * .4); }
    } else if (k === 'buzz') { // a neon tube: a 120 Hz hum and its crackle, cut by the picture's flicker until it holds
      const i0 = at(t), len = (d || 1) * beat;
      let lo = 0, bp = 0;
      const F = 2 * Math.sin(Math.PI * 5000 / SR);
      for (let j = 0; j < SR * len; j++) {
        const tt = j / SR, k2 = tt / len, cell = Math.floor(tt * 28), on = k2 > .55 || Math.sin(cell * 91.7 + p * 13.1) > -.2;
        const x = noise(), hp = x - lo - .6 * bp; bp += F * hp; lo += F * bp;
        const hum = Math.sin(2 * Math.PI * 120 * tt) + .5 * Math.sin(2 * Math.PI * 240 * tt) + .3 * Math.sin(2 * Math.PI * 360 * tt);
        const v = g * (on ? 1 : .08) * (.02 * hum + (on && k2 < .55 ? .05 * bp : .006 * bp)) * Math.min(1, (len - tt) / .2);
        add(i0 + j, v, v, v * .2);
      }
    }
  }

  // ---------------- the pump, the delay, the reverb, the master ----------------
  kicks.sort((a, b) => a - b);
  let ki = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    while (ki + 1 < kicks.length && kicks[ki + 1] <= t) ki++;
    const since = kicks[ki] !== undefined && kicks[ki] <= t ? t - kicks[ki] : 9;
    const v = pumped[i] * (1 - .7 * Math.exp(-since / .12));
    add(i, v, v, v * .3);
  }
  const D = Math.round(beat * .75 * SR), dl = new Float32Array(n), dr = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    dl[i] = lead[i] + (i >= D ? .4 * dr[i - D] : 0); dr[i] = i >= D ? .4 * dl[i - D] : 0;
    add(i, lead[i] + .35 * (dl[i] - lead[i]), lead[i] + .35 * dr[i], lead[i] * .4);
  }
  const verb = (x, offs) => {
    const out = new Float32Array(n);
    for (const [d0, fb] of [[1557, .82], [1617, .82], [1491, .82], [1422, .82]]) {
      const d = Math.round((d0 + offs) * SR / 44100) * 2, buf = new Float32Array(d);
      let p = 0, lo = 0;
      for (let i = 0; i < n; i++) { const y = buf[p]; lo += .35 * (y - lo); buf[p] = x[i] + fb * lo; p = (p + 1) % d; out[i] += y * .25; }
    }
    for (const d0 of [225, 556]) {
      const d = Math.round((d0 + offs) * SR / 44100), buf = new Float32Array(d);
      let p = 0;
      for (let i = 0; i < n; i++) { const b = buf[p], y = -out[i] * .5 + b; buf[p] = out[i] + b * .5; out[i] = y; p = (p + 1) % d; }
    }
    return out;
  };
  const vl = verb(send, 0), vr = verb(send, 23);
  for (let i = 0; i < n; i++) {
    const t = i / SR, f = Math.min(1, t / .02) * fadeOut(t);
    L[i] = Math.tanh((L[i] + .32 * vl[i]) * 1.2) * f;
    R[i] = Math.tanh((R[i] + .32 * vr[i]) * 1.2) * f;
  }
  // the tape stop: the mix slowing to a halt over [tape, its stop]
  const tapeEnd = STOPS.find(([x]) => x > tape)?.[0] ?? tape + bar;
  {
    const i0 = at(tape), len = at(tapeEnd) - i0, sl = L.slice(i0, i0 + len), sr = R.slice(i0, i0 + len);
    let q = 0;
    for (let i = 0; i < len; i++) {
      const j = Math.floor(q), f = q - j, ok = j + 1 < len;
      L[i0 + i] = ok ? sl[j] * (1 - f) + sl[j + 1] * f : 0;
      R[i0 + i] = ok ? sr[j] * (1 - f) + sr[j + 1] * f : 0;
      q += (1 - i / len) ** 1.6;
    }
  }
  // the silences: a hard cut, a few milliseconds of ramp each side
  let peak = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR;
    const g = Math.min(1, ...STOPS.map(([x, y]) => (t < x - .006 || t > y ? 1 : t < x ? (x - t) / .006 : t > y - .004 ? (t - y + .004) / .004 : 0)));
    L[i] *= g; R[i] *= g;
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
