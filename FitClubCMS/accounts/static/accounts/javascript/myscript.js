
// $(document).ready(function() {
//   // Event listener for sidebar link clicks
//   $('.sub-menu a').on('click', function(event) {
//     console.log('Link clicked');
//      event.preventDefault(); // Prevent the default link behavior


//      var target = $(this).data('target'); // Get the target HTML file from the data-target attribute

//      // Load the content using AJAX
//      $.ajax({
//         url: target,
//         dataType: 'html',
//         success: function(data) {
//            $('#content-container').html(data); // Insert the loaded content into the container
//         },
//         error: function() {
//            // Handle any error that occurs during the AJAX request
//            console.log('Error loading content');
//         }
//      });
//   });
// });


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






