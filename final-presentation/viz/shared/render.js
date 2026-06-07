/* shared/render.js — small Canvas helpers shared by the visualizations.
 * Exposed as the global `VZ`. Plain script (file:// friendly).
 */
"use strict";
var VZ = (function () {

  // matplotlib-style "jet" colormap, t in [0,1] -> writes RGBA at out[o..o+3]
  function jet(t, out, o) {
    if (t < 0) t = 0; else if (t > 1) t = 1;
    const r = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 3)));
    const g = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 2)));
    const b = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 1)));
    out[o] = r * 255; out[o + 1] = g * 255; out[o + 2] = b * 255; out[o + 3] = 255;
  }
  // jet as a css color string (for legends/colorbars)
  function jetCss(t) {
    const a = [0, 0, 0, 0]; jet(t, a, 0);
    return "rgb(" + (a[0] | 0) + "," + (a[1] | 0) + "," + (a[2] | 0) + ")";
  }

  // offscreen heat-map buffer
  function makeHeatmap(nx, ny) {
    const buf = document.createElement("canvas"); buf.width = nx; buf.height = ny;
    const bctx = buf.getContext("2d"); const img = bctx.createImageData(nx, ny);
    return { buf: buf, bctx: bctx, img: img, nx: nx, ny: ny };
  }
  // paint Float array into the buffer. mode 'div' -> [-vmax,vmax], 'seq' -> [0,vmax]
  function paintHeatmap(hm, data, vmax, mode) {
    const d = hm.img.data, n = hm.nx * hm.ny, div = mode !== "seq";
    for (let i = 0; i < n; i++) {
      const t = div ? (data[i] + vmax) / (2 * vmax) : data[i] / vmax;
      jet(t, d, i * 4);
    }
    hm.bctx.putImageData(hm.img, 0, 0);
  }

  // draw a framed plot box with ticks + labels.
  // g = {x,y,w,h}  ax = {xr:[lo,hi], yr:[lo,hi], xstep, ystep, xlabel, ylabel,
  //                      xfmt, yfmt, color}
  function frame(ctx, g, ax) {
    const col = ax.color || "#888", ink = "#cbd3df";
    ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.strokeRect(g.x, g.y, g.w, g.h);
    ctx.fillStyle = ink; ctx.font = "11px sans-serif";
    const xfmt = ax.xfmt || (v => v.toFixed(1));
    const yfmt = ax.yfmt || (v => v.toFixed(0));
    const X = v => g.x + (v - ax.xr[0]) / (ax.xr[1] - ax.xr[0]) * g.w;
    const Y = v => g.y + (ax.yr[1] - v) / (ax.yr[1] - ax.yr[0]) * g.h;
    if (ax.xstep) {
      ctx.textAlign = "center"; ctx.textBaseline = "top";
      for (let v = ax.xr[0]; v <= ax.xr[1] + 1e-9; v += ax.xstep) {
        const x = X(v); ctx.beginPath(); ctx.moveTo(x, g.y + g.h); ctx.lineTo(x, g.y + g.h + 4); ctx.stroke();
        ctx.fillText(xfmt(v), x, g.y + g.h + 6);
      }
    }
    if (ax.ystep) {
      ctx.textAlign = "right"; ctx.textBaseline = "middle";
      for (let v = ax.yr[0]; v <= ax.yr[1] + 1e-9; v += ax.ystep) {
        const y = Y(v); ctx.beginPath(); ctx.moveTo(g.x - 4, y); ctx.lineTo(g.x, y); ctx.stroke();
        ctx.fillText(yfmt(v), g.x - 6, y);
      }
    }
    if (ax.xlabel) { ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText(ax.xlabel, g.x + g.w / 2, g.y + g.h + 26); }
    if (ax.ylabel) { ctx.save(); ctx.translate(g.x - 34, g.y + g.h / 2); ctx.rotate(-Math.PI / 2); ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText(ax.ylabel, 0, 0); ctx.restore(); }
    return { X: X, Y: Y };
  }

  // vertical jet colorbar at (x,y,w,h) labelled lo..hi
  function colorbar(ctx, x, y, w, h, lo, hi, label) {
    for (let i = 0; i < h; i++) { const t = 1 - i / (h - 1); ctx.fillStyle = jetCss(t); ctx.fillRect(x, y + i, w, 1); }
    ctx.strokeStyle = "#888"; ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = "#cbd3df"; ctx.font = "10px sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.fillText(hi, x + w + 4, y + 4); ctx.fillText(lo, x + w + 4, y + h - 4);
    if (label) { ctx.save(); ctx.translate(x + w + 26, y + h / 2); ctx.rotate(-Math.PI / 2); ctx.textAlign = "center"; ctx.fillText(label, 0, 0); ctx.restore(); }
  }

  // HiDPI canvas setup: returns the 2d context scaled to css pixels
  function hidpi(canvas, cssW, cssH) {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = cssW * dpr; canvas.height = cssH * dpr;
    canvas.style.width = cssW + "px"; canvas.style.height = cssH + "px";
    const ctx = canvas.getContext("2d"); ctx.scale(dpr, dpr); return ctx;
  }

  return { jet: jet, jetCss: jetCss, makeHeatmap: makeHeatmap, paintHeatmap: paintHeatmap,
           frame: frame, colorbar: colorbar, hidpi: hidpi };
})();
