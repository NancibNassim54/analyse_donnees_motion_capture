# smoothness_alternatives.py
import os
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, find_peaks
from scipy.fft import rfft, rfftfreq

INPUT_FOLDER = "data_t"
OUTPUT_FOLDER = "data_smoothness"
FS = 60.0
DT = 1.0 / FS

FINGER_COLS = ["doigts_x", "doigts_y", "doigts_z"]

# ---------- helpers ----------
def speed_norm(pos):
    """pos: (N,3) positions -> returns speed norm (N,)"""
    vel = np.gradient(pos, DT, axis=0)
    speed = np.linalg.norm(vel, axis=1)
    return speed

# ---------- Spectral Arc Length ----------
def spectral_arc_length(speed, fs=FS, fmax=10.0):
    """
    Compute SAL on speed signal.
    Steps:
     - window speed to movement (non-zero), or assume speed already segmented
     - compute FFT magnitude spectrum (rfft)
     - normalize frequency axis to [0, fmax] and magnitude to max=1
     - compute arc length of (freq, mag) curve up to fmax
     - return -arc_length or arc_length depending on convention (we return -SAL so larger -> smoother)
    """
    N = len(speed)
    if N < 4:
        return np.nan

    # remove DC & taper? here simple detrend
    speed = speed - np.mean(speed)

    # FFT
    Y = np.abs(rfft(speed))
    freqs = rfftfreq(N, d=1.0/fs)

    # restrict to 0 < f <= fmax
    mask = (freqs > 0) & (freqs <= fmax)
    if not np.any(mask):
        return np.nan

    f = freqs[mask]
    mag = Y[mask]

    # normalize magnitude
    if np.max(mag) == 0:
        return np.nan
    mag = mag / np.max(mag)

    # compute arc length
    df = np.diff(f)
    dm = np.diff(mag)
    seg_len = np.sqrt(df**2 + dm**2)
    arc = np.sum(seg_len)

    # SAL often reported as negative arc (so more negative = less smooth). 
    # We'll return -arc so that larger positive = smoother.
    return -arc

# ---------- velocity peaks ----------
def velocity_peaks(speed, min_prominence=0.05):
    """
    Count peaks in speed. min_prominence in absolute units of speed;
    choose relative if needed.
    """
    if len(speed) < 3:
        return 0
    peaks, props = find_peaks(speed, prominence=min_prominence)
    return len(peaks)

# ---------- Savitzky-Golay jerk approach ----------
def compute_njs_savgol(pos, window_ms=101, polyorder=3):
    """
    Optional: compute (log) normalized jerk score using Savitzky-Golay derivatives.
    window_ms: window length in ms; must result in odd window length in samples
    """
    N = len(pos)
    # choose window length in samples (odd)
    win = int(round(window_ms * FS / 1000.0))
    if win % 2 == 0:
        win += 1
    if win < 5:
        win = 5
    if win >= N:
        win = N - 1 if (N-1) % 2 == 1 else N-2

    # apply SG to each axis to get smooth pos and derivatives
    pos_f = np.zeros_like(pos)
    for i in range(3):
        pos_f[:, i] = savgol_filter(pos[:, i], window_length=win, polyorder=polyorder, mode='mirror')

    vel = np.gradient(pos_f, DT, axis=0)
    acc = np.gradient(vel, DT, axis=0)
    jerk = np.gradient(acc, DT, axis=0)

    jerk_norm_sq = np.sum(jerk**2, axis=1)
    integral = np.sum(jerk_norm_sq) * DT
    T = N * DT
    diffs = np.diff(pos_f, axis=0)
    L = np.sum(np.linalg.norm(diffs, axis=1))
    if L == 0:
        return np.nan
    NJS = (T**5 / (L**2)) * integral
    return NJS

# ---------- main pipeline ----------
def process_one_df(df):
    # check columns
    if not all(c in df.columns for c in FINGER_COLS):
        return None

    pos = df[FINGER_COLS].values.astype(float)

    # optional light smoothing of pos to reduce spike noise BEFORE spectral measures
    # small SG window to remove frame glitches
    try:
        for i in range(3):
            pos[:, i] = savgol_filter(pos[:, i], window_length=7, polyorder=2, mode='mirror')
    except Exception:
        pass

    # speed
    speed = speed_norm(pos)

    # SAL (use fmax=10Hz or choose smaller if you have low-bandwidth movements)
    sal = spectral_arc_length(speed, fs=FS, fmax=10.0)

    # velocity peaks: choose prominence relative to max speed
    max_speed = np.max(speed) if len(speed)>0 else 0
    prominence = max(0.02, 0.1 * max_speed)  # e.g., 10% of peak or min 0.02
    vpeaks = velocity_peaks(speed, min_prominence=prominence)

    # optional: NJS via SG (more robust than finite diff but still needs decent SNR)
    njs_sg = compute_njs_savgol(pos, window_ms=101, polyorder=3)

    return {"SAL_neg_arc": sal, "vel_peaks": vpeaks, "NJS_savgol": njs_sg, "max_speed": max_speed}

def process_all(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    print("\n--- PROCESS SMOOTHNESS ALTERNATIVES ---\n")
    if not os.path.exists(input_folder):
        print("no input")
        return
    os.makedirs(output_folder, exist_ok=True)

    rows = []
    for participant in os.listdir(input_folder):
        p_in = os.path.join(input_folder, participant)
        if not os.path.isdir(p_in):
            continue
        out_p = os.path.join(output_folder, participant)
        os.makedirs(out_p, exist_ok=True)
        for file in os.listdir(p_in):
            if not file.lower().endswith('.csv'):
                continue
            fpath = os.path.join(p_in, file)
            df = pd.read_csv(fpath)
            res = process_one_df(df)
            if res is None:
                print("Skipping")
                continue

            # save per-file CSV with metrics
            out_csv = os.path.join(out_p, file)
            pd.DataFrame([res]).to_csv(out_csv, index=False)

            print(f"{participant}/{file} -> SAL={res['SAL_neg_arc']:.4f}, "
                  f"peaks={res['vel_peaks']}, NJS_sg={res['NJS_savgol']:.2f}")

            rows.append({"participant": participant, "file": file, **res})

    # summary file
    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(output_folder, "summary_smoothness.csv"), index=False)
    print("\n--- DONE. Results in", output_folder)

if __name__ == '__main__':
    process_all()