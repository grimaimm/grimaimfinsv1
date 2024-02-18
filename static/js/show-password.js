function togglePasswordVisibility() {
  const currentPasswordInput = document.getElementById("currentPassword");
  const newPasswordInput = document.getElementById("newPassword");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  // Toggle tipe input antara "password" dan "text"
  currentPasswordInput.type = currentPasswordInput.type === "password" ? "text" : "password";
  newPasswordInput.type = newPasswordInput.type === "password" ? "text" : "password";
  confirmPasswordInput.type = confirmPasswordInput.type === "password" ? "text" : "password";
}

function toggleShowPassword() {
  const showPasswordInput = document.getElementById("showPassword");
  // Toggle tipe input antara "password" dan "text"
  showPasswordInput.type = showPasswordInput.type === "password" ? "text" : "password";
}