document.addEventListener("DOMContentLoaded", function() {
  flatpickr("#datetimepicker-dashboard", {
    inline: true,
    prevArrow: '<span class="btn-kalender" title="Previous month"><i class="fa-duotone fa-chevrons-left"></i></span>',
    nextArrow: '<span class="btn-kalender" title="Next month"><i class="fa-duotone fa-chevrons-right"></i></span>',
    defaultDate: "today", // Set default date to today
  });
});
