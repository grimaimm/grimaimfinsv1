// function myFunction() {
//   // Declare variables
//   var input, filter, table, tr, td, i, txtValue, noRecordsFound;
//   input = document.getElementById("myInput");
//   filter = input.value.toUpperCase();
//   table = document.getElementById("myTable");
//   tr = table.getElementsByTagName("tr");
//   noRecordsFound = true; // Assume initially that no records are found

//   // Loop through all table rows, and hide those who don't match the search query
//   for (i = 0; i < tr.length; i++) {
//     td = tr[i].getElementsByTagName("td")[1];
//     if (td) {
//       txtValue = td.textContent || td.innerText;
//       if (txtValue.toUpperCase().indexOf(filter) > -1) {
//         tr[i].style.display = "";
//         noRecordsFound = false; // Set to false if at least one record is found
//       } else {
//         tr[i].style.display = "none";
//       }
//     }
//   }

//   // Display "No matching records found" if no records are found
//   if (noRecordsFound) {
//     // Assuming there is an element with the id "noRecordsMessage"
//     document.getElementById("noRecordsMessage").style.display = "block";
//   } else {
//     // Hide the message if there are matching records
//     document.getElementById("noRecordsMessage").style.display = "none";
//   }
// }

function myFunction() {
  var input, filter, table, tr, td, i, j, txtValue;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  // Initialize flag to indicate if any records are found
  var recordsFound = false;

  // Loop through all table rows, excluding the first row (index 0) which is the <thead>
  for (i = 1; i < tr.length; i++) {
      // Initialize flag to indicate if the row should be displayed
      var rowShouldBeDisplayed = false;

      // Loop through all columns for each row
      for (j = 0; j < tr[i].cells.length; j++) {
          td = tr[i].getElementsByTagName("td")[j];
          if (td) {
              txtValue = td.textContent || td.innerText;
              // Check if any column contains the search query
              if (txtValue.toUpperCase().indexOf(filter) > -1) {
                  rowShouldBeDisplayed = true;
                  recordsFound = true;
                  break;  // No need to check other columns for this row
              }
          }
      }

      // Set the display style for the row based on the flag
      tr[i].style.display = rowShouldBeDisplayed ? "" : "none";
  }

  // Show/hide the "No Records Found" message based on the recordsFound flag
  var noRecordsMessage = document.getElementById("noRecordsMessage");
  if (recordsFound) {
      noRecordsMessage.style.display = "none";
  } else {
      noRecordsMessage.style.display = "block";
  }
}


var simulatedResults = [
	"/dashboard - Dashboard",
	"/dashboard/mingguan - Dashboard Mingguan",
	"/dashboard/bulanan - Dashboard Bulanan",
	"/dashboard/tahunan - Dashboard Tahunan",

	"/pengeluaran - Pengeluaran",
	"/pengeluaran/harian - Pengeluaran Harian",
	"/pengeluaran/mingguan - Pengeluaran Mingguan",
	"/pengeluaran/bulanan - Pengeluaran Bulanan",

	"/pemasukan - Pemasukan",
	"/pemasukan/harian - Pemasukan Harian",
	"/pemasukan/mingguan - Pemasukan Mingguan",
	"/pemasukan/bulanan - Pemasukan Bulanan",

	"/keuangan - Keuangan",
	"/keuangan/harian - Keuangan Harian",
	"/keuangan/mingguan - Keuangan Mingguan",
	"/keuangan/bulanan - Keuangan Bulanan",

	"/kategori - Kategori",
	"/kategori/harian - Kategori Harian",
	"/kategori/mingguan - Kategori Mingguan",
	"/kategori/bulanan - Kategori Bulanan",

	"/account/{{ userInfo.username }} - My Account",

	"/logout - Log out"
];

document.addEventListener("DOMContentLoaded", function() {
	var searchInput = document.getElementById('searchInput');
	var searchResults = document.getElementById('searchResults');

	// Tambahkan event listener pada input
	searchInput.addEventListener('input', function() {
		var searchQuery = searchInput.value.toLowerCase();

		// Hapus hasil pencarian sebelumnya
		searchResults.innerHTML = '';

		if (searchQuery.trim() !== '') {
			// Tampilkan hasil pencarian sebagai dropdown
			var foundResults = simulatedResults.filter(function(result) {
				var parts = result.split(' - ');
				var url = parts[0];
				var label = parts[1];

				return url.toLowerCase().includes(searchQuery) || label.toLowerCase().includes(searchQuery);
			});

			if (foundResults.length > 0) {
				foundResults.forEach(function(result) {
					var parts = result.split(' - ');
					var url = parts[0];
					var label = parts[1];

					var resultItem = document.createElement('a');
					resultItem.href = url;
					resultItem.textContent = label;
					searchResults.appendChild(resultItem);
				});
			} else {
				// Tampilkan pesan "Not Found" dengan kelas CSS yang sesuai
				var notFoundItem = document.createElement('div');
				notFoundItem.className = 'not-found';
				notFoundItem.textContent = 'Not Found';
				searchResults.appendChild(notFoundItem);
			}

			// Tampilkan dropdown hasil pencarian
			searchResults.style.display = 'block';
		} else {
			// Sembunyikan dropdown jika input kosong
			searchResults.style.display = 'none';
		}
	});

	// Sembunyikan dropdown jika klik di luar elemen pencarian
	document.addEventListener('click', function(event) {
		if (!event.target.closest('.sidebar-search')) {
			searchResults.style.display = 'none';
		}
	});
});