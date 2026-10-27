"""Put airborne geophysical grids from several survey blocks onto one common grid.

Plain-language note: the USGS survey comes as two blocks with different cell sizes.
This module averages each block onto the same 200 m squares so every square has
one value per measurement. You do not need to open this file.
"""
from __future__ import annotations

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject


def common_transform(bounds_list, cell):
    """Return (transform, height, width) of a grid that covers all bounds, snapped to `cell`."""
    left = np.floor(min(b[0] for b in bounds_list) / cell) * cell
    bottom = np.floor(min(b[1] for b in bounds_list) / cell) * cell
    right = np.ceil(max(b[2] for b in bounds_list) / cell) * cell
    top = np.ceil(max(b[3] for b in bounds_list) / cell) * cell
    width = int(round((right - left) / cell))
    height = int(round((top - bottom) / cell))
    return from_origin(left, top, cell, cell), height, width


def mosaic_average(paths, transform, shape, crs):
    """Average-resample each raster in `paths` onto the target grid; later files fill gaps only.

    Returns a float32 array with NaN where no source has data. Each target cell is
    the mean of the source cells it covers (rasterio Resampling.average), so finer
    blocks are smoothed, not subsampled.
    """
    out = np.full(shape, np.nan, dtype="float32")
    for p in paths:
        with rasterio.open(p) as src:
            src_arr = src.read(1).astype("float32")
            nod = src.nodata
            if nod is not None:
                src_arr[src_arr == nod] = np.nan
            tmp = np.full(shape, np.nan, dtype="float32")
            reproject(src_arr, tmp, src_transform=src.transform, src_crs=src.crs,
                      dst_transform=transform, dst_crs=crs, src_nodata=np.nan,
                      dst_nodata=np.nan, resampling=Resampling.average)
        fill = np.isnan(out) & ~np.isnan(tmp)
        out[fill] = tmp[fill]
    return out


def analytic_signal(field, cell):
    """Total-gradient (3D analytic signal) amplitude of a potential-field grid.

    Horizontal derivatives by central differences; the vertical derivative by the
    FFT |k| filter on a NaN-filled copy. Edges within a few cells of data gaps are
    less reliable; cells that were NaN stay NaN.
    """
    f = field.astype("float64")
    mask = np.isnan(f)
    fill = np.where(mask, np.nanmean(f), f)
    dy, dx = np.gradient(fill, cell)
    ky = np.fft.fftfreq(f.shape[0], d=cell) * 2 * np.pi
    kx = np.fft.fftfreq(f.shape[1], d=cell) * 2 * np.pi
    k = np.sqrt(kx[None, :] ** 2 + ky[:, None] ** 2)
    dz = np.real(np.fft.ifft2(np.fft.fft2(fill - fill.mean()) * k))
    asig = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    asig[mask] = np.nan
    return asig.astype("float32")


def local_std(field, radius_cells):
    """Standard deviation in a square window (2r+1 cells), ignoring NaN. A texture measure."""
    from scipy.ndimage import uniform_filter
    f = field.astype("float64")
    valid = ~np.isnan(f)
    z = np.where(valid, f, 0.0)
    size = 2 * radius_cells + 1
    n = uniform_filter(valid.astype("float64"), size)
    m1 = uniform_filter(z, size) / np.where(n > 0, n, np.nan)
    m2 = uniform_filter(z * z, size) / np.where(n > 0, n, np.nan)
    sd = np.sqrt(np.clip(m2 - m1 ** 2, 0, None))
    sd[~valid] = np.nan
    return sd.astype("float32")


def local_mean(field, radius_cells):
    """Mean in a square window (2r+1 cells), ignoring NaN."""
    from scipy.ndimage import uniform_filter
    f = field.astype("float64")
    valid = ~np.isnan(f)
    size = 2 * radius_cells + 1
    n = uniform_filter(valid.astype("float64"), size)
    m = uniform_filter(np.where(valid, f, 0.0), size) / np.where(n > 0, n, np.nan)
    m[~valid] = np.nan
    return m.astype("float32")
