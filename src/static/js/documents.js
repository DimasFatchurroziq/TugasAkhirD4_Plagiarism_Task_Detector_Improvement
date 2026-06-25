let selectedDocumentId = null;

function openDeleteModal(documentId) {
  selectedDocumentId = documentId;
  document.getElementById("deleteModal").classList.add("open");
}

function closeDeleteModal() {
  selectedDocumentId = null;
  document.getElementById("deleteModal").classList.remove("open");
}


(function () {

  function init() {
    bindDeleteButton();
  }

  function bindDeleteButton() {
    const btn = document.getElementById("confirmDeleteBtn");
    if (!btn) return;

    btn.addEventListener("click", handleDelete);
  }

  async function handleDelete() {
    if (!selectedDocumentId) return;

    try {
      const row = document.getElementById(`doc-${selectedDocumentId}`);

      const res = await fetch(`/documents/${selectedDocumentId}`, {
        method: "DELETE"
      });

      if (!res.ok) {
        throw new Error("Gagal menghapus data");
      }

      closeDeleteModal();

      if (row) {
        row.remove();
        showToast("Berhasil menghapus data", "ti-check");
      } else {
        console.log(row)
        showToast("Data sudah tidak ada di tampilan", "ti-info-circle");
      }

      setTimeout(() => {
        location.reload();
      }, 3000);

    } catch (err) {
      showToast(err.message, "ti-alert-circle", true);
    }
  }

  document.addEventListener("DOMContentLoaded", init);

})();