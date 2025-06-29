import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

def spline_interpolation(
    df: pd.DataFrame,
    keypoints=None,
    time_col: str = 'frame_count',
    group_cols='video_name',
    min_points: int = 4
) -> pd.DataFrame:
    """
    Applies cubic spline interpolation to the _x and _y columns for each keypoint in the DataFrame.
    Only interpolates when both x and y are 0 and there is sufficient data.
    Adds a global 'interpolated' boolean column.
    """
    df = df.sort_values(by=['video_name', 'frame_count']).copy()


    if keypoints is None:
        keypoints = [col[:-2] for col in df.columns if col.endswith('_x')]

    def interpolate_group(group):
        group = group.copy()
        interpolated_any = np.zeros(len(group), dtype=bool)
        for kp in keypoints:
            x_col = f'{kp}_x'
            y_col = f'{kp}_y'
            x = group[x_col]
            y = group[y_col]
            valid_mask = (~x.isnull()) & (~y.isnull()) & ~((x == 0.0) & (y == 0.0))
            zero_mask = (x == 0.0) & (y == 0.0)

            # Parameters to skip interpolation for keypoint
            missing_frac = zero_mask.sum() / len(group) # If more than 25% of the frames have
            valid_frac = valid_mask.sum() / len(group)  # if less than 20% of frames have valid values
            if missing_frac > 0.25 or valid_frac < 0.20:
                continue
            
            try:
                spline_x = CubicSpline(group[time_col][valid_mask], x[valid_mask], bc_type='natural')
                spline_y = CubicSpline(group[time_col][valid_mask], y[valid_mask], bc_type='natural')
            except Exception:
                continue
            if zero_mask.any():
                x_interp = spline_x(group[time_col][zero_mask])
                y_interp = spline_y(group[time_col][zero_mask])
                x_interp = np.round(x_interp, decimals=6).astype(np.float32)
                y_interp = np.round(y_interp, decimals=6).astype(np.float32)
                x_interp = np.asarray(x_interp, dtype=float).flatten()
                y_interp = np.asarray(y_interp, dtype=float).flatten()
                if x_interp.size == 1:
                    group.loc[zero_mask, x_col] = x_interp[0]
                    group.loc[zero_mask, y_col] = y_interp[0]
                else:
                    group.loc[zero_mask, x_col] = x_interp
                    group.loc[zero_mask, y_col] = y_interp
                # Mark as interpolated if the new value is not (0,0)
                interpolated_any = interpolated_any | (zero_mask & ((group[x_col] != 0.0) | (group[y_col] != 0.0)))
        group['interpolated'] = interpolated_any
        return group

    if group_cols:
        return df.groupby(group_cols, group_keys=False).apply(interpolate_group).reset_index(drop=True)
    else:
        return interpolate_group(df)