/* shared/physics.js -- Fabry-Perot interferometer thermal-average model
 * Nakamura et al. 2020 (arXiv:2006.14115), Supp. Discussion 2.
 *
 *   E(N)/E_c = dq_net^2 + (Delta_qp/E_c)|N|
 *   dq_net   = nu A_I B/Phi0 + estar N - q_donor - alpha_bulk dV_g   [estar = e_star/e]
 *   <dG>     = (1/Z) Sum_N exp(-E(N)/kT) cos(2pi estar A_I B/Phi0 + N theta_anyon)
 *
 * Exposed as the global object `FQH` (plain script, works over file://).
 * ASCII-only on purpose (avoids charset issues under file://).
 */
"use strict";
var FQH = (function () {
  // --- physical constants (SI) ---
  const E = 1.602176634e-19, H = 6.62607015e-34, KB = 1.380649e-23,
        EPS0 = 8.8541878128e-12, EPSR = 12.9, PHI0 = H / E, D = 48e-9;
  // --- ν = 1/3 defaults ---
  const NU = 1 / 3, ESTAR = 1 / 3, THETA = 2 * Math.PI / 3, NMAX = 20;
  // --- default field / gate window (matches the published panels) ---
  const BMIN = 8.2, BMAX = 9.1, VTOP = 0, VBOT = -30;   // B in T, δV_g in mV
  // --- pixel-fitted geometric parameters (see reproduce_simulation.py) ---
  const FIT = { A0: 0.098e-12, dad: 0.120e-12, dqe: 1.07, Bc: 8.653, ab: 0.100,
                ratio: 0.02 };

  // charging energy E_c = e²/2C  (C = 2εA₀/d), returned in Kelvin
  function Ec_K(A0) { const C = 2 * EPS0 * EPSR * A0 / D; return (E * E / (2 * C)) / KB; }

  // fill model params with ν-defaults
  function norm(p) {
    const nu = p.nu !== undefined ? p.nu : NU;
    return {
      A0: p.A0, dad: p.dad, dqe: p.dqe, ab: p.ab, ratio: p.ratio,
      Bc: p.Bc, nu: nu,
      estar: p.estar !== undefined ? p.estar : ESTAR,
      theta: p.theta !== undefined ? p.theta : THETA,
      qd:    p.qd    !== undefined ? p.qd    : nu * p.A0 * p.Bc / PHI0,  // hoisted (per norm, not per pixel)
      nmax:  p.nmax  !== undefined ? p.nmax  : NMAX
    };
  }

  // thermal average at a single (B [T], Vg [mV]); returns {dG, N}
  function point(B, Vg, P) {
    const A_I = P.A0 + P.dad * (Vg * 1e-3);
    const abp = 2 * Math.PI * P.estar * A_I * B / PHI0;
    const fc  = P.nu * A_I * B / PHI0;
    const off = fc - P.qd - P.ab * Vg;
    const Nstar = Math.round(-off / P.estar);
    const lo = Math.max(-P.nmax, Nstar - 16), hi = Math.min(P.nmax, Nstar + 16);
    let minE = Infinity;
    for (let N = lo; N <= hi; N++) { const dq = off + P.estar * N; const Et = dq * dq + P.dqe * Math.abs(N); if (Et < minE) minE = Et; }
    let Z = 0, gs = 0, ns = 0;
    for (let N = lo; N <= hi; N++) {
      const dq = off + P.estar * N; const Et = dq * dq + P.dqe * Math.abs(N);
      const w = Math.exp(-(Et - minE) / P.ratio);
      Z += w; gs += w * Math.cos(abp + N * P.theta); ns += w * N;
    }
    return { dG: gs / Z, N: ns / Z };
  }

  // full heat-map over the (B, Vg) window.
  // returns {dG:Float32Array(nB*nV) row-major (row0 = Vg=VTOP/top), nqpTop:Float64Array(nB), vmax}
  function grid(p, nB, nV, win) {
    win = win || { bmin: BMIN, bmax: BMAX, vtop: VTOP, vbot: VBOT };
    const P = norm(p);
    const dG = new Float32Array(nB * nV), nq = new Float64Array(nB);
    let vmax = 1e-9;
    for (let iy = 0; iy < nV; iy++) {
      const Vg = win.vtop + (win.vbot - win.vtop) * iy / (nV - 1);
      for (let ix = 0; ix < nB; ix++) {
        const B = win.bmin + (win.bmax - win.bmin) * ix / (nB - 1);
        const r = point(B, Vg, P);
        dG[iy * nB + ix] = r.dG;
        if (Math.abs(r.dG) > vmax) vmax = Math.abs(r.dG);
        if (iy === 0) nq[ix] = r.N;
      }
    }
    return { dG: dG, nqpTop: nq, vmax: vmax };
  }

  // line cut δG, ⟨N⟩ vs δV_g at fixed B
  function lineVsVg(B, p, nV, win) {
    win = win || { vtop: VTOP, vbot: VBOT };
    const P = norm(p), g = new Float64Array(nV), n = new Float64Array(nV), v = new Float64Array(nV);
    for (let i = 0; i < nV; i++) {
      const Vg = win.vtop + (win.vbot - win.vtop) * i / (nV - 1);
      const r = point(B, Vg, P); g[i] = r.dG; n[i] = r.N; v[i] = Vg;
    }
    return { Vg: v, dG: g, N: n };
  }

  // analytic derived quantities (for read-outs)
  function derived(p) {
    const P = norm(p);
    return {
      slope: -P.A0 / (P.Bc * P.dad) * 1e3,                 // AB carrier slope, mV/T
      Bper:  PHI0 / (P.estar * P.A0) * 1e3,                  // B period, mT
      Vper:  PHI0 / (P.estar * P.Bc * P.dad) * 1e3,          // Vg period, mV
      cen:   (P.estar + P.dqe / P.estar) * PHI0 / (P.estar * P.A0) * 1e3, // central width, mT (approx)
      transSlope: P.nu * P.A0 / (PHI0 * (P.ab * 1e3)) * 1e3, // transition slope dVg/dB, mV/T
      Ec:    Ec_K(P.A0),                                     // K
      qd:    P.nu * P.A0 * P.Bc / PHI0
    };
  }

  return {
    E: E, H: H, KB: KB, EPS0: EPS0, EPSR: EPSR, PHI0: PHI0, D: D,
    NU: NU, ESTAR: ESTAR, THETA: THETA, NMAX: NMAX,
    BMIN: BMIN, BMAX: BMAX, VTOP: VTOP, VBOT: VBOT, FIT: FIT,
    Ec_K: Ec_K, point: point, grid: grid, lineVsVg: lineVsVg, derived: derived, norm: norm
  };
})();
if (typeof module !== "undefined" && module.exports) module.exports = FQH;  // node test
