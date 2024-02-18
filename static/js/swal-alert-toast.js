$(function() {
  function showToast(icon, title) {
    var Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000
    });

    Toast.fire({
      icon: icon,
      title: title
    });
  }

  $('.swalDefaultSuccess').click(function() {
    showToast('success', 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.');
  });

  $('.swalDefaultInfo').click(function() {
    showToast('info', 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.');
  });

  $('.swalDefaultError').click(function() {
    showToast('error', 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.');
  });

  $('.swalDefaultWarning').click(function() {
    showToast('warning', 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.');
  });

  $('.swalDefaultQuestion').click(function() {
    showToast('question', 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.');
  });
});