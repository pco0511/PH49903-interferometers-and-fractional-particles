"""Parse ref-crops/fig2_overlay.svg (the phase-slip / AB-fringe annotation lines
that were split out of Fig 2) into (B, dVg) data coordinates.

The SVG holds, inside one <g> (a global translate that cancels because we map
everything relative to the bounding <rect>):
  * SOLID thick lines  (stroke-width 20.625)  = AB iso-phase fringe markers
    -> negative slope dVg/dB
  * DASHED thin lines   (stroke-width 6.875, stroke-dasharray, matrix flip)
    = discrete phase-slip boundary trajectories -> positive slope
  * one <rect> = the data bounding box (maps to the Fig 2 extent).

Output: viz/prototypes/data/fig2_overlay.js  ->  window.OVERLAY.fig2 = {
  extent, slopeAB, slopeJump, solid:[[B1,V1,B2,V2]...], dashed:[[B1,V1,B2,V2]...] }
"""
import re, json
from pathlib import Path

HERE = Path(__file__).parent
SVG = (HERE / "ref-crops" / "fig2_overlay.svg").read_text()

# Fig 2 data extent (user-confirmed), matching ref-crops/fig2.png
EXTENT = [8.71, 9.03, -31.9, -3.1]      # [Bmin,Bmax,Vbot,Vtop]

# bounding rect (data area) in SVG path coords
m = re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', SVG)
RX, RY, RW, RH = (float(g) for g in m.groups())

def to_data(x, y):
    B = EXTENT[0] + (x - RX) / RW * (EXTENT[1] - EXTENT[0])
    # y=RY (top) -> Vtop (least negative); y=RY+RH (bottom) -> Vbot
    Vg = EXTENT[3] + (y - RY) / RH * (EXTENT[2] - EXTENT[3])
    return B, Vg

def apply_mat(mat, x, y):
    a, b, c, d, e, f = mat
    return a * x + c * y + e, b * x + d * y + f

solid, dashed = [], []
for tag in re.findall(r'<path\b[^>]*>', SVG):
    dm = re.search(r'\bd="([^"]+)"', tag)
    if not dm:
        continue
    nums = [float(v) for v in re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', dm.group(1))]
    if len(nums) < 4:
        continue
    x1, y1, x2, y2 = nums[:4]
    tm = re.search(r'transform="matrix\(([^)]+)\)"', tag)
    if tm:
        mat = [float(v) for v in tm.group(1).split()]
        x1, y1 = apply_mat(mat, x1, y1)
        x2, y2 = apply_mat(mat, x2, y2)
    B1, V1 = to_data(x1, y1); B2, V2 = to_data(x2, y2)
    seg = [round(B1, 4), round(V1, 3), round(B2, 4), round(V2, 3)]
    is_dashed = ("stroke-dasharray" in tag) or ('stroke-width="6.875"' in tag)
    (dashed if is_dashed else solid).append(seg)

def slope(seg):                       # dVg/dB in mV/T
    B1, V1, B2, V2 = seg
    return (V2 - V1) / (B2 - B1) if B2 != B1 else float('nan')

def median(xs):
    s = sorted(xs); n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])

# drop near-vertical / degenerate solids (none expected) and any |dB| tiny
sl_solid = [slope(s) for s in solid if abs(s[2] - s[0]) > 1e-4]
sl_dash = [slope(s) for s in dashed if abs(s[2] - s[0]) > 1e-4]
slopeAB = round(median(sl_solid)) if sl_solid else None
slopeJump = round(median(sl_dash)) if sl_dash else None

print(f"rect (x,y,w,h) = {RX},{RY},{RW},{RH}")
print(f"solid lines: {len(solid)}  median slope = {slopeAB} mV/T  "
      f"(range {round(min(sl_solid))}..{round(max(sl_solid))})")
print(f"dashed lines: {len(dashed)}  median slope = {slopeJump} mV/T  "
      f"(range {round(min(sl_dash))}..{round(max(sl_dash))})")

payload = {"extent": EXTENT, "slopeAB": slopeAB, "slopeJump": slopeJump,
           "solid": solid, "dashed": dashed}
out = HERE / "viz" / "prototypes" / "data" / "fig2_overlay.js"
out.write_text("window.OVERLAY = window.OVERLAY || {};\n"
               "window.OVERLAY.fig2 = " + json.dumps(payload) + ";\n")
print(f"-> {out.relative_to(HERE)}  ({len(solid)} solid + {len(dashed)} dashed)")
