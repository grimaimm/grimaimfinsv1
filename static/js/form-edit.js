function toggleButtons() {
  var cancelButton = document.querySelector('.btn-cancel-update');
  var submitButton = document.querySelector('.btn-save-update');
  var editButton = document.querySelector('.btn-update-account');
  var inputFields = document.querySelectorAll('.enable-on-edit');

  // Toggle visibility of buttons
  cancelButton.classList.toggle('d-none');
  submitButton.classList.toggle('d-none');
  editButton.classList.toggle('d-none');

  // Toggle disabled attribute of input fields
  inputFields.forEach(function (input) {
    input.disabled = !input.disabled;
  });
}