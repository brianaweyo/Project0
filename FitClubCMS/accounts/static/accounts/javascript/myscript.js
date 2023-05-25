let arrow = document.querySelectorAll(" .arrow");
for (var i = 0; i<arrow.length; i++){
     arrow[i].addEventListener("click",(e)=>{    
    let arrowParent = e.target.parentElement.parentElement;
    console.log(arrowParent);
    arrowParent.classList.toggle("showMenu");
    });

}
let sidebar =document.querySelector(".sidebar");
let sidebarBtn =document.querySelector(".bx-menu");
console.log(sidebarBtn);
sidebarBtn.addEventListener("click", ()=>{
  sidebar.classList.toggle("close");
});

$(document).ready(function(){
  var showCards = 3; // Number of cards to show initially
  
  // Function to show/hide cards
  function toggleCards() {
    $('.card-group .card:lt(' + showCards + ')').show();
    $('.card-group .card:gt(' + (showCards - 1) + ')').hide();
  }
  
  toggleCards(); // Initially show the desired number of cards
  
  // Toggle cards on chevron down click
  $('.bx-chevron-down').on('click', function() {
    showCards += 3; // Increase the number of cards to show by 3
    toggleCards(); // Toggle the cards based on the updated value
  });
});




