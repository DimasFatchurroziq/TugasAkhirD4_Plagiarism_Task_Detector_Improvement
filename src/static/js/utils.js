/* static/js/utils.js — Toast, Modal, dan helper global */

/* ── Toast ─────────────────────────────────────────────────────── */
function showToast(msg, icon = 'ti-info-circle', isError = false) {
  const wrap  = document.getElementById('toast-wrap');
  const toast = document.createElement('div');
  toast.className = `toast${isError ? ' error' : ''}`;
  toast.innerHTML = `<i class="ti ${icon}"></i>${msg}`;
  wrap.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity .3s, transform .3s';
    toast.style.opacity    = '0';
    toast.style.transform  = 'translateY(8px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}


// taruh util (VERSI PERBAIKAN)
function closeModalOnBackdrop(e) { 
  if (e.target === e.currentTarget) {
    const overlay = e.currentTarget;
    
    // 1. Hapus class open untuk memicu animasi closing CSS
    overlay.classList.remove('open');
    
    // 2. Jika ini adalah modal dinamis dari HTMX (detail/edit), hapus total dari DOM setelah animasi selesai
    // Cek apakah modal ini BUKAN modal new-job bawaan page
    if (overlay.id !== 'new-job-modal') {
      setTimeout(() => {
        overlay.remove();
      }, 200); // Sesuaikan 200ms dengan durasi transisi CSS kamu
    }
  }
}


function togglePlagiatManual(button, pairId) {
  // Ambil status saat ini dari atribut data
  const currentStatus = button.getAttribute('data-status');
  const statusContainer = document.getElementById('status-badge-container');
  let is_plagiat = '';

  const plagiatBadgeHTML = `
    <span style="color:var(--red-fg); background: repeating-linear-gradient(45deg, var(--red-bg), var(--red-bg) 5px, transparent 5px, transparent 10px); border: 3px solid var(--red-bg); padding: 4px 8px; border-radius: 10px;">
      ⚠ PLAGIAT
    </span>`;
    
  const orisinilBadgeHTML = `
    <span style="color:var(--green-dark); background: repeating-linear-gradient(45deg, var(--green-light), var(--green-light) 5px, transparent 5px, transparent 10px); border: 3px solid var(--green-light); padding: 4px 8px; border-radius: 10px;">
      ✓ ORISINIL
    </span>`;
  
  if (currentStatus === 'orisinil') {
    // Aksi: Mengubah dari Aman -> Plagiat
    is_plagiat = true;
    button.setAttribute('data-status', 'plagiat');
    
    // Ubah Tampilan menjadi tombol bahaya (Merah) dengan teks "Plagiat"
    button.className = "btn btn-danger btn-sm";
    button.innerHTML = '<i class="ti ti-alert-triangle"></i> Lepas Plagiat';

    statusContainer.innerHTML = plagiatBadgeHTML;
    
    showToast('Dilaporkan sebagai plagiat', 'ti-flag');
  } else {
    // Aksi: Membatalkan status plagiat (Plagiat -> Aman)
    is_plagiat = false;
    button.setAttribute('data-status', 'orisinil');
    
    // Ubah Tampilan kembali menjadi tombol sekunder (Abu-abu) dengan teks "Tandai Plagiat"
    button.className = "btn self-btn-green btn-sm";
    button.innerHTML = '<i class="ti ti-flag"></i> Tandai Plagiat';

    statusContainer.innerHTML = orisinilBadgeHTML;
    
    showToast('Tanda plagiat dibatalkan', 'ti-check');
  }

  // Kirim data perubahan status ini ke Backend via Fetch API
  fetch(`/comparisons/${pairId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ is_plagiat: is_plagiat })
  })
  .then(response => {
    if (!response.ok) {
      showToast('Gagal memperbarui status di server', 'ti-alert-circle');
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}


document.addEventListener('jobCreatedDelayed', function(event) {
  // Ambil URL target yang dinamis dari backend
  const destinationUrl = event.detail.value; 

  // Berikan jeda 1000ms (1 detik) sebelum pindah halaman
  setTimeout(function() {
    window.location.href = destinationUrl;
  }, 1000);
});

document.body.addEventListener('jobDeleted', function() {
    showToast('Job berhasil dihapus!', 'ti-trash');
});











