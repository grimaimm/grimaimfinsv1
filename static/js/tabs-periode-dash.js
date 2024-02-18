{/* <div class="tabs-container">
  <select class="tabs-select" id="tabsSelect">
    <option value="tab1">Tab 1</option>
    <option value="tab2">Tab 2</option>
    <option value="tab3">Tab 3</option>
  </select>

  <div class="tabs-content" id="tab1">Content for Tab 1</div>
  <div class="tabs-content" id="tab2">Content for Tab 2</div>
  <div class="tabs-content" id="tab3">Content for Tab 3</div>
</div> */}
// Tambahkan event listener untuk mengganti konten saat tab dipilih
// var tabsSelect = document.getElementById('tabsSelect');
// var tabsContents = document.querySelectorAll('.tabs-content');

// tabsSelect.addEventListener('change', function() {
//   var selectedTab = tabsSelect.value;

//   // Sembunyikan semua konten dan tampilkan yang sesuai dengan tab yang dipilih
//   tabsContents.forEach(function(content) {
//     content.classList.remove('active');
//   });

//   document.getElementById(selectedTab).classList.add('active');
// });

// // Secara otomatis atur tab 1 sebagai tab aktif saat halaman dimuat
// document.getElementById('tab1').classList.add('active');

{/* <div id="tab1" class="tab-content active">
Content for Tab 1
</div>

<div id="tab2" class="tab-content">
Content for Tab 2
</div>

<div id="tab3" class="tab-content">
Content for Tab 3
</div> */}

function showTab(tabId) {
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(function(tabContent) {
    tabContent.classList.remove('active');
  });

  // Deactivate all tabs
  document.querySelectorAll('.tab').forEach(function(tab) {
    tab.classList.remove('active');
  });

  // Show the selected tab and activate it
  document.getElementById(tabId).classList.add('active');
  event.currentTarget.classList.add('active');
}

function showTabAccount(tab) {
    $('.tab').removeClass('active');
    $('.tab-content').removeClass('active');
    $(`#${tab}`).addClass('active');
}