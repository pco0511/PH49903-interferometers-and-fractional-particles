"""Extract the measured pajama-plot panels (Fig 2, Fig 3b) from the rendered
figure PNGs for use in the comparison prototypes.

Steps:
  1. auto-detect the heatmap data box via colour saturation (jet is highly
     saturated; white background + black axes/text are not),
  2. pick the WIDE saturated band (= heatmap) and reject the NARROW one
     (= colorbar),
  3. crop, save a lossless PNG to ref-crops/,
  4. invert the jet colormap -> scalar dG in [-1,1] (re-uses the same LUT/KDTree
     idea as fit_to_pixels.py),
  5. downsample and dump JSON {nx,ny,extent,dG} for the web prototypes.

Axis extents are read from the published tick labels (set below); the detected
box is assumed to span exactly those extents.  Good enough for an overlay
prototype (alignment within a few mT).
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from pathlib import Path

HERE = Path(__file__).parent
OUT_CROP = HERE / "ref-crops"
OUT_DATA = HERE / "viz" / "prototypes" / "data"
OUT_CROP.mkdir(exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)

# jet inversion LUT
_lut_t = np.linspace(0, 1, 512)
_lut_rgb = plt.cm.jet(_lut_t)[:, :3] * 255.0
_tree = cKDTree(_lut_rgb)


def invert_jet(rgb):
    h, w, _ = rgb.shape
    flat = rgb.reshape(-1, 3).astype(float)
    _, idx = _tree.query(flat, workers=-1)
    t = _lut_t[idx].reshape(h, w)
    return 2 * t - 1.0


def saturation(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    return sat, mx


def runs(mask):
    """Return list of (start, end_exclusive) for True runs in 1-D bool array."""
    out = []
    i = 0
    n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def detect_box(rgb, sat_thr=0.45, col_frac=0.30, row_frac=0.30):
    sat, mx = saturation(rgb)
    colored = (sat > sat_thr) & (mx > 60)
    col_score = colored.mean(axis=0)            # fraction colored per column
    col_mask = col_score > col_frac
    bands = runs(col_mask)
    if not bands:
        raise RuntimeError("no saturated columns found")
    # widest band = heatmap (colorbar is narrow)
    x0, x1 = max(bands, key=lambda b: b[1] - b[0])
    sub = colored[:, x0:x1]
    row_score = sub.mean(axis=1)
    row_mask = row_score > row_frac
    rbands = runs(row_mask)
    y0, y1 = max(rbands, key=lambda b: b[1] - b[0])
    return x0, x1, y0, y1


def process(figname, extent, out_name, downs=(220, 180), box=None,
            scale=None, unit=None, scale_note=None, extent_note=None,
            srcdir="figures"):
    im = plt.imread(HERE / srcdir / figname)
    rgb = (im[:, :, :3] * (255 if im.max() <= 1.0 else 1)).astype(float)
    if box == "full":                      # source is already a tight data-area crop
        x0, x1, y0, y1 = 0, rgb.shape[1], 0, rgb.shape[0]
    else:
        x0, x1, y0, y1 = box if box else detect_box(rgb)
    print(f"{figname}: box x[{x0}:{x1}] y[{y0}:{y1}]  "
          f"({x1-x0}x{y1-y0})  of {rgb.shape[1]}x{rgb.shape[0]}")
    crop = rgb[y0:y1, x0:x1]
    # save crop PNG (uint8)
    plt.imsave(OUT_CROP / f"{out_name}.png", crop.astype(np.uint8))
    # invert jet -> scalar field, row0 = top (Vg max / least negative)
    D = invert_jet(crop)
    # downsample by block-mean
    ny, nx = D.shape
    tx, ty = downs
    xi = (np.linspace(0, nx, tx + 1)).astype(int)
    yi = (np.linspace(0, ny, ty + 1)).astype(int)
    small = np.empty((ty, tx))
    for a in range(ty):
        for b in range(tx):
            small[a, b] = D[yi[a]:yi[a+1], xi[b]:xi[b+1]].mean()
    payload = {
        "fig": figname,
        "nx": tx, "ny": ty,
        "extent": extent,                # [Bmin,Bmax,Vbot,Vtop]
        "note": "dG normalized to [-1,1] via jet inversion; row0=top=Vtop",
        # absolute scale: physical dG = (normalized dG) * scale, in `unit`.
        # colorbar runs -scale..+scale (jet t=0 -> -scale, t=1 -> +scale).
        "scale": scale, "unit": unit, "scale_note": scale_note,
        "extent_note": extent_note,
        "dG": [round(float(v), 4) for v in small.ravel()],
    }
    (OUT_DATA / f"{out_name}.json").write_text(json.dumps(payload))
    print(f"  -> ref-crops/{out_name}.png , viz/prototypes/data/{out_name}.json"
          f"  (dG range {D.min():.2f}..{D.max():.2f})")
    return payload


if __name__ == "__main__":
    # Fig 2: CLEAN crop supplied by the user (annotation lines split out into
    #   ref-crops/fig2_overlay.svg). It is already a tight data-area crop, so use
    #   the whole image (box="full").
    #   User-confirmed extent B[8.71, 9.03], dVg[-31.9, -3.1];
    #   colormap -4..+4 (x10^-2 e^2/h) -> scale = 4.0.
    pa = process("fig2.png", [8.71, 9.03, -31.9, -3.1], "measured_fig2",
                 srcdir="ref-crops", box="full", scale=4.0, unit="x1e-2 e2/h")
    # Fig 3b: wide range, 450 mT central region. Detected axis FRAME box (the
    #   coloured data only fills the left/central part; right side is no-data).
    #   Tick-calibrated B[8.682, 9.396]; dVg ESTIMATED [-32, -3].
    #   colormap range ASSUMED same as Fig 2 (-4..+4); same paper colorscale,
    #   not separately read off Fig 3b's tiny colorbar.
    pb = process("fig3.png", [8.682, 9.396, -32.0, -3.0], "measured_fig3b",
                 box=(946, 1784, 184, 637),
                 scale=4.0, unit="x1e-2 e2/h", scale_note="assumed same as Fig 2",
                 extent_note="δV_g 추정")
    # combined JS for file:// (fetch of local JSON is blocked under file://)
    js = "window.MEASURED = " + json.dumps({"fig2": pa, "fig3b": pb}) + ";\n"
    (OUT_DATA / "measured.js").write_text(js)
    print(f"  -> viz/prototypes/data/measured.js  ({len(js)} bytes)")
