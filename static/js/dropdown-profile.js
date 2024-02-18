function toggleDropdown(element) {
  element.classList.toggle("active");

  // Close the dropdown when clicking outside
  if (!element.classList.contains("active")) {
    document.removeEventListener("click", closeDropdown);
  } else {
    document.addEventListener("click", closeDropdown);
  }
}

function closeDropdown(event) {
  var dropdown = document.querySelector(".dropdown.active");
  if (dropdown && !dropdown.contains(event.target)) {
    dropdown.classList.remove("active");
    document.removeEventListener("click", closeDropdown);
  }
}

