/* static/js/upload.js — Drag & Drop, File Preview, Upload ke API */

// Menampung file secara dinamis, contoh strukturnya nanti:
// { dokumen_utama: [file1, file2], dokumen_pendukung: [fileA] }
let _uploadInstances = {}; 

/* ── Drag & Drop ────────────────────────────────────────────────── */
function handleDragOverSingle(e) {
  e.preventDefault();
  e.currentTarget.classList.add('dragover');
}

function handleDragLeaveSingle(e) {
  e.currentTarget.classList.remove('dragover');
}

function handleDropSingle(e, suffix) {
  e.preventDefault();
  e.currentTarget.classList.remove('dragover');
  handleFileInputSingle(e.dataTransfer.files, suffix);
}

/* ── File validation & preview ──────────────────────────────────── */
const ALLOWED_EXTS  = ['pdf', 'docx', 'txt'];
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

function handleFileInputSingle(files, suffix) {
  // Inisialisasi array jika suffix ini belum pernah dipakai
  if (!_uploadInstances[suffix]) {
    _uploadInstances[suffix] = [];
  }

  let added = 0;
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase();

    if (!ALLOWED_EXTS.includes(ext)) {
      showToast(`Format .${ext} tidak didukung`, 'ti-alert-circle', true);
      continue;
    }
    if (f.size > MAX_SIZE_BYTES) {
      showToast(`${f.name} melebihi 10 MB`, 'ti-alert-circle', true);
      continue;
    }
    // Cek duplikasi khusus di dalam kelompok suffix ini saja
    if (!_uploadInstances[suffix].find(u => u.name === f.name)) {
      _uploadInstances[suffix].push(f);
      added++;
    }
  }

  if (added) showToast(`${added} file ditambahkan`, 'ti-check');
  renderFileGridSingle(suffix);
}

/* ── Render preview grid ─────────────────────────────────────────── */
const EXT_ICONS = {
  pdf:  { cls: 'pdf',  icon: 'ti-file-type-pdf' },
  docx: { cls: 'docx', icon: 'ti-file-type-doc' },
  txt:  { cls: 'txt',  icon: 'ti-file-text' },
};

function renderFileGridSingle(suffix) {
  const grid    = document.getElementById(`file-grid-${suffix}`);
  const section = document.getElementById(`uploaded-section-${suffix}`);
  const count   = document.getElementById(`upload-count-${suffix}`);
  
  const files   = _uploadInstances[suffix] || [];

  if (!grid || !section) return;

  if (!files.length) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'block';
  if (count) count.textContent = files.length;

  grid.innerHTML = files.map((f, i) => {
    const ext    = f.name.split('.').pop().toLowerCase();
    const meta   = EXT_ICONS[ext] || { cls: '', icon: 'ti-file' };
    const sizeKb = (f.size / 1024).toFixed(1);
    return `
    <div class="file-card" id="fc-${suffix}-${i}">
      <div class="file-icon ${meta.cls}"><i class="ti ${meta.icon}"></i></div>
      <div class="file-info">
        <div class="file-name" title="${f.name}">${f.name}</div>
        <div class="file-size">${ext.toUpperCase()} · ${sizeKb} KB</div>
      </div>
      <button class="file-remove" onclick="removeFileSingle('${suffix}', ${i})" title="Hapus">
        <i class="ti ti-x"></i>
      </button>
    </div>`;
  }).join('');
}

/* ── Aksi Hapus & Reset ────────────────────────────────────────── */
function removeFileSingle(suffix, i) {
  if (_uploadInstances[suffix]) {
    _uploadInstances[suffix].splice(i, 1);
  }
  
  // KOREKSI DI SINI: Gunakan ID langsung untuk mereset input file asli
  const input = document.getElementById(`file-input-${suffix}`);
  if (input) input.value = '';

  renderFileGridSingle(suffix);
}

function clearAllFilesSingle(suffix) {
  _uploadInstances[suffix] = [];
  
  // KOREKSI DI SINI: Gunakan ID langsung untuk mereset input file asli
  const input = document.getElementById(`file-input-${suffix}`);
  if (input) input.value = '';
  
  renderFileGridSingle(suffix);
  showToast('Semua file dihapus', 'ti-trash');
}

/* ── Proses Upload Spesifik Tujuan ────────────────────────────────── */
// 1. Fungsi startUploads sekarang mengembalikan (return) Promise Fetch
async function startUploadsSingle(suffix) {
  const files = _uploadInstances[suffix] || [];
  
  // PERBAIKAN: Jika form kosong, langsung kembalikan status SUKSES 
  // tanpa memicu fetch() ke server yang bisa bikin error 404/gagal.
  if (files.length === 0) {
    return Promise.resolve({ success: true, message: `Tidak ada file untuk ${suffix}` });
  }

  const jobId = document.getElementById('active-job-select')?.value;
  if (!jobId) {
    showToast('Pilih job terlebih dahulu', 'ti-alert-circle', true);
    return;
  }

  const formData = new FormData();
  formData.append('job_id', jobId); 

  // Perbaikan sintaks menggunakan if/else if versi JavaScript
  if (suffix === "utama") {
    formData.append('category', "ONE");
  } else if (suffix === "pendukung") {
    formData.append('category', "MANY");
  }

  files.forEach((file) => { 
    formData.append('files', file); // Sudah benar tanpa [] untuk FastAPI
  });
  
  // PENTING: Pastikan '/upload-endpoint' ini diganti dengan URL backend kamu yang benar!
  return fetch('/upload/files', { 
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) throw new Error(`Gagal mengupload dokumen ${suffix}`);
    return response.json();
  })
  .then(data => {
    clearAllFilesSingle(suffix); 
    return data;
  })
  .catch(error => {
    showToast(error.message || 'Upload gagal', 'ti-alert-circle', true);
    throw error;
  });
}

// 2. FUNGSI UTAMA: Memicu semua upload sekaligus baru pindah halaman
function submitSemuaDokumenSingle() {
  const fileUtama = _uploadInstances['utama'] || [];
  const filePendukung = _uploadInstances['pendukung'] || [];

  // Validasi: Misal Dokumen Utama wajib diisi, Dokumen Pendukung opsional
  // if (fileUtama.length === 0) {
  //   showToast('Dokumen Utama wajib diisi!', 'ti-alert-circle', true);
  //   return;
  // }

  // Target tombol submit global untuk efek loading
  const btnSubmit = document.getElementById('btn-submit-all');
  const originalHtml = btnSubmit.innerHTML;
  btnSubmit.disabled = true;
  btnSubmit.innerHTML = `<i class="ti ti-spinner rotate"></i> Memproses Dokumen...`;

  // Jalankan upload UTAMA dan PENDUKUNG secara bersamaan (Paralel)
  Promise.all([
    startUploadsSingle('utama'),
    startUploadsSingle('pendukung')
  ])
  .then((results) => {
    showToast('Semua dokumen berhasil disimpan!', 'ti-check');
    
    // Pindah halaman setelah ALL sukses
    const jobId = document.getElementById('active-job-select')?.value;
      if (!jobId) {
        showToast('Pilih job terlebih dahulu', 'ti-alert-circle', true);
        return;
      }
    setTimeout(() => {
      window.location.href = `/documents/?job_id=${jobId}`; // Ganti dengan URL tujuanmu
    }, 1000);
  })
  .catch(error => {
    console.error('Error saat submit:', error);
    showToast('Terjadi kesalahan saat mengupload salah satu dokumen.', 'ti-alert-circle', true);
  })
  .finally(() => {
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = originalHtml;
  });
}

// function showToast(message, iconClass, isError = false) {
//   console.log(`[Toast] ${message}`);
// }
// function showToast(message, iconClass, isError = false) {
//   console.log(`[Toast] ${message}`);
// }
// function showToast(message, iconClass, isError = false) {
//   console.log(`[Toast] ${message}`);
// }


let _uploadedFiles = [];

/* ── Drag & Drop ────────────────────────────────────────────────── */
function handleDragOverMultiple(e) {
  e.preventDefault();
  document.getElementById('drop-zone')?.classList.add('dragover');
}

function handleDragLeaveMultiple(e) {
  document.getElementById('drop-zone')?.classList.remove('dragover');
}

function handleDropMultiple(e) {
  e.preventDefault();
  document.getElementById('drop-zone')?.classList.remove('dragover');
  handleFileInputMultiple(e.dataTransfer.files);
}

function handleFileInputMultiple(files) {
  let added = 0;
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase();

    if (!ALLOWED_EXTS.includes(ext)) {
      showToast(`Format .${ext} tidak didukung`, 'ti-alert-circle', true);
      continue;
    }
    if (f.size > MAX_SIZE_BYTES) {
      showToast(`${f.name} melebihi 10 MB`, 'ti-alert-circle', true);
      continue;
    }
    if (!_uploadedFiles.find(u => u.name === f.name)) {
      _uploadedFiles.push(f);
      added++;
    }
  }

  if (added) showToast(`${added} file ditambahkan`, 'ti-check');
  renderFileGridMultiple();
}

function renderFileGridMultiple() {
  const grid    = document.getElementById('file-grid');
  const section = document.getElementById('uploaded-section');
  const count   = document.getElementById('upload-count');
  if (!grid || !section) return;

  if (!_uploadedFiles.length) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'block';
  if (count) count.textContent = _uploadedFiles.length;

  grid.innerHTML = _uploadedFiles.map((f, i) => {
    const ext    = f.name.split('.').pop().toLowerCase();
    const meta   = EXT_ICONS[ext] || { cls: '', icon: 'ti-file' };
    const sizeKb = (f.size / 1024).toFixed(1);
    return `
    <div class="file-card" id="fc-${i}">
      <div class="file-icon ${meta.cls}"><i class="ti ${meta.icon}"></i></div>
      <div class="file-info">
        <div class="file-name" title="${f.name}">${f.name}</div>
        <div class="file-size">${ext.toUpperCase()} · ${sizeKb} KB</div>
      </div>
      <button class="file-remove" onclick="removeFileMultiple(${i})" title="Hapus">
        <i class="ti ti-x"></i>
      </button>
    </div>`;
  }).join('');
}

function removeFileMultiple(i) {
  _uploadedFiles.splice(i, 1);
  renderFileGridMultiple();
}

function clearAllFilesMultiple() {
  _uploadedFiles = [];
  const input = document.getElementById('file-input');
  if (input) input.value = '';
  renderFileGridMultiple();
  showToast('Semua file dihapus', 'ti-trash');
}

/* ── Upload & mulai perbandingan ────────────────────────────────── */
async function startUploadsMultiple() {
  if (!_uploadedFiles.length) {
    showToast('Upload file terlebih dahulu', 'ti-alert-circle', true);
    return;
  }

  const jobId = document.getElementById('active-job-select')?.value;
  if (!jobId) {
    showToast('Pilih job terlebih dahulu', 'ti-alert-circle', true);
    return;
  }

  // Tampilkan progress bar
  const progressSection = document.getElementById('upload-progress-section');
  const bar             = document.getElementById('upload-bar');
  const pct             = document.getElementById('upload-pct');
  if (progressSection) progressSection.style.display = 'block';

  const fd = new FormData();
  fd.append('job_id', jobId);
  fd.append('category', 'MANY');
  _uploadedFiles.forEach(f => fd.append('files', f));

  // Simulasi progress (XHR untuk progress asli)
  const xhr = new XMLHttpRequest();
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const p = Math.round((e.loaded / e.total) * 100);
      if (bar) bar.style.width = p + '%';
      if (pct) pct.textContent = p + '%';
    }
  });

  xhr.addEventListener('load', () => {
    if (xhr.status === 200) {
      const data = JSON.parse(xhr.responseText);
      showToast(
        `${data.uploaded.length} file berhasil diupload${data.errors.length ? `, ${data.errors.length} gagal` : ''}`,
        'ti-check'
      );
      // Submit form start comparison
      const startJobId = document.getElementById('start-job-id');
      if (startJobId) startJobId.value = jobId;
      setTimeout(() => {
        window.location.href = `/documents/?job_id=${jobId}`;
      }, 1000);
    } else {
      showToast('Upload gagal', 'ti-alert-circle', true);
      if (progressSection) progressSection.style.display = 'none';
    }
  });

  xhr.addEventListener('error', () => {
    showToast('Koneksi gagal', 'ti-alert-circle', true);
    if (progressSection) progressSection.style.display = 'none';
  });

  xhr.open('POST', '/upload/files');
  xhr.send(fd);
}


// async function unprocessDocuments() {

//   const jobId = document.getElementById('results-job-filter')?.value;

//   if (!jobId) {
//     showToast('Pilih job terlebih dahulu', 'ti-alert-circle', true);
//     return;
//   }

//   try {

//     showToast('Memulai pemrosesan...', 'ti-loader');

//     const response = await fetch(`/processdddd/job/${jobId}`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       }
//     });

//     const data = await response.json();

//     if (!response.ok) {
//       throw new Error(data.message || 'Process gagal');
//     }

//     showToast('Dokumen berhasil diproses', 'ti-check');

//     // optional redirect
//     setTimeout(() => {
//       window.location.href = `/results/?job_id=${jobId}`;
//     }, 1000);

//   } catch (err) {

//     showToast(err.message || 'Terjadi kesalahan', 'ti-alert-circle', true);

//   }
// }


async function deleteDocument(documentId) {
  if (!confirm("Yakin ingin menghapus dokumen ini?")) return;

  const res = await fetch(`/documents/${documentId}`, {
    method: "DELETE"
  });

  if (res.ok) {
    // reload halaman setelah sukses
    location.reload();
  } else {
    const msg = await res.text();
    alert("Gagal menghapus: " + msg);
  }
}



let isProcessing = false;
let currentAbortController = null;

async function processDocuments() {

  window.onbeforeunload = function() {
        return "Sedang menyimpan...";
    };

  const jobSelect = document.getElementById('results-job-filter');
  const jobId = jobSelect?.value;

  const overlay = document.getElementById('loading-overlay');

  if (!jobId) {
    showToast('Pilih job terlebih dahulu', 'ti-alert-circle', true);
    return;
  }

  // cegah double click
  if (isProcessing) return;

  isProcessing = true;

  // cancel request sebelumnya jika ada
  if (currentAbortController) {
    currentAbortController.abort();
  }

  currentAbortController = new AbortController();

  const btn = document.querySelector('[onclick="processDocuments()"]');
  if (btn) btn.disabled = true;

  try {
    if (overlay) overlay.classList.add('open');

    showToast('Memulai pemrosesan...', 'ti-loader');

    const response_sce = await fetch(`/jobss/${jobId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
    });

    if (!response_sce.ok) {
      throw new Error('Gagal mengambil data job');
    }

    // Konversi response_sce stream menjadi objek JSON
    const jobData = await response_sce.json();
    
    // Ambil properti scenario dari data job (sesuaikan dengan field di model/schema Job Anda)
    const scenario = jobData.scenario; 
    
    console.log("Skenario job ini:", scenario);

    let endpoint = '';
    if (scenario === "MULTIPLE") {
      endpoint = `/processmultiple/job/${jobId}`;
    } else if (scenario === "SINGLE") {
      endpoint = `/processsingle/job/${jobId}`;
    } else {
      throw new Error('Skenario analisis tidak dikenal');
    }

    // 2. BARU EKSEKUSI FETCH DI SINI (Gunakan const res)
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: currentAbortController.signal,
    });

    // 3. Sekarang 'res' pasti aman diakses di sini
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || 'Process gagal');
    }

    const data = await res.json().catch(() => ({})); // Amankan jika return kosongan

    showToast(`Dokumen berhasil diproses`, 'ti-check');

    setTimeout(() => {
      window.location.href = `/results/?job_id=${jobId}`;
    }, 1000);

  } catch (err) {

    if (err.name !== 'AbortError') {
      showToast(err.message || 'Error terjadi', 'ti-alert-circle', true);
    }

  } finally {
    if (overlay) overlay.classList.remove('open');

    isProcessing = false;
    if (btn) btn.disabled = false;

    window.onbeforeunload = null;
  }
}

