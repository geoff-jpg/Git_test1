"""Synthesise an original soundtrack for the Sonardyne Brazil movie.

Everything is generated from scratch (no samples), so there are no licensing
issues. The music follows the slides:

  0-12 s   sea       ocean swell, sonar pings, warm pad       (title, at a glance)
  12-29 s  Brazil    bossa nova guitar, rim clave, shaker    (history, ecosystem)
  29-72 s  tech      electronic arpeggio, pulse bass, beat   (OD OBN, how it works,
                                                               Mero, technology, fleet)
  72-94 s  fusion    bossa + arpeggio + sea, fading to waves (roadmap, takeaways, sources)

One key (D minor) and one tempo (120 bpm, 2 s bars) keep the sections joined.
Usage: python make_music.py out.wav [duration_seconds]
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 94.0
N = int(SR * DUR)
BEAT = 0.5
BAR = 2.0
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def env_curve(points):
    """Piecewise-linear gain automation from [(time, gain), ...]."""
    t = np.arange(N) / SR
    ts, gs = zip(*points)
    return np.interp(t, ts, gs)


def add(buf, sig, t0):
    i = int(t0 * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i]


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------- instruments ----------
def pluck(freq, dur, bright=0.5):
    """Karplus-Strong nylon-ish guitar string."""
    n = int(dur * SR)
    p = max(2, int(SR / freq))
    buf = lp(rng.uniform(-1, 1, p), 1500 + 3000 * bright, 1)
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = 0.4985 * (v + buf[(i + 1) % p])
    return out * np.exp(-np.arange(n) / SR * 1.2)


_pluck_cache = {}


def pluck_c(midi, dur=1.6):
    k = (midi, dur)
    if k not in _pluck_cache:
        _pluck_cache[k] = pluck(hz(midi), dur)
    return _pluck_cache[k]


def pad_note(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * freq * d * t + ph) for d, ph in [(1, 0), (1.004, 1.1), (0.996, 2.3), (2.002, 0.7)])
    s += 0.3 * np.sin(2 * np.pi * freq * 3.001 * t)
    return s * adsr(len(t), a=0.6, d=0.3, s=0.85, r=0.7)


def bass_note(freq, dur, pluck_amt=0.6):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t)
    return s * adsr(len(t), a=0.005, d=0.15, s=pluck_amt, r=0.08)


def synth_arp(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    saw = 2 * ((freq * t) % 1) - 1
    sq = np.sign(np.sin(2 * np.pi * freq * 1.003 * t))
    s = lp(0.6 * saw + 0.4 * sq, 2600)
    return s * np.exp(-t * 7)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def surdo():
    t = np.arange(int(0.6 * SR)) / SR
    f = 55 + 25 * np.exp(-t * 20)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    return hp(rng.uniform(-1, 1, n), 7000) * np.exp(-np.arange(n) / SR * (18 if open_ else 70))


def rim():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return (bp(rng.uniform(-1, 1, n), 1500, 4000) * 0.6 + np.sin(2 * np.pi * 820 * t)) * np.exp(-t * 90)


def shaker(acc):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    e = np.minimum(t / 0.015, 1) * np.exp(-t * 40)
    return hp(rng.uniform(-1, 1, n), 5000) * e * acc


def ping(freq=1480):
    t = np.arange(int(2.5 * SR)) / SR
    s = np.sin(2 * np.pi * freq * t) * np.exp(-t * 2.2) * np.minimum(t / 0.004, 1)
    echo = np.zeros_like(s)
    d = int(0.38 * SR)
    echo[d:] = 0.35 * s[:-d]
    return s + echo


def flute(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(t / 0.3, 1)
    ph = 2 * np.pi * freq * np.cumsum(vib) / SR
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    s += 0.03 * lp(rng.uniform(-1, 1, len(t)), 3000)
    return s * adsr(len(t), a=0.06, d=0.1, s=0.8, r=0.15)


# ---------- harmony (D minor, 4-bar loops) ----------
# voicings as MIDI notes; bass root separately
BOSSA = [  # Dm9 | G13 | Cmaj9 | A7(b13)
    (38, [53, 57, 60, 64]), (43, [53, 59, 64, 69]), (36, [52, 55, 59, 62]), (33, [55, 61, 65, 67])]
TECH = [  # Dm(add9) | Bbmaj7 | Fmaj7 | C6
    (38, [50, 57, 62, 64]), (34, [50, 57, 58, 62]), (41, [48, 57, 60, 65]), (36, [48, 55, 57, 64])]

layers = {k: np.zeros(N) for k in
          ["waves", "ping", "pad_b", "pad_t", "guitar", "bass_b", "rim", "shaker",
           "arp", "bass_t", "kick", "hat", "flute", "surdo"]}

nbars = int(np.ceil(DUR / BAR)) + 1

# Ocean: brown-ish noise with slow swells
white = rng.standard_normal(N)
brown = np.cumsum(white); brown -= lp(brown, 0.5, 1); brown /= np.max(np.abs(brown))
t = np.arange(N) / SR
swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5 - 1.5) ** 2
layers["waves"] = lp(brown, 700) * swell + 0.25 * bp(white, 300, 2500) * swell ** 3 * 0.3

for b in range(nbars):
    t0 = b * BAR
    # pads: whole-bar chords for both progressions (mixed by automation)
    for prog, key in [(BOSSA, "pad_b"), (TECH, "pad_t")]:
        root, chord = prog[b % 4]
        for m in chord:
            add(layers[key], pad_note(hz(m), BAR + 0.7) * 0.12, t0)

    # bossa guitar: thumb bass on 1 and 3, chord stabs on a bossa rhythm (16ths)
    root, chord = BOSSA[b % 4]
    add(layers["guitar"], pluck_c(root + 12, 1.2) * 0.9, t0)
    add(layers["guitar"], pluck_c(root + 12 + (7 if b % 2 == 0 else 0), 1.2) * 0.8, t0 + 2 * BEAT)
    stabs = [0, 3, 6, 10, 12] if b % 2 == 0 else [2, 6, 8, 11, 14]
    for s16 in stabs:
        for k, m in enumerate(chord):
            add(layers["guitar"], pluck_c(m, 0.9) * 0.45, t0 + s16 * BEAT / 4 + k * 0.008)
    add(layers["bass_b"], bass_note(hz(root), 0.9), t0)
    add(layers["bass_b"], bass_note(hz(root + 7), 0.5), t0 + 1.5 * BEAT)
    add(layers["bass_b"], bass_note(hz(root), 0.9), t0 + 2 * BEAT)
    add(layers["bass_b"], bass_note(hz(root + 7), 0.5), t0 + 3.5 * BEAT)
    # bossa clave (3-2 over two bars) and shaker 16ths
    clave = [0, 6, 12] if b % 2 == 0 else [4, 10]
    for s16 in clave:
        add(layers["rim"], rim(), t0 + s16 * BEAT / 4)
    for s16 in range(16):
        add(layers["shaker"], shaker(1.0 if s16 % 4 == 2 else 0.45), t0 + s16 * BEAT / 4)
    add(layers["surdo"], surdo(), t0 + 1 * BEAT)
    add(layers["surdo"], surdo() * 0.7, t0 + 3 * BEAT)

    # tech: 16th-note arpeggio, pulsing 8th bass, four-on-floor, offbeat hats
    root_t, chord_t = TECH[b % 4]
    arp_notes = [chord_t[0] + 12, chord_t[1] + 12, chord_t[2] + 12, chord_t[3] + 12, chord_t[2] + 24, chord_t[3] + 12, chord_t[1] + 12, chord_t[2] + 12]
    for s16 in range(16):
        add(layers["arp"], synth_arp(hz(arp_notes[s16 % 8]), 0.2) * (1.0 if s16 % 4 == 0 else 0.7), t0 + s16 * BEAT / 4)
    for e8 in range(8):
        add(layers["bass_t"], bass_note(hz(root_t), 0.22, 0.4), t0 + e8 * BEAT / 2)
    for q in range(4):
        add(layers["kick"], kick(), t0 + q * BEAT)
        add(layers["hat"], hat(open_=(q % 2 == 1)), t0 + q * BEAT + BEAT / 2)
    for s16 in range(0, 16, 2):
        add(layers["hat"], hat() * 0.35, t0 + s16 * BEAT / 4)

# Brazilian flute melody for the Brazil and finale sections (D dorian / bossa flavour)
MEL = [  # (bar offset in beats, midi, beats)
    (0, 69, 1.5), (1.5, 67, 0.5), (2, 65, 1), (3, 64, 1),
    (4, 67, 1.5), (5.5, 65, 0.5), (6, 64, 1), (7, 62, 1),
    (8, 64, 1), (9, 67, 1), (10, 71, 1.5), (11.5, 69, 0.5),
    (12, 67, 1), (13, 64, 1), (14, 61, 2),
]
for start in [16.0, 76.0, 84.0]:
    for off, m, ln in MEL:
        add(layers["flute"], flute(hz(m + 12), ln * BEAT * 0.95), start + off * BEAT)

# Sonar pings: sparse at the start, on bar lines in the tech section, one to close
for tp in [1.0, 5.0, 9.0, 29.0, 37.0, 45.0, 53.0, 61.0, 69.0, 89.0]:
    add(layers["ping"], ping(1480 if tp < 80 else 1175), tp)

# ---------- mix automation ----------
G = {
    "waves":  [(0, 0), (1.5, 0.6), (10, 0.6), (13, 0.18), (70, 0.15), (74, 0.3), (86, 0.35), (91, 0.7), (DUR, 0.7)],
    "ping":   [(0, 0.35), (DUR, 0.35)],
    "pad_b":  [(0, 0.8), (27, 0.8), (30, 0), (71, 0), (74, 0.7), (DUR, 0.7)],
    "pad_t":  [(0, 0), (27, 0), (30, 0.6), (71, 0.6), (74, 0), (DUR, 0)],
    "guitar": [(0, 0), (11, 0), (13, 0.55), (28, 0.55), (30.5, 0), (72, 0), (74, 0.5), (89, 0.5), (92, 0)],
    "bass_b": [(0, 0), (12, 0), (14, 0.35), (28, 0.35), (30, 0), (72, 0), (74, 0.3), (88, 0.3), (91, 0)],
    "rim":    [(0, 0), (12, 0), (14, 0.22), (28, 0.22), (30, 0), (72, 0), (74, 0.2), (88, 0.2), (91, 0)],
    "shaker": [(0, 0), (12, 0), (14, 0.12), (28, 0.12), (30, 0.05), (70, 0.05), (74, 0.12), (88, 0.12), (91, 0)],
    "surdo":  [(0, 0), (20, 0), (21, 0.35), (28, 0.35), (30, 0), (72, 0), (74, 0.3), (88, 0.3), (91, 0)],
    "flute":  [(0, 0.18), (DUR, 0.18)],
    "arp":    [(0, 0), (28, 0), (30, 0.16), (70, 0.16), (73, 0.08), (88, 0.08), (91, 0)],
    "bass_t": [(0, 0), (28, 0), (30, 0.3), (71, 0.3), (73, 0), (DUR, 0)],
    "kick":   [(0, 0), (30, 0), (31, 0.4), (70, 0.4), (72, 0), (DUR, 0)],
    "hat":    [(0, 0), (29, 0), (31, 0.1), (70, 0.1), (73, 0.05), (88, 0.05), (90, 0)],
}
mix = np.zeros(N)
for k, pts in G.items():
    sig = layers[k]
    pk = np.max(np.abs(sig)) or 1.0
    mix += sig / pk * env_curve(pts)

# master: gentle fade in/out, soft limiting, normalise to about -14 dBFS RMS
mix *= env_curve([(0, 0), (1.0, 1), (DUR - 4, 1), (DUR, 0)])
mix = np.tanh(mix * 1.2)
mix *= 10 ** (-14 / 20) / np.sqrt(np.mean(mix ** 2))
mix = np.clip(mix, -0.98, 0.98)

# light stereo width: short Haas delay on the right channel
d = int(0.012 * SR)
right = np.concatenate([np.zeros(d), mix[:-d]]) * 0.9 + mix * 0.1
stereo = np.stack([mix, right], axis=1)
wavfile.write(sys.argv[1], SR, (stereo * 32767).astype(np.int16))
print("wrote", sys.argv[1], f"{DUR:.1f}s")
