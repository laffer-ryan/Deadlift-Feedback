from scipy.signal import welch, butter, filtfilt
import numpy as np
import pandas as pd

def estimate_cutoff_hz(signal: np.ndarray, fps: int, energy_keep: float = 0.95, nperseg: int | None = None) -> float:
    """
    Return the smallest frequency f_c such that the one sided PSD’s
    cumulative energy below f_c ≥ `energy_keep`.
    """
    f, Pxx = welch(signal, fs=fps, nperseg=nperseg)
    cumulative = np.cumsum(Pxx)
    cutoff_idx = np.searchsorted(cumulative,
                                 energy_keep * cumulative[-1])
    return f[cutoff_idx]

def butterworth_filter(df, fps: int = 60, energy_keep: float = 0.95, order: int = 4, group_cols=None,  conf_threshold: float = 0.85):
    """
    Same as before, but chooses cut‑off automatically per time‑series.
    """
    df = df.sort_values(by=['video_name', 'frame_count']).copy()
    def process_one(col, conf):
        # use confident samples only when “listening” to the spectrum
        good = (conf >= conf_threshold) & ~np.isnan(col)
        if good.sum() < 2*fps:            # < ~2 s of data → bail out
            return col

        fc = estimate_cutoff_hz(col[good].to_numpy(), fps, energy_keep)
        nyq = 0.5 * fps
        b, a = butter(order, fc/nyq, btype='low')
        padlen = 3 * max(len(a), len(b))

        filt = col.to_numpy(dtype=float)
        apply_mask = (conf < conf_threshold) & ~np.isnan(filt)
        if apply_mask.sum() > padlen:
            filt[apply_mask] = filtfilt(b, a, filt[apply_mask])
        return pd.Series(filt, index=col.index)

    def filter_group(g):
        g = g.copy()
        for c in g.columns:
            if c.endswith(('_x', '_y')):
                base = c[:-2]
                conf_c = base + '_confidence'
                if conf_c in g.columns:
                    g[c] = process_one(g[c], g[conf_c])
        return g

    if group_cols:
        return (df.groupby(group_cols, group_keys=False)
                .apply(filter_group)
                .reset_index(drop=True))
    return filter_group(df)