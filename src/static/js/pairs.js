// Open modal smooth (setelah HTMX load)
document.body.addEventListener('htmx:afterSwap', (evt) => {
  const modal = evt.target.querySelector('.pair-modal-overlay');
  if (modal) {
    // Force browser reflow sebelum menambahkan kelas .open
    requestAnimationFrame(() => modal.classList.add('open'));
  }
});

document.body.addEventListener('htmx:beforeRequest', () => {
  document.querySelectorAll('.pair-modal-overlay').forEach(m => m.remove());
});

// function closePairDetailModal(button) {
//   const overlay = button.closest('.modal-overlay');
//   if (!overlay) return;
//   overlay.classList.remove('open'); // mulai fade out

//   // Hapus elemen setelah animasi selesai (0.2s sesuai CSS)
//   setTimeout(() => {
//       overlay.remove();
//       window.location.reload(); // Taruh di sini agar sinkron setelah modal hilang
//     }, 200);
// }
