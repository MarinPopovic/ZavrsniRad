 // Select the search input and search button
 const searchInput = document.getElementById('search-term-input');
 const searchButton = document.getElementById('search-button');

 // Add an input event listener to the search input
 searchInput.addEventListener('input', function() {
   // Enable the search button if the input value is not empty, otherwise disable it
   if (searchInput.value.trim() !== '') {
     searchButton.disabled = false;
   } else {
     searchButton.disabled = true;
   }
 });