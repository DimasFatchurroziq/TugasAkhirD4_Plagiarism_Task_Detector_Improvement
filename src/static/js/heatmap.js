/**
 * static/js/heatmap.js
 * ─────────────────────────────────────────────────────────────────
 * Engine rendering similarity heatmap di atas <canvas>.
 *
 * Data masuk dari template Jinja2 via variabel global:
 *   PAIRS_DATA  → list[{file_a, file_b, sim, status, note, action}]
 *   FILES_DATA  → list[string]  (nama file unik, urutan awal)
 *
 * API publik (dipanggil dari results.html):
 *   hmInit()              → render pertama kali
 *   hmSetThreshold(val)   → ubah ambang sorot
 *   hmSort(mode)          → ubah urutan file
 *   hmPalette(name)       → ganti skema warna
 *   hmDownload()          → unduh canvas sebagai PNG
 * ─────────────────────────────────────────────────────────────────
 */

/* ═══════════════════════════════════════════════════════════════
   1. STATE
═══════════════════════════════════════════════════════════════ */
const HM = {
  threshold: 0,
  sortMode:  'name',
  palette:   'redgreen',
  files:     [],          // nama file terurut
  matrix:    {},          // matrix[fileA][fileB] = { sim, note, action }
  cellSize:  0,
  labelW:    0,
  initialized: false,
};

/* ═══════════════════════════════════════════════════════════════
   2. COLOR SCALES
═══════════════════════════════════════════════════════════════ */
const PALETTES = {
  redgreen: {
    label: 'Merah–Hijau',
    gradient: 'linear-gradient(to right, #E1F5EE, #EF9F27, #E24B4A)',
    fn: (v) => {
      // 0→hijau, 40→kuning, 70→oranye, 100→merah tua
      if (v < 40)  return lerpColor('#E1F5EE', '#EF9F27', v / 40);
      if (v < 70)  return lerpColor('#EF9F27', '#E24B4A', (v - 40) / 30);
      return       lerpColor('#E24B4A', '#A32D2D', (v - 70) / 30);
    },
  },
  heatmap: {
    label: 'Heatmap',
    gradient: 'linear-gradient(to right, #042C53, #185FA5, #EF9F27, #E24B4A, #791F1F)',
    fn: (v) => {
      const stops = [
        [0,   '#042C53'],
        [25,  '#185FA5'],
        [50,  '#EF9F27'],
        [75,  '#E24B4A'],
        [100, '#791F1F'],
      ];
      for (let i = 0; i < stops.length - 1; i++) {
        const [t0, c0] = stops[i];
        const [t1, c1] = stops[i + 1];
        if (v <= t1) return lerpColor(c0, c1, (v - t0) / (t1 - t0));
      }
      return stops[stops.length - 1][1];
    },
  },
  blue: {
    label: 'Biru',
    gradient: 'linear-gradient(to right, #E6F1FB, #378ADD, #042C53)',
    fn: (v) => {
      if (v < 50) return lerpColor('#E6F1FB', '#378ADD', v / 50);
      return       lerpColor('#378ADD', '#042C53', (v - 50) / 50);
    },
  },
};

/** Interpolasi linear antara dua warna hex. */
function lerpColor(hex1, hex2, t) {
  t = Math.max(0, Math.min(1, t));
  const r1 = parseInt(hex1.slice(1, 3), 16);
  const g1 = parseInt(hex1.slice(3, 5), 16);
  const b1 = parseInt(hex1.slice(5, 7), 16);
  const r2 = parseInt(hex2.slice(1, 3), 16);
  const g2 = parseInt(hex2.slice(3, 5), 16);
  const b2 = parseInt(hex2.slice(5, 7), 16);
  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);
  return `rgb(${r},${g},${b})`;
}

/* ═══════════════════════════════════════════════════════════════
   3. BUILD MATRIX
   Mengubah PAIRS_DATA (list pasangan) menjadi matrix simetris
   matrix[A][B] = matrix[B][A] = { sim, note, action }
   Diagonal (A==A) = 100 (file dibandingkan dengan dirinya sendiri)
═══════════════════════════════════════════════════════════════ */
function buildMatrix() {
  const matrix = {};

  // Inisialisasi semua file dengan default 0
  const allFiles = [...FILES_DATA];
  allFiles.forEach(f => {
    matrix[f] = {};
    allFiles.forEach(g => { matrix[f][g] = { sim: 0, note: '', action: false }; });
    matrix[f][f] = { sim: 100, note: 'File yang sama', action: false };
  });

  // Isi dari PAIRS_DATA
  PAIRS_DATA.forEach(p => {
    const entry = { sim: p.sim, note: p.note || '', action: p.action || false };
    if (matrix[p.file_a]) matrix[p.file_a][p.file_b] = entry;
    if (matrix[p.file_b]) matrix[p.file_b][p.file_a] = entry; // simetris
  });

  return matrix;
}

/* ═══════════════════════════════════════════════════════════════
   4. SORT FILES
═══════════════════════════════════════════════════════════════ */
function sortFiles(files, matrix, mode) {
  if (mode === 'name') {
    return [...files].sort((a, b) => a.localeCompare(b));
  }

  // Hitung rata-rata / maks kemiripan per file (exclude diagonal)
  function stats(f) {
    const sims = files.filter(g => g !== f).map(g => matrix[f]?.[g]?.sim ?? 0);
    const avg = sims.reduce((s, v) => s + v, 0) / (sims.length || 1);
    const max = Math.max(...sims);
    return { avg, max };
  }

  if (mode === 'avg_desc') {
    return [...files].sort((a, b) => stats(b).avg - stats(a).avg);
  }
  if (mode === 'max_desc') {
    return [...files].sort((a, b) => stats(b).max - stats(a).max);
  }
  return files;
}

/* ═══════════════════════════════════════════════════════════════
   5. RENDER CANVAS
═══════════════════════════════════════════════════════════════ */
function renderCanvas() {
  const canvas = document.getElementById('hm-canvas');
  if (!canvas) return;
  const ctx   = canvas.getContext('2d');
  const files = HM.files;
  const n     = files.length;
  const pal   = PALETTES[HM.palette];

  // Ukuran cell — responsif tapi tidak terlalu kecil
  const containerW = document.getElementById('hm-container')?.offsetWidth || 800;
  const maxCell    = 56;
  const minCell    = 28;
  const rawCell    = Math.floor((containerW - 160) / n);  // 160 = estimasi label
  const cellSize   = Math.max(minCell, Math.min(maxCell, rawCell));

  // Lebar label — maks 140px, font 11px
  const labelW = Math.min(140, Math.max(80,
    Math.max(...files.map(f => f.length)) * 6.5
  ));

  HM.cellSize = cellSize;
  HM.labelW   = labelW;

  const PAD_TOP  = labelW + 12;  // rotasi 45° label atas
  const PAD_LEFT = labelW + 8;
  const total    = n * cellSize;

  const W = PAD_LEFT + total + 60;
  const H = PAD_TOP  + total + 20;

  // Device pixel ratio untuk layar retina
  const dpr = window.devicePixelRatio || 1;
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, W, H);

  // ── 5.1 Label kolom (atas, diagonal 45°) ──────────────────────
  ctx.save();
  ctx.font = '11px "DM Sans", sans-serif';
  ctx.fillStyle = '#6C757D';
  ctx.textAlign = 'left';

  files.forEach((f, j) => {
    const x = PAD_LEFT + j * cellSize + cellSize / 2;
    ctx.save();
    ctx.translate(x, PAD_TOP - 8);
    ctx.rotate(-Math.PI / 4);
    // Truncate label jika panjang
    const label = f.length > 18 ? f.slice(0, 16) + '…' : f;
    ctx.fillText(label, 0, 0);
    ctx.restore();
  });
  ctx.restore();

  // ── 5.2 Label baris (kiri) ────────────────────────────────────
  ctx.save();
  ctx.font = '11px "DM Sans", sans-serif';
  ctx.textAlign = 'right';

  files.forEach((f, i) => {
    const y = PAD_TOP + i * cellSize + cellSize / 2;
    const label = f.length > 20 ? f.slice(0, 18) + '…' : f;

    // Background label hover (opsional — hanya saat hover di row)
    ctx.fillStyle = '#6C757D';
    ctx.fillText(label, PAD_LEFT - 8, y + 4);
  });
  ctx.restore();

  // ── 5.3 Sel-sel ───────────────────────────────────────────────
  files.forEach((rowFile, i) => {
    files.forEach((colFile, j) => {
      const x = PAD_LEFT + j * cellSize;
      const y = PAD_TOP  + i * cellSize;
      const entry = HM.matrix[rowFile]?.[colFile];
      const sim   = entry?.sim ?? 0;
      const isDiag = rowFile === colFile;

      // Warna fill
      if (isDiag) {
        ctx.fillStyle = '#E9ECEF';
      } else {
        ctx.fillStyle = pal.fn(sim);
      }
      ctx.fillRect(x, y, cellSize, cellSize);

      // Border grid tipis
      ctx.strokeStyle = 'rgba(255,255,255,0.6)';
      ctx.lineWidth   = 0.5;
      ctx.strokeRect(x, y, cellSize, cellSize);

      // Garis sorot threshold
      if (!isDiag && sim >= HM.threshold) {
        ctx.strokeStyle = 'rgba(255,255,255,0.9)';
        ctx.lineWidth   = 1.5;
        ctx.strokeRect(x + 0.75, y + 0.75, cellSize - 1.5, cellSize - 1.5);
      }

      // Teks persentase di dalam sel (hanya jika cukup besar)
      if (cellSize >= 38 && !isDiag) {
        const textColor = sim >= 60
          ? 'rgba(255,255,255,0.95)'
          : 'rgba(0,0,0,0.55)';
        ctx.fillStyle  = textColor;
        ctx.font       = `${cellSize >= 48 ? 12 : 10}px "DM Mono", monospace`;
        ctx.textAlign  = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(sim + '%', x + cellSize / 2, y + cellSize / 2);
      }

      // "×" di diagonal
      if (isDiag) {
        ctx.fillStyle = '#ADB5BD';
        ctx.font      = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('—', x + cellSize / 2, y + cellSize / 2);
      }
    });
  });

  // ── 5.4 Garis pembatas threshold (horizontal & vertikal) ──────
  // Tandai di mana zona "high" dimulai
  ctx.save();
  ctx.setLineDash([4, 3]);
  ctx.strokeStyle = 'rgba(163, 45, 45, 0.4)';
  ctx.lineWidth   = 1;
  // Tidak perlu garis — visual sudah dari warna sel
  ctx.restore();
}

/* ═══════════════════════════════════════════════════════════════
   6. TOOLTIP
═══════════════════════════════════════════════════════════════ */
function attachTooltip() {
  const canvas  = document.getElementById('hm-canvas');
  const tooltip = document.getElementById('hm-tooltip');
  if (!canvas || !tooltip) return;

  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;

    const PAD_LEFT = HM.labelW + 8;
    const PAD_TOP  = HM.labelW + 12;
    const cs = HM.cellSize;

    const col = Math.floor((mx - PAD_LEFT) / cs);
    const row = Math.floor((my - PAD_TOP)  / cs);
    const n   = HM.files.length;

    if (col < 0 || row < 0 || col >= n || row >= n) {
      tooltip.style.display = 'none';
      return;
    }

    const fileA = HM.files[row];
    const fileB = HM.files[col];
    const isDiag = fileA === fileB;

    if (isDiag) {
      tooltip.style.display = 'none';
      return;
    }

    const entry = HM.matrix[fileA]?.[fileB];
    const sim   = entry?.sim ?? 0;

    const simColor = sim >= 70 ? '#E24B4A' : sim >= 40 ? '#EF9F27' : '#1D9E75';
    const statusLabel = sim >= 70 ? 'Sangat Tinggi'
                      : sim >= 40 ? 'Perlu Dicek' : 'Aman';

    tooltip.innerHTML = `
      <div style="margin-bottom:6px;">
        <span style="font-size:11px;color:rgba(255,255,255,.6);">File A</span><br/>
        <strong style="font-size:12px;">${fileA}</strong>
      </div>
      <div style="margin-bottom:8px;">
        <span style="font-size:11px;color:rgba(255,255,255,.6);">File B</span><br/>
        <strong style="font-size:12px;">${fileB}</strong>
      </div>
      <div style="display:flex;align-items:baseline;gap:8px;border-top:0.5px solid rgba(255,255,255,.15);padding-top:8px;">
        <span class="hm-tooltip-sim" style="color:${simColor};">${sim}%</span>
        <span style="font-size:11.5px;color:rgba(255,255,255,.7);">${statusLabel}</span>
      </div>
      ${entry?.note ? `<div style="margin-top:6px;font-size:11px;color:rgba(255,255,255,.6);border-top:0.5px solid rgba(255,255,255,.1);padding-top:6px;">${entry.note}</div>` : ''}
    `;

    // Posisi tooltip — cegah keluar viewport
    const cw  = canvas.clientWidth;
    let tx = mx + 12;
    let ty = my - 20;
    if (tx + 230 > cw) tx = mx - 240;
    if (ty < 0) ty = 4;

    tooltip.style.left    = tx + 'px';
    tooltip.style.top     = ty + 'px';
    tooltip.style.display = 'block';
  });

  canvas.addEventListener('mouseleave', () => {
    tooltip.style.display = 'none';
  });

  // Klik sel → buka modal detail pair (via HTMX / fetch)
  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;

    const PAD_LEFT = HM.labelW + 8;
    const PAD_TOP  = HM.labelW + 12;
    const cs = HM.cellSize;

    const col = Math.floor((mx - PAD_LEFT) / cs);
    const row = Math.floor((my - PAD_TOP)  / cs);
    const n   = HM.files.length;

    if (col < 0 || row < 0 || col >= n || row >= n) return;
    if (HM.files[row] === HM.files[col]) return;

    const fileA = HM.files[row];
    const fileB = HM.files[col];

    // Cari pair di PAIRS_DATA berdasarkan nama file
    const pair = PAIRS_DATA.find(p =>
      (p.file_a === fileA && p.file_b === fileB) ||
      (p.file_a === fileB && p.file_b === fileA)
    );

    if (pair) {
      // Trigger HTMX fetch untuk modal detail
      const url = `/results/pairs/${pair.id}`;
      fetch(url, { headers: { 'HX-Request': 'true' } })
        .then(r => r.text())
        .then(html => {
          // Hapus modal lama jika ada
          document.getElementById('pair-modal')?.remove();
          document.body.insertAdjacentHTML('beforeend', html);
        });
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   7. SUMMARY STRIP
═══════════════════════════════════════════════════════════════ */
function renderSummary() {
  const el = document.getElementById('hm-summary');
  if (!el) return;

  const all   = PAIRS_DATA;
  const high  = all.filter(p => p.sim >= 70).length;
  const med   = all.filter(p => p.sim >= 40 && p.sim < 70).length;
  const low   = all.filter(p => p.sim < 40).length;
  const maxSim = Math.max(...all.map(p => p.sim), 0);
  const avgSim = all.length
    ? Math.round(all.reduce((s, p) => s + p.sim, 0) / all.length)
    : 0;

  el.innerHTML = `
    <div class="hm-stat">
      <span class="hm-stat-label">Total Pasangan</span>
      <span class="hm-stat-value">${all.length}</span>
    </div>
    <div class="hm-stat">
      <span class="hm-stat-label">Sangat Tinggi (≥70%)</span>
      <span class="hm-stat-value red">${high}</span>
    </div>
    <div class="hm-stat">
      <span class="hm-stat-label">Perlu Dicek (40–69%)</span>
      <span class="hm-stat-value amber">${med}</span>
    </div>
    <div class="hm-stat">
      <span class="hm-stat-label">Aman (&lt;40%)</span>
      <span class="hm-stat-value green">${low}</span>
    </div>
    <div class="hm-stat">
      <span class="hm-stat-label">Kemiripan Maks.</span>
      <span class="hm-stat-value red">${maxSim}%</span>
    </div>
    <div class="hm-stat">
      <span class="hm-stat-label">Rata-rata</span>
      <span class="hm-stat-value">${avgSim}%</span>
    </div>
  `;
}

/* ═══════════════════════════════════════════════════════════════
   8. LEGEND BAR
═══════════════════════════════════════════════════════════════ */
function renderLegend() {
  const bar = document.getElementById('hm-legend-bar');
  if (!bar) return;
  bar.style.background = PALETTES[HM.palette].gradient;
}

/* ═══════════════════════════════════════════════════════════════
   9. PUBLIC API
═══════════════════════════════════════════════════════════════ */

/** Inisialisasi & render pertama kali (dipanggil saat tab heatmap dibuka). */
function hmInit() {
  if (!window.PAIRS_DATA || !window.FILES_DATA) {
    console.warn('heatmap.js: PAIRS_DATA atau FILES_DATA tidak ditemukan.');
    return;
  }

  HM.matrix = buildMatrix();
  HM.files  = sortFiles(FILES_DATA, HM.matrix, HM.sortMode);

  renderLegend();
  renderCanvas();
  renderSummary();

  if (!HM.initialized) {
    attachTooltip();
    // Re-render saat window resize
    window.addEventListener('resize', _debounce(() => renderCanvas(), 200));
    HM.initialized = true;
  }
}

/** Ubah ambang batas sorot. */
function hmSetThreshold(val) {
  HM.threshold = parseInt(val);
  document.getElementById('hm-threshold-val').textContent = val + '%';
  renderCanvas();
}

/** Ubah urutan file. */
function hmSort(mode) {
  HM.sortMode = mode;
  HM.files    = sortFiles(FILES_DATA, HM.matrix, mode);
  renderCanvas();
}

/** Ganti skema warna. */
function hmPalette(name) {
  if (!PALETTES[name]) return;
  HM.palette = name;
  renderLegend();
  renderCanvas();
}

/** Unduh canvas sebagai PNG. */
function hmDownload() {
  const canvas = document.getElementById('hm-canvas');
  if (!canvas) return;
  const link    = document.createElement('a');
  link.download = 'plagcheck_heatmap.png';
  link.href     = canvas.toDataURL('image/png');
  link.click();
}

/* ═══════════════════════════════════════════════════════════════
   10. UTILITY
═══════════════════════════════════════════════════════════════ */
function _debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
