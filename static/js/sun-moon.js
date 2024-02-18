// {/* <div class="sidebar-mode">
//   <button id="toggleButton"><i class="fa-duotone fa-clouds-sun"></i></button>
// </div> */}

// // Ambil elemen tombol dan ikon
// var button = document.getElementById('toggleButton');
// var icon = button.querySelector('i');

// // Tambahkan event listener untuk mengganti ikon saat tombol diklik
// button.addEventListener('click', function() {
//   // Periksa kelas ikon saat ini dan ganti sesuai dengan kondisi yang diinginkan
//   if (icon.classList.contains('fa-clouds-sun')) {
//     icon.classList.remove('fa-clouds-sun');
//     icon.classList.add('fa-clouds-moon');
//   } else {
//     icon.classList.remove('fa-clouds-moon');
//     icon.classList.add('fa-clouds-sun');
//   }

//   var bodyElement = document.body;
//     // Toggle antara body-light dan body-dark
//     bodyElement.classList.toggle('body-dark');
//     bodyElement.classList.toggle('body-light');
    
// });


// // var bodyElement = document.body;
// // var button = document.getElementById('toggleButton');
// // var icon = button.querySelector('i');

// // // Cek apakah ada nilai mode di localStorage saat halaman dimuat
// // var savedMode = localStorage.getItem('mode');

// // // Jika ada nilai, atur mode sesuai nilai tersebut
// // if (savedMode) {
// //   bodyElement.classList.add(savedMode);
// //   // Jika dark mode, ubah ikon ke moon
// //   if (savedMode === 'body-dark') {
// //     icon.classList.remove('fa-clouds-sun');
// //     icon.classList.add('fa-clouds-moon');
// //   }
// // }

// // button.addEventListener('click', function() {
// //   // Periksa kelas ikon saat ini dan ganti sesuai dengan kondisi yang diinginkan
// //   if (icon.classList.contains('fa-clouds-sun')) {
// //     icon.classList.remove('fa-clouds-sun');
// //     icon.classList.add('fa-clouds-moon');
// //   } else {
// //     icon.classList.remove('fa-clouds-moon');
// //     icon.classList.add('fa-clouds-sun');
// //   }

// //   // Toggle antara body-light dan body-dark
// //   bodyElement.classList.toggle('body-dark');
// //   bodyElement.classList.toggle('body-light');

// //   // Simpan nilai mode saat ini ke localStorage
// //   var currentMode = bodyElement.classList.contains('body-light') ? 'body-light' : 'body-dark';
// //   localStorage.setItem('mode', currentMode);
// // });

/**
 * Utility function to calculate the current theme setting.
 * Look for a local storage value.
 * Fall back to the system setting.
 * Fall back to light mode.
 */
function calculateSettingAsThemeString({ localStorageTheme, systemSettingDark }) {
  if (localStorageTheme !== null) {
    return localStorageTheme;
  }

  if (systemSettingDark.matches) {
    return "dark";
  }

  return "light";
}

/**
 * Utility function to update the button with Font Awesome icon and aria-label.
 */
function updateButton({ buttonEl, isDark }) {
  const iconClass = isDark ? "fa-clouds-moon" : "fa-clouds-sun";
  const newCta = `<i class="fa-duotone ${iconClass}" aria-hidden="true"></i>`;
  // Use an aria-label if you are omitting text on the button
  // and using a sun/moon icon, for example
  buttonEl.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
  buttonEl.innerHTML = newCta;
}

/**
 * Utility function to update the theme setting on the html tag.
 */
function updateThemeOnHtmlEl({ theme }) {
  document.querySelector("html").setAttribute("data-theme", theme);
}

/**
 * On page load:
 */

/**
 * 1. Grab what we need from the DOM and system settings on page load.
 */
const button = document.querySelector("[data-theme-toggle]");
const localStorageTheme = localStorage.getItem("theme");
const systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");

/**
 * 2. Work out the current site settings.
 */
let currentThemeSetting = calculateSettingAsThemeString({ localStorageTheme, systemSettingDark });

/**
 * 3. Update the theme setting and button text according to current settings.
 */
updateButton({ buttonEl: button, isDark: currentThemeSetting === "dark" });
updateThemeOnHtmlEl({ theme: currentThemeSetting });

/**
 * 4. Add an event listener to toggle the theme.
 */
button.addEventListener("click", (event) => {
  const newTheme = currentThemeSetting === "dark" ? "light" : "dark";

  localStorage.setItem("theme", newTheme);
  updateButton({ buttonEl: button, isDark: newTheme === "dark" });
  updateThemeOnHtmlEl({ theme: newTheme });

  currentThemeSetting = newTheme;
});
