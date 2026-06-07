"""Fit the Supp. Fig. 5 model parameters directly to the published pixels.

Panels a/b/c are extracted from the PDF (data area only), the jet colormap is
inverted to recover the scalar conductance dG, and the model parameters are
fit to the pixel data:

  * geometry (A_0, dA/dVg)  from the dominant 2D-FFT wavevector of the central
    region (sub-bin parabolic interpolation),
  * central-region width    -> Delta_qp/E_c,  and its centre -> B_center,
  * alpha_bulk              from the side-region "node" (transition) wavevector,
  * kT/E_c per panel        by matching the side/central coherent-power ratio.

Run after the three _panel_{a,b,c}.npy crops have been produced.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from pathlib import Path

HERE = Path(__file__).parent
PHI0 = 6.62607015e-34 / 1.602176634e-19      # h/e [T m^2]

# data extent (user-confirmed): B 8.2-9.1 T, dVg 0..-30 mV (top->bottom)
BMIN, BMAX, VTOP, VBOT = 8.2, 9.1, 0.0, -30.0

# ------------------------------------------------------------------ #
# jet colormap inversion: RGB pixel -> scalar t in [0,1] -> dG = 2t-1
# ------------------------------------------------------------------ #
_lut_t = np.linspace(0, 1, 512)
_lut_rgb = plt.cm.jet(_lut_t)[:, :3] * 255.0
_tree = cKDTree(_lut_rgb)

def invert_jet(rgb):
    h, w, _ = rgb.shape
    flat = rgb.reshape(-1, 3).astype(float)
    _, idx = _tree.query(flat, workers=-1)
    t = _lut_t[idx].reshape(h, w)
    return 2 * t - 1.0           # normalized dG in [-1,1]

def load_panel(name):
    """Prefer a user-supplied tight crop in ref-crops/; else PDF extraction.

    User crop: ref-crops/panel_{a,b,c}.png  (lossless PNG, data area only,
    B 8.2->9.1 left->right, dVg 0->-30 top->bottom).
    """
    patterns = [f"panel_{name}.png", f"panel_{name}.PNG",
                f"supp-fig5-{name}.png", f"supp-fig5-{name}.PNG"]
    for pat in patterns:
        p = HERE / "ref-crops" / pat
        if p.exists():
            im = plt.imread(p)                       # float 0..1 or uint8
            rgb = (im[:, :, :3] * (255 if im.max() <= 1.0 else 1)).astype(float)
            print(f"  using user crop {p.name}  {rgb.shape[1]}x{rgb.shape[0]}")
            return invert_jet(rgb)
    rgb = np.load(HERE / f"_panel_{name}.npy")
    print(f"  using PDF extraction for panel {name}")
    return invert_jet(rgb)        # shape (H, W), row0 = Vg=0 (top)

# ------------------------------------------------------------------ #
# 2D FFT peak with sub-bin parabolic interpolation
# ------------------------------------------------------------------ #
def fft_peak(sig):
    """Return (fx, fy) in cycles/pixel of the dominant spectral peak."""
    s = sig - sig.mean()
    wy = np.hanning(s.shape[0])[:, None]
    wx = np.hanning(s.shape[1])[None, :]
    F = np.fft.fftshift(np.abs(np.fft.fft2(s * wy * wx)))
    ny, nx = s.shape
    cy, cx = ny // 2, nx // 2
    F[cy-3:cy+4, cx-3:cx+4] = 0          # kill DC neighbourhood
    # restrict to upper half-plane (fy<0 rows) to pick one of the conj. pair
    half = F[:cy, :].copy()
    py, px = np.unravel_index(np.argmax(half), half.shape)
    # parabolic sub-bin in each axis
    def sub(arr, i):
        if 0 < i < len(arr) - 1:
            a, b, c = arr[i-1], arr[i], arr[i+1]
            d = a - 2*b + c
            return i + (0.5 * (a - c) / d if d != 0 else 0.0)
        return float(i)
    pys = sub(F[:, px], py)
    pxs = sub(F[py, :], px)
    fy = (pys - cy) / ny
    fx = (pxs - cx) / nx
    return fx, fy

def geom_from_peak(fx, fy, pxT, pxMV, Bc):
    Bper = 1.0 / abs(fx * pxT) * 1e3        # mT
    Vper = 1.0 / abs(fy * pxMV)             # mV
    slope = -Vper / (Bper * 1e-3)           # mV/T
    A0 = 3 * PHI0 / (Bper * 1e-3)           # m^2   (B-per = 3 Phi0 / A)
    dad = 3 * PHI0 / (Bc * Vper * 1e-3)     # m^2/V
    return dict(Bper=Bper, Vper=Vper, slope=slope, A0=A0, dad=dad)


from scipy.optimize import least_squares

def planewave_fit(region, k0):
    """Fit region ~ A cos(2pi(kx*ix+ky*iy)+phi)+c. Return (kx,ky,resid_norm)."""
    H, W = region.shape
    iy, ix = np.mgrid[0:H, 0:W]
    z = region - region.mean()
    norm = np.sqrt((z**2).mean())
    if norm < 1e-9:
        return k0[0], k0[1], 1.0
    z = z / norm
    def resid(p):
        kx, ky, a, b, c = p
        ph = 2*np.pi*(kx*ix + ky*iy)
        return (a*np.cos(ph) + b*np.sin(ph) + c - z).ravel()
    p0 = [k0[0], k0[1], 1.0, 0.0, 0.0]
    r = least_squares(resid, p0, method='lm', max_nfev=4000)
    rn = np.sqrt((r.fun**2).mean())          # residual rms (0=perfect single wave)
    return r.x[0], r.x[1], rn

def central_scan(D, pxT, pxMV, win=130, step=10):
    """Slide a B-window across D; single-plane-wave fit each -> (Bc, kx, ky, resid)."""
    H, W = D.shape
    fx0, fy0 = fft_peak(D[:, int(.40*W):int(.60*W)])   # central seed
    out = []
    for xc in range(win//2, W-win//2, step):
        sub = D[:, xc-win//2:xc+win//2]
        kx, ky, rn = planewave_fit(sub, (fx0, fy0))
        B = BMIN + (BMAX-BMIN)*xc/(W-1)
        out.append((B, abs(kx), abs(ky), rn))
    return np.array(out)


def main():
    Da, Db, Dc = (load_panel(n) for n in "abc")
    H, W = Da.shape
    pxT = W / (BMAX - BMIN)                  # px per Tesla
    pxMV = H / (VTOP - VBOT)                 # px per mV
    print(f"panels {Da.shape}, px/T={pxT:.0f}, px/mV={pxMV:.2f}\n")

    # ---- sliding single-wave fit on panel a: find central region + geometry
    scan = central_scan(Da, pxT, pxMV)
    B, kx, ky, rn = scan.T
    thr = rn.min() + 0.35*(rn.max()-rn.min())
    central = rn < thr
    Bc = B[central].mean()
    cen_lo, cen_hi = B[central].min(), B[central].max()
    kx_c, ky_c = kx[central].mean(), ky[central].mean()
    Bper = 1.0/(kx_c*pxT)*1e3
    Vper = 1.0/(ky_c*pxMV)
    slope = -Vper/(Bper*1e-3)
    A0 = 3*PHI0/(Bper*1e-3)
    dad = 3*PHI0/(Bc*Vper*1e-3)
    print("[central region & geometry - plane-wave fit on panel a]")
    print(f"  central B-range  = {cen_lo:.3f}-{cen_hi:.3f} T  (width {(cen_hi-cen_lo)*1e3:.0f} mT)")
    print(f"  B_center         = {Bc:.3f} T")
    print(f"  B-period={Bper:.1f} mT  Vg-period={Vper:.2f} mV  slope={slope:.0f} mV/T")
    print(f"  => A_0={A0*1e12:.3f} um^2 ,  dA/dVg={dad*1e12:.3f} um^2/V")

    # ---- alpha_bulk from a side-region 2nd wavevector (panel b) -----------
    Hb, Wb = Db.shape
    side = Db[:, :int(0.22*Wb)]              # left quasiparticle region
    fx1, fy1 = fft_peak(side)
    # subtract dominant wave, find 2nd peak (the node/transition family)
    iy, ix = np.mgrid[0:side.shape[0], 0:side.shape[1]]
    kxc, kyc, _ = planewave_fit(side, (fx1, fy1))
    ph = 2*np.pi*(kxc*ix+kyc*iy)
    M = np.c_[np.cos(ph).ravel(), np.sin(ph).ravel(), np.ones(side.size)]
    coef, *_ = np.linalg.lstsq(M, (side-side.mean()).ravel(), rcond=None)
    res = (side-side.mean()) - (M@coef).reshape(side.shape)
    fx2, fy2 = fft_peak(res)
    # node family slope (positive): transition lines g=const
    node_slope = -(1.0/(fy2*pxMV))/(1.0/(fx2*pxT)*1e-3)
    # alpha_bulk from transition slope dVg/dB = nu*A/(Phi0*alpha) -> alpha=nu*A/(Phi0*slope)
    alpha = NU*A0/(PHI0*abs(node_slope)*1e-3) if node_slope else float('nan')
    print(f"\n[side-region node wavevector - panel b]")
    print(f"  node-family slope = {node_slope:.0f} mV/T  => alpha_bulk = {alpha*1e-3:.3f} mV^-1")

    # ---- recovered + scan diagnostic image -------------------------------
    fig, ax = plt.subplots(4, 1, figsize=(9, 8))
    for a, D, t in zip(ax[:3], (Da, Db, Dc), "abc"):
        a.imshow(D, extent=[BMIN, BMAX, VBOT, VTOP], origin='upper',
                 aspect='auto', cmap='jet', vmin=-1, vmax=1)
        a.axvline(cen_lo, color='w', ls='--', lw=1); a.axvline(cen_hi, color='w', ls='--', lw=1)
        a.set_title(f"recovered dG  panel {t}", fontsize=9)
    ax[3].plot(B, rn, '-o', ms=3); ax[3].axhline(thr, color='r', ls=':')
    ax[3].axvspan(cen_lo, cen_hi, color='y', alpha=.2)
    ax[3].set_title("single-wave fit residual vs B (low = pure central region)", fontsize=9)
    ax[3].set_xlabel("B (T)"); ax[3].set_xlim(BMIN, BMAX)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "recovered-panels.png", dpi=110)
    print("\nsaved figures/recovered-panels.png")

    return dict(A0=A0, dad=dad, Bc=Bc, cen_w=(cen_hi-cen_lo), alpha=alpha, slope=slope)


if __name__ == "__main__":
    main()
