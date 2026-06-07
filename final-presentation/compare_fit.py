"""Render the model at the pixel-fitted parameters and compare to the data."""
import numpy as np
import matplotlib.pyplot as plt
from fit_to_pixels import load_panel, BMIN, BMAX
from reproduce_simulation import simulate

# parameters fit directly from the pixels (robust per-observable inversion)
FIT = dict(area0=0.098e-12, dadvg=0.120e-12, dqe=1.066,
           alpha_bulk=100.0, b_center=8.653, vmin=-30.0, vmax=0.0)   # alpha=0.10 mV^-1
TEMPS = [0.002, 0.02, 0.1]

DATA = [load_panel(n) for n in "abc"]
H, W = DATA[0].shape

fig, axs = plt.subplots(3, 2, figsize=(12, 7.2))
ext = [BMIN, BMAX, -30, 0]
for i, (D, r) in enumerate(zip(DATA, TEMPS)):
    _, _, dG, _ = simulate(r, nB=W, nV=H, **FIT)
    axs[i, 0].imshow(D, extent=ext, origin='upper', aspect='auto',
                     cmap='jet', vmin=-1, vmax=1)
    vmax = np.abs(dG).max()
    axs[i, 1].imshow(dG[::-1], extent=ext, origin='upper', aspect='auto',
                     cmap='jet', vmin=-vmax, vmax=vmax)
    axs[i, 0].set_ylabel(f"panel {'abc'[i]}\n" + r"$\delta V_g$ (mV)")
    axs[i, 0].set_title(f"DATA (pixels)   kT/E_c={r}", fontsize=9)
    axs[i, 1].set_title(f"FITTED MODEL", fontsize=9)
for ax in axs[2]:
    ax.set_xlabel("B (T)")
fig.suptitle("Pixel fit: A0=0.098 um^2, dA/dVg=0.120 um^2/V, "
             "Dqp/Ec=1.07, alpha_bulk=0.10 mV^-1, B_center=8.653 T", fontsize=10)
fig.tight_layout()
fig.savefig("figures/fit-vs-data.png", dpi=120)
print("saved figures/fit-vs-data.png")
