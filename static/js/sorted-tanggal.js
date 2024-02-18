document.addEventListener("DOMContentLoaded", function () {
  var buttonSorted = document.getElementById("buttonSorted");

  // Mendapatkan urutan awal dari URL saat halaman dimuat
  var currentOrder = window.location.href.includes("sort=asc") ? "asc" : "desc";

  // Mendapatkan ikon saat ini
  var icon = buttonSorted.querySelector("i");

  // Menyesuaikan ikon berdasarkan urutan awal
  if (currentOrder === "asc") {
      icon.classList.remove("fa-sort-down");
      icon.classList.add("fa-sort-up");
  } else {
      icon.classList.remove("fa-sort-up");
      icon.classList.add("fa-sort-down");
  }

  buttonSorted.addEventListener("click", function () {
      // Mendapatkan ikon saat ini
      var icon = buttonSorted.querySelector("i");

      // Mengubah ikon dan arahkan ke URL yang sesuai
      if (currentOrder === "asc") {
          // Jika saat ini adalah ascending, ubah menjadi descending
          icon.classList.remove("fa-sort-up");
          icon.classList.add("fa-sort-down");
          window.location.href = "{{ url_for('pengeluaran', sort='desc') }}";
          currentOrder = "desc";
      } else {
          // Jika saat ini adalah descending atau default, ubah menjadi ascending
          icon.classList.remove("fa-sort-down");
          icon.classList.add("fa-sort-up");
          window.location.href = "{{ url_for('pengeluaran', sort='asc') }}";
          currentOrder = "asc";
      }
  });
});