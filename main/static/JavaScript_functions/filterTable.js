function filterTable() {
  // Get user input
  var input = document.getElementById("myInput");
  var filter = input.value.toLowerCase();

  // Get table rows
  var table = document.getElementsByTagName("table")[0]; 
  var rows = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those that do not match the filter
  for (var i = 1; i < rows.length; i++) { // start at 1 to skip header row
    var email = rows[i].getElementsByTagName("td")[1]; // email column is second -> [1]
    if (email) {
      var emailText = email.textContent || email.innerText;
      if (emailText.toLowerCase().indexOf(filter) > -1) {
        rows[i].style.display = "";
      } else {
        rows[i].style.display = "none";
      }
    }
  }
}