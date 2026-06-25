// taruh job
function openNewJobModal() {
  const modal = document.getElementById('new-job-modal');
  if (modal) {
    modal.classList.add('open');
    setTimeout(() => {
      const input = document.getElementById('new-job-name');
      if (input) input.focus();
      // Panggil fungsi inisialisasi slider di sini
      // initSliderBobot();
    }, 100);
  }
}

//taruh job
function closeNewJobModal() {
  const modal = document.getElementById('new-job-modal');
  if (modal) {
    modal.classList.remove('open');
    const form = document.getElementById('new-job-form');
    if (form) form.reset();
  }
}

// taruh job
(function() {
  // Semua helper, modal, toast, dan event listener
  function initJobFormListeners() {
    document.body.addEventListener('htmx:afterOnLoad', function(evt) {
      if (evt.detail.elt.id === 'new-job-form') {
        closeNewJobModal();
        showToast('Job berhasil dibuat', 'ti-check');
        setTimeout(() => {
          location.reload();
        }, 3000);
        ['recent-job-list', 'full-job-list'].forEach(id => {
          const list = document.getElementById(id);
        });
        
      }
    });

    document.body.addEventListener('htmx:responseError', function(evt) {
      if (evt.detail.elt.id === 'new-job-form') {
        showToast('Gagal membuat job', 'ti-alert-circle', true);
      }
    });
  }

  // Jalankan saat DOM siap
  document.addEventListener('DOMContentLoaded', initJobFormListeners);
})();


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Open modal smooth (setelah HTMX load)
document.body.addEventListener('htmx:afterSwap', (evt) => {
  const modal = evt.target.querySelector('.detail-job-modal-overlay');
  if (modal) {
    // Force browser reflow sebelum menambahkan kelas .open
    requestAnimationFrame(() => modal.classList.add('open'));
  }
});

document.body.addEventListener('htmx:beforeRequest', () => {
  document.querySelectorAll('.detail-job-modal-overlay').forEach(m => m.remove());
});

function closeJobDetailModal(button) {
  const overlay = button.closest('.modal-overlay');
  if (!overlay) return;
  overlay.classList.remove('open'); // mulai fade out

  // Hapus elemen setelah animasi selesai (0.2s sesuai CSS)
  setTimeout(() => overlay.remove(), 200);
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Open modal smooth (setelah HTMX load)
document.body.addEventListener('htmx:afterSwap', (evt) => {
  const modal = evt.target.querySelector('.edit-job-modal-overlay');
  if (modal) {
    // Force browser reflow sebelum menambahkan kelas .open
    requestAnimationFrame(() => modal.classList.add('open'));
  }
});

document.body.addEventListener('htmx:beforeRequest', () => {
  document.querySelectorAll('.edit-job-modal-overlay').forEach(m => m.remove());
});

function closeEditJobModal(button) {
  const overlay = button.closest('.modal-overlay');
  if (!overlay) return;
  overlay.classList.remove('open'); // mulai fade out

  // Hapus elemen setelah animasi selesai (0.2s sesuai CSS)
  setTimeout(() => overlay.remove(), 200);
}


let selectedJobId = null;

function openDeleteJobModal(JobId) {
  selectedJobId = JobId;
  document.getElementById("deleteJobModal").classList.add("open");
}

function closeDeleteJobModal() {
  selectedJobId = null;
  document.getElementById("deleteJobModal").classList.remove("open");
}


(function () {

  function init() {
    bindJobDeleteButton();
  }

  function bindJobDeleteButton() {
    const btn = document.getElementById("confirmDeleteJobBtn");
    if (!btn) return;

    btn.addEventListener("click", handleJobDelete);
  }

  async function handleJobDelete() {
    if (!selectedJobId) return;

    try {
      const row = document.getElementById(`job-card-${selectedJobId}`);
      const detailModal = document.getElementById("job-modal"); // Tambahan untuk menutup detail modal

      const res = await fetch(`/jobs/${selectedJobId}`, {
        method: "DELETE"
      });

      if (!res.ok) {
        throw new Error("Gagal menghapus data");
      }

      // 1. Tutup modal konfirmasi hapus
      closeDeleteJobModal();

      // 2. Tutup modal detail job jika sedang terbuka
      if (detailModal) {
        detailModal.remove(); // atau ganti dengan fungsi closeJobDetailModal(detailModal) milikmu
      }

      // 3. Hapus baris tabel/card list jika ada
      if (row) {
        row.remove();
        showToast("Berhasil menghapus job", "ti-check");
      } else {
        showToast("Job berhasil dihapus", "ti-check");
      }

      // 4. Reload halaman setelah 3 detik
      setTimeout(() => {
        location.reload();
      }, 3000);

    } catch (err) {
      showToast(err.message, "ti-alert-circle", true);
    }
  }

  document.addEventListener("DOMContentLoaded", init);

})();
