"""Reproduce the numerical results of Nakamura et al., arXiv:2006.14115v1.

"Direct observation of anyonic braiding statistics at the nu=1/3 fractional
quantum Hall state."

The paper's only genuine *simulation* is Supplementary Discussion 2 / Supp.
Fig. 5: a thermal average of the interferometer conductance over the localized
quasiparticle number N_qp.  This script reproduces that simulation and also
cross-checks every analytic number quoted in Supp. Discussions 1-3
(lever arms, oscillation periods, transition slope, edge velocity, T_0).

Model (Supp. Eqns. 3-7):

    theta(N_qp)   = 2*pi*(e*/e)*A_I*B/Phi_0 + N_qp*theta_anyon          (Eqn 4)
    dq_net(N_qp)  = nu*A_I*B/Phi_0 + (e*/e)*N_qp - q_donor - a_bulk*dVg (Eqn 3, in units of e)
    E(N_qp)       = (e^2/2C)*dq_net^2 + Delta_qp*|N_qp|                  (Eqn 7, E_0 dropped)
    <dG>          = (1/Z) sum_N exp(-E/kT) cos(theta)                    (Eqn 5)
    Z             = sum_N exp(-E/kT)                                     (Eqn 6)

Units: energies are carried in Kelvin (E_c, Delta_qp), so exp(-E/kT) uses E[K]/T[K].
We work in the reduced variable Etilde = E/E_c, so exp(-Etilde / (kT/E_c)).
The control parameter kT/E_c is the one the paper sets to 0.002, 0.02, 0.1.

Only numpy + matplotlib are required (both already installed).
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pathlib import Path

# --------------------------------------------------------------------------- #
# Physical constants (SI)
# --------------------------------------------------------------------------- #
E_CHG = 1.602176634e-19      # elementary charge [C]
H_PLANCK = 6.62607015e-34    # Planck constant [J s]
HBAR = H_PLANCK / (2 * np.pi)
KB = 1.380649e-23            # Boltzmann constant [J/K]
EPS0 = 8.8541878128e-12      # vacuum permittivity [F/m]
PHI0 = H_PLANCK / E_CHG      # flux quantum h/e [Wb = T m^2]
EPS_R_GAAS = 12.9            # static dielectric constant of GaAs

# --------------------------------------------------------------------------- #
# Parameters quoted in the paper (Supp. Discussion 1 & 2)
# --------------------------------------------------------------------------- #
NU = 1.0 / 3.0               # filling factor
ESTAR_OVER_E = 1.0 / 3.0     # fractional charge e* = e/3
THETA_ANYON = 2 * np.pi / 3  # anyonic braiding phase
DELTA_GAP_K = 5.5            # full nu=1/3 transport gap [K] (Supp. Fig. 3)
DELTA_QP_K = DELTA_GAP_K / 2 # quasiparticle gap Delta_qp = Delta/2 = 2.75 K

N_2DES = 0.7e11 * 1e4        # 2DES density 0.7e11 cm^-2 -> m^-2 (sets q_donor)
D_SETBACK = 48e-9            # screening-layer setback from main well [m]

A0_SIM = 0.1e-12             # area A_0 = 0.1 um^2 stated in paper for the sim
A0_REAL = 0.38e-12           # real device area from AB period [m^2]
DA_DVG = 0.167e-12 / 1.0     # REAL-device dA/dVg = 0.167 um^2/V (Supp. Disc. 1)
ALPHA_BULK = 0.07e3          # a_bulk = 0.07 mV^-1 = 70 V^-1  [1/V]

# --------------------------------------------------------------------------- #
# PIXEL-FITTED parameters (fit the 5 geometric knobs to the published pixels)
# --------------------------------------------------------------------------- #
# Each parameter is inverted from a robust observable measured directly off the
# three Supp. Fig. 5 panels (jet-inverted; see fit_to_pixels.py / compare_fit.py;
# temperatures held fixed at kT/E_c = 0.002/0.02/0.1):
#   central B-period   127 mT          -> A_0          = 0.098 um^2
#   central Vg-period  12.2 mV         -> dA/dVg       = 0.120 um^2/V
#   carrier slope      -95 mV/T        (= -A_0/(B dA/dVg), follows from above)
#   central width      447 mT          -> Delta_qp/E_c = 1.07
#   side Vg-period     9.7 mV          -> alpha_bulk   = 0.10 mV^-1
#                                         (2nd/transition slope ~ +75 mV/T)
#   central location                   -> B_center     = 8.653 T
A0_FIG = 0.098e-12           # [m^2]   central B-period 127 mT
DA_DVG_FIG = 0.120e-12       # [m^2/V] central Vg-period 12.2 mV, slope -95 mV/T
ALPHA_BULK_FIG = 0.10e3      # [1/V]   side Vg-period 9.7 mV, transition slope +75

# Field / gate window of Supp. Fig. 5
B_MIN, B_MAX = 8.2, 9.1      # [T]
VG_MIN, VG_MAX = -30.0, 0.0  # side-gate voltage dVg [mV] (matches the crops)

N_QP_MAX = 20                # truncate the infinite sum to [-20, +20]
RATIOS = [0.002, 0.02, 0.1]  # kT / E_c values for panels a, b, c


# --------------------------------------------------------------------------- #
# Derived energy scales
# --------------------------------------------------------------------------- #
def charging_energy_K(area_m2: float) -> float:
    """E_c = e^2 / 2C with C = 2*eps*A_I/d  (Supp. Discussion 2). Returned in K."""
    eps = EPS0 * EPS_R_GAAS
    C = 2 * eps * area_m2 / D_SETBACK
    Ec_J = E_CHG**2 / (2 * C)
    return Ec_J / KB


EC_K = charging_energy_K(A0_SIM)        # naive charging energy in Kelvin (~1.95 K)
DELTA_QP_OVER_EC = DELTA_QP_K / EC_K    # naive ratio ~1.41 (=> central ~565 mT)

# Centre of the AB region, fit from the central-region location in the pixels.
B_CENTER = 8.653                         # [T]

# Central-region width knob.  With A_0 = A0_FIG = 0.098 um^2, Delta_qp/E_c = 1.07
# makes the pure-AB core ~447 mT wide (matches the measured central region).
DELTA_QP_OVER_EC_FIG = 1.07


# --------------------------------------------------------------------------- #
# Core simulation: thermal-averaged conductance and <N_qp>
# --------------------------------------------------------------------------- #
def simulate(ratio_kT_Ec, nB=400, nV=300, area0=A0_FIG,
             dqe=DELTA_QP_OVER_EC_FIG, q_donor=None, dadvg=DA_DVG_FIG,
             alpha_bulk=ALPHA_BULK_FIG, b_center=B_CENTER,
             vmin=VG_MIN, vmax=VG_MAX):
    """Return (B[T], Vg[mV], <dG>[v,b] a.u., <N_qp>[v,b]) for one kT/E_c ratio.

    dqe        = Delta_qp / E_c  (width of the pure-AB central region).
    dadvg      = dA/dVg          (stripe slope and the Vg period).
    alpha_bulk = bulk lever arm [1/V] (transition-line slope, side-region period).
    b_center   = field at which the AB region is centred (sets q_donor).
    q_donor (units of e); if None it is derived from area0 & b_center.
    """
    if q_donor is None:
        q_donor = NU * area0 * b_center / PHI0   # centre at b_center
    B = np.linspace(B_MIN, B_MAX, nB)            # [T]
    Vg = np.linspace(vmin, vmax, nV)             # [mV], increasing -> top of plot

    # Interferometer area depends on gate voltage: A_I = A0 + (dA/dVg)*dVg.
    A_I = area0 + dadvg * (Vg * 1e-3)            # Vg in mV -> V; shape (nV,)

    # Broadcast to grids indexed [v, b].
    A_grid = A_I[:, None]                        # (nV, 1)
    B_grid = B[None, :]                          # (1, nB)
    Vg_grid = Vg[:, None]                        # (nV, 1) [mV]

    flux_charge = NU * A_grid * B_grid / PHI0    # nu*A_I*B/Phi0 (condensate charge / e)
    ab_phase = 2 * np.pi * ESTAR_OVER_E * A_grid * B_grid / PHI0  # AB phase

    # static offset of dq_net that does NOT depend on N_qp
    offset = flux_charge - q_donor - alpha_bulk * (Vg_grid * 1e-3)  # (nV, nB)

    N = np.arange(-N_QP_MAX, N_QP_MAX + 1)       # (nN,)
    N_b = N[None, None, :]                        # (1, 1, nN)

    dq_net = offset[:, :, None] + ESTAR_OVER_E * N_b           # (nV, nB, nN)
    Etilde = dq_net**2 + dqe * np.abs(N_b)                     # E / E_c
    # exp(-E/kT) = exp(-Etilde / (kT/Ec)); subtract per-pixel min for stability.
    expo = -Etilde / ratio_kT_Ec
    expo -= expo.max(axis=2, keepdims=True)
    w = np.exp(expo)                                          # Boltzmann weights

    Z = w.sum(axis=2)                                         # (nV, nB)
    phase = ab_phase[:, :, None] + N_b * THETA_ANYON
    dG = (w * np.cos(phase)).sum(axis=2) / Z                  # <dG> (a.u.)
    Nqp = (w * N_b).sum(axis=2) / Z                           # <N_qp>

    return B, Vg, dG, Nqp


# --------------------------------------------------------------------------- #
# Analytic cross-checks (reproduce numbers stated in the paper)
# --------------------------------------------------------------------------- #
def analytic_checks():
    lines = []
    add = lines.append
    add("=" * 70)
    add("ANALYTIC CROSS-CHECKS  (computed value  vs  paper value)")
    add("=" * 70)

    # --- Derived energy scales --------------------------------------------- #
    q_donor_fig = NU * A0_FIG * B_CENTER / PHI0
    add(f"\n[Energy scales]")
    add(f"  naive: A_0={A0_SIM*1e12:.2f} um^2, E_c=e^2/2C={EC_K:.2f} K,"
        f" Delta_qp/E_c={DELTA_QP_OVER_EC:.2f} -> central ~565 mT (paper text 530)")
    add(f"  Delta_qp      = {DELTA_QP_K:.3f} K   (= Delta/2)")
    add(f"\n[Pixel-fitted knobs]  (5 geometric params fit to Supp. Fig. 5 panels)")
    add(f"  A_0           = {A0_FIG*1e12:.3f} um^2   (B-period 127 mT; data 127)")
    add(f"  dA/dVg        = {DA_DVG_FIG*1e12:.3f} um^2/V (Vg-period 12.2 mV; data 12.2)")
    add(f"  Delta_qp/E_c  = {DELTA_QP_OVER_EC_FIG:.2f}        (central 447 mT; data 447)")
    add(f"  alpha_bulk    = {ALPHA_BULK_FIG/1e3:.3f} mV^-1 (side Vg-period 9.7 mV; data 9.7)")
    add(f"  B_center      = {B_CENTER} T     (q_donor/e = {q_donor_fig:.1f})")
    slope_fig = -A0_FIG / (B_CENTER * DA_DVG_FIG) * 1e3
    tslope = NU * A0_FIG / (PHI0 * ALPHA_BULK_FIG) * 1e3
    add(f"  => two slopes: AB carrier {slope_fig:.0f} mV/T (data -95),"
        f" transition +{tslope:.0f} mV/T")
    add(f"  kT/E_c=0.002,0.02,0.1 -> T = "
        f"{0.002*EC_K*1e3:.1f}, {0.02*EC_K*1e3:.1f}, {0.1*EC_K*1e3:.0f} mK")

    # --- Lever arms (Supp. Discussion 1) ----------------------------------- #
    # dA/dVg from nu=1 AB period 8.0 mV at B=3.1 T
    B_nu1, dVg_nu1 = 3.1, 8.0e-3
    dA_dVg = PHI0 / (B_nu1 * dVg_nu1)
    n_nu1 = E_CHG * B_nu1 / H_PLANCK              # density at nu=1
    alpha_edge = n_nu1 * dA_dVg                   # [1/V]
    alpha_total = 0.19e3                          # from 5.4 mV CB period (paper)
    alpha_bulk = alpha_total - alpha_edge
    add("\n[Lever arms]")
    add(f"  dA/dVg     = {dA_dVg*1e12:.3f} um^2/V     (paper 0.167)")
    add(f"  alpha_edge = {alpha_edge*1e-3:.3f} mV^-1   (paper 0.12)")
    add(f"  alpha_bulk = {alpha_bulk*1e-3:.3f} mV^-1   (paper 0.07)")

    # --- Predicted side-gate oscillation periods --------------------------- #
    # central (only AB term): dVg = (Phi0/B)(e/e*)(dA/dVg)^-1
    def period_central(B):
        return (PHI0 / B) * (1 / ESTAR_OVER_E) / DA_DVG * 1e3   # mV
    # high/low field (AB + quasiparticle term)
    def period_qp(B):
        denom = (B / (3 * PHI0)) * DA_DVG + ALPHA_BULK          # [1/V]
        return 1.0 / denom * 1e3                                # mV
    add("\n[Side-gate oscillation periods]")
    add(f"  central  B=8.85T: dVg = {period_central(8.85):.2f} mV   (paper 8.4, meas 8.5)")
    add(f"  low  fld B=8.40T: dVg = {period_qp(8.40):.2f} mV   (paper 5.5, meas 5.8)")
    add(f"  high fld B=9.30T: dVg = {period_qp(9.30):.2f} mV   (paper 5.1, meas 5.4)")

    # --- Quasiparticle transition-line slope ------------------------------- #
    slope = NU * A0_REAL / (PHI0 * ALPHA_BULK)    # V/T
    add("\n[Transition-line slope dVg/dB]  (A = 0.38 um^2)")
    add(f"  dVg/dB = {slope*1e3/1e3:.3f} mV/mT      (paper 0.44, meas ~0.5)")

    # --- Central region width (set by the gap) ----------------------------- #
    # width in dq_net where N_qp stays 0: 1/3 + 3*(Delta_qp/E_c); convert to B.
    width_n = 1.0 / 3.0 + 3.0 * DELTA_QP_OVER_EC
    dB_central = width_n * PHI0 / (NU * A0_SIM)
    add("\n[Central 'pure AB' region width]")
    add(f"  Delta B_central = {dB_central*1e3:.0f} mT   (paper ~530, meas ~450)")

    # --- Edge velocities (Supp. Discussion 3) ------------------------------ #
    L = 4 * np.sqrt(A0_REAL)                      # perimeter ~2.5 um
    def v_edge(dVsd):                             # dVsd in V
        return ESTAR_OVER_E * E_CHG * L * dVsd / (2 * np.pi * HBAR)
    add(f"\n[Edge velocity]  L = 4*sqrt(A) = {L*1e6:.2f} um")
    for B, dVsd, paper in [(8.4, 41e-6, 8.3), (8.85, 48e-6, 9.7), (9.3, 46e-6, 9.3)]:
        v = v_edge(dVsd)
        add(f"  B={B:>4}T  dVsd={dVsd*1e6:.0f}uV -> v = {v/1e3:.1f}e3 m/s  (paper {paper}e3)")

    # --- Predicted T_0 from edge thermal smearing -------------------------- #
    # T_0 = h/(2*pi*kB*tau) * (1/g), tau = L/v, g = 1/3
    g_exp = 1.0 / 3.0
    add("\n[Predicted T_0 from edge smearing]  g = 1/3")
    for B, dVsd, paper in [(8.4, 41e-6, 76), (8.85, 48e-6, 89), (9.3, 46e-6, 85)]:
        v = v_edge(dVsd)
        tau = L / v
        T0 = H_PLANCK / (2 * np.pi * KB * tau) / g_exp
        add(f"  B={B:>4}T  v={v/1e3:.1f}e3 -> T_0 = {T0*1e3:.0f} mK   (paper {paper})")

    add("\n  (measured T_0: 31 mK low / 94 mK center / 32 mK high field --")
    add("   low & high field measured << predicted => topological dephasing.)")
    add("=" * 70)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Plotting: reproduce Supp. Fig. 5 (panels a, b, c, d) + a schematic e
# --------------------------------------------------------------------------- #
def make_figure(out_path: Path):
    sims = [simulate(r) for r in RATIOS]
    B = sims[0][0]

    fig = plt.figure(figsize=(13, 7.5))
    gs = gridspec.GridSpec(3, 2, width_ratios=[1.7, 1.0],
                           height_ratios=[1, 1, 1], hspace=0.32, wspace=0.22)

    labels = ['a)', 'b)', 'c)']
    region_titles = (r"Quasiparticle region $\Phi_0$ period      "
                     r"Pure AB region $3\Phi_0$ period      "
                     r"Quasihole region $\Phi_0$ period")
    for i, (r, (Bv, Vg, dG, Nqp)) in enumerate(zip(RATIOS, sims)):
        ax = fig.add_subplot(gs[i, 0])
        vmax = np.abs(dG).max()
        im = ax.imshow(dG, extent=[B_MIN, B_MAX, VG_MIN, VG_MAX],
                       origin='lower', aspect='auto', cmap='jet',
                       vmin=-vmax, vmax=vmax)
        ax.set_ylabel(r'$\delta V_g$ (mV)')
        ax.text(-0.07, 1.02, labels[i], transform=ax.transAxes,
                fontsize=14, fontweight='bold', va='bottom')
        ax.text(0.99, 0.04, rf'$k_BT/E_c={r}$', transform=ax.transAxes,
                ha='right', va='bottom', color='w', fontsize=9,
                bbox=dict(fc='k', alpha=0.4, lw=0))
        if i == 0:
            ax.set_title(region_titles, fontsize=8.5, pad=8)
        if i == 2:
            ax.set_xlabel(r'$B$ (T)')
        fig.colorbar(im, ax=ax, pad=0.01, fraction=0.04,
                     label=r'$\delta G$ (a.u.)')

    # Panel d: <N_qp> vs B (line cut at dVg = 0, i.e. top row).
    axd = fig.add_subplot(gs[0, 1])
    colors = ['k', 'tab:blue', 'tab:red']
    for r, (Bv, Vg, dG, Nqp), c in zip(RATIOS, sims, colors):
        axd.plot(Bv, Nqp[-1, :], color=c, lw=1.6, label=rf'$T/E_c={r}$')
    axd.axhline(0, color='0.6', lw=0.7)
    axd.set_xlabel(r'$B$ (T)')
    axd.set_ylabel(r'$\langle N_{qp}\rangle$')
    axd.text(-0.18, 1.02, 'd)', transform=axd.transAxes,
             fontsize=14, fontweight='bold', va='bottom')
    axd.legend(fontsize=8, loc='upper right')
    axd.set_xlim(B_MIN, B_MAX)

    # Panel e: qualitative density of states (schematic, matches paper).
    axe = fig.add_subplot(gs[1:, 1])
    energy = np.linspace(-3, 3, 600)

    def gauss(x, mu, s=0.35):
        return np.exp(-((x - mu) ** 2) / (2 * s ** 2))

    for shift, c, lab, off in [(-1.0, 'tab:blue', 'Low field', 0.0),
                               (0.0, 'k', 'Center', 1.4),
                               (1.0, 'tab:red', 'High field', 2.8)]:
        dos = gauss(energy, -1.2 + shift) + gauss(energy, 1.2 + shift)
        axe.fill_between(energy, off, dos + off, color=c, alpha=0.35)
        axe.plot(energy, dos + off, color=c, lw=1.2, label=lab)
    axe.axvline(0, color='0.3', ls='--', lw=1)
    axe.text(0.02, 0.97, r'$\mu$', transform=axe.transAxes, va='top')
    axe.text(0.5, -0.04, 'Energy', transform=axe.transAxes, ha='center')
    axe.set_yticks([])
    axe.set_ylabel('Density of States')
    axe.text(-0.1, 1.02, 'e)', transform=axe.transAxes,
             fontsize=14, fontweight='bold', va='bottom')
    axe.legend(fontsize=8, loc='upper right')

    fig.suptitle("Reproduction of Supp. Fig. 5 "
                 "(Nakamura et al. 2020, arXiv:2006.14115v1)", fontsize=11)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"saved -> {out_path}")

    # Report the simulated central-region width for comparison with ~530 mT.
    _, _, _, Nqp0 = sims[0]
    nq_top = Nqp0[-1, :]
    central = B[np.abs(nq_top) < 0.5]
    if central.size:
        print(f"simulated central |<N_qp>|<0.5 width: "
              f"{(central.max()-central.min())*1e3:.0f} mT "
              f"({central.min():.3f}-{central.max():.3f} T)")


def main():
    out_dir = Path(__file__).parent / 'figures'
    out_dir.mkdir(exist_ok=True)
    print(analytic_checks())
    print()
    make_figure(out_dir / 'repro-supp-fig5.png')


if __name__ == '__main__':
    main()
