// document.addEventListener("DOMContentLoaded", function() {
//   var fullnameElements = document.querySelectorAll('.fullname');
//   var maxCharacters = 15;

//   fullnameElements.forEach(function(element) {
//       var fullName = element.textContent || element.innerText;

//       if (fullName.length > maxCharacters) {
//           element.textContent = fullName.substring(0, maxCharacters);
//       }
//   });
// });

document.addEventListener("DOMContentLoaded", function() {
  var fullnameElements = document.querySelectorAll('.fullname');
  var maxWords = 2;

  fullnameElements.forEach(function(element) {
      var fullName = element.textContent || element.innerText;
      var words = fullName.split(' ');

      if (words.length > maxWords) {
          element.textContent = words.slice(0, maxWords).join(' ');
      }
  });
});