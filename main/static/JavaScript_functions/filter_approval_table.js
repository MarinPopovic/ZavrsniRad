function filterBookTable() {
    // Get user input
    var input = document.getElementById("EmailInput2");
    var filter = input.value.toLowerCase();
  
    // Get table rows
    var table = document.getElementById("ApproveReturnTable");
    var rows = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those that do not match the filter
    for (var i = 1; i < rows.length; i++) { // start at 1 to skip header row
      var email = rows[i].getElementsByTagName("td")[2]; // email column is third -> [2]
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
  