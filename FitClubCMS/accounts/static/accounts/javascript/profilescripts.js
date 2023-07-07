$(document).ready(function() {

  var calendar = $('#calendar').fullCalendar({
      header:{
          left: 'prev, nex, today',
          center: 'title',
          right: 'month, agendaWeek, agendaDay'
      },
      events: '/all_events',
      selectable: true,
      selectHelper: true,
      editable: true,
      eventLimit: true,
      select: function(start, end, allDay){
          var title = prompt("Enter Event Title");
          if(title) {
              var start = $.fullCalendar.formatDate(start, "MMMM D, YYYY, h a");
              var end = $.fullCalendar.formatDate(end, "MMMM D, YYYY, h a");
              
              $.ajax({
                  type: "GET",
                  url: '/add_event',
                  data: {'title': title, 'start': start, 'end': end },
                  dataType: 'json',
                  success: function(data) {
                      calendar.fullCalendar('refetchEvents');
                      alert("Added Successfully");
                  },
                  error: function(data) {
                      alert('Problem occured!!');
                  }
              });
          }
      },

      eventResize: function (event) {
          var start = $.fullCalendar.formatDate(event.start, "Y-MM-DD HH:mm");
          var end = $.fullCalendar.formatDate(event.end, "Y-MM-DD HH:mm");
          var title = event.title;
          var id = event.id;
          $.ajax({
              type: "GET",
              url: '/update_event',
              data: {'title': title, 'start': start, 'end': end, 'id': id},
              dataType: "json",
  
              success: function(data) {
                  calendar.fullCalendar('refetchEvents');
                  alert('Event succesfully updated');
  
              },
              error: function(data) {
                  alert('There was error in updating the event!!');
              
              },
  
          });
      },  


      eventDrop: function(event) {
          var start = $.fullCalendar.formatDate(event.start, "Y-MM-DD HH:mm");
          var end = $.fullCalendar.formatDate(event.end, "Y-MM-DD HH:mm");
          var title = event.title;
          var id = event.id;
          $.ajax({
              type: "GET",
              url: '/update_event',
              data: {'title': title, 'start': start, 'end': end, 'id': id},
              dataType: "json",
  
              success: function(data) {
                  calendar.fullCalendar('refetchEvents');
                  alert('Event succesfully updated');
  
              },
              error: function(data) {
                  alert('There was error in updating the event!!');
          
              },
  
          });          
      },
      eventClick: function (event) {
          if (confirm("Are you sure you want to remove it?")) {
              var id = event.id;
              $.ajax({
                  type: "GET",
                  url: '/remove_event',
                  data: {'id': id},
                  dataType: "json",
  
                  success: function(data) {
                      calendar.fullCalendar('refetchEvents');
                      alert('Event succesfully Removed');
      
                  },
                  error: function(data) {
                      alert('An error occured while removing the event!!');
                  
                  },
              });
          }
  
      }
  });

  // Get the CSRF token from the cookie; needed when submitting the cancel request with the data using Post
  function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) {
          const token = parts.pop().split(';').shift();
          console.log('CSRF Token:', token);
          return token;
      }
      // if (parts.length === 2) return parts.pop().split(';').shift();
  }    



// Fetch bookings data and populate the table
fetch( '/my_bookings')
.then(response => response.json())
.then(data => {
const tableBody = document.querySelector('#bookings-table tbody');
tableBody.innerHTML = '';

data.bookings.forEach(booking => {
    const row = document.createElement('tr');

    const bookingIdCell = document.createElement('td');
    bookingIdCell.textContent = booking.booking_id;
    row.appendChild(bookingIdCell);

    const sessionNameCell = document.createElement('td');
    sessionNameCell.textContent = booking.name;
    row.appendChild(sessionNameCell);

    const countdownCell = document.createElement('td'); // Create the Time Left (Countdown) cell
    row.appendChild(countdownCell); // Append it to the row

    calculateCountdown(booking.start, countdownCell); // Pass the countdownCell to the calculateCountdown function

    const actionCell = document.createElement('td');
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.setAttribute('data-booking-id', booking.booking_id);
    cancelButton.setAttribute('class', 'custom-button');
    actionCell.appendChild(cancelButton);
    row.appendChild(actionCell);

    tableBody.appendChild(row);



    cancelButton.addEventListener('click', function() {
      const bookingId = this.getAttribute('data-booking-id');
      const confirmed = confirm('Are you sure you want to cancel this booking?');
  
      if (confirmed) {
          // Send cancellation request to the server and delete the booking
          fetch(`/cancel_booking/${bookingId}/`, {  // Pass the booking_id in the URL
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken'),
              },
              body: JSON.stringify({ bookingId: bookingId }),
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  // Remove the booking row from the table
                  row.remove();
                  alert('Booking successfully canceled.');
              } else {
                  throw new Error(data.error || 'Failed to cancel the booking. Please try again.');
              }
          })
          .catch(error => {
              console.error('An error occurred while canceling the booking:', error);
              alert('An error occurred while canceling the booking.');
          });
      }
  });

  });
});

});//close of documet.ready function

// Function to calculate the countdown between the start time and the current time
function calculateCountdown(startTime, countdownCell) {
  const startTimestamp = new Date(startTime).getTime();

  // Update countdown every second
  const countdownInterval = setInterval(updateCountdown, 1000);

  function updateCountdown() {
    const currentTimestamp = Date.now();
    const countdown = startTimestamp - currentTimestamp;

    if (countdown > 0) {
      const hours = Math.floor(countdown / (1000 * 60 * 60));
      const minutes = Math.floor((countdown % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((countdown % (1000 * 60)) / 1000);

      countdownCell.textContent = `${hours}h ${minutes}m ${seconds}s`;
    } else {
      countdownCell.textContent = 'Expired';
      clearInterval(countdownInterval); // Stop updating the countdown
    }
  }
}

//Display cureent time on the dashboard 
function updateTime() {
  var currentTimeElement = document.getElementById('current-time');
  var currentTime = new Date().toLocaleTimeString(); // Get the current time
  currentTimeElement.value = currentTime; // Update the input value with the current time
}

// Call updateTime() initially to display the current time
updateTime();

// Call updateTime() every second to keep the time updated
setInterval(updateTime, 1000);




$('.booking-form').submit(function() {
  var submitBtn = $(this).find('input[type=submit]');
  submitBtn.val('Booked');
});


// Get the current date in the payment form date field
var currentDate = new Date();

// Format the date as YYYY-MM-DD
var formattedDate = currentDate.toISOString().split('T')[0];

// Set the value of the input field
document.getElementById('todayField').value = formattedDate;



// countdown to the next class
var countdownElement = document.getElementById('next-class-countdown');
var countdownValue = countdownElement.textContent;

function updateCountdown() {
var countdownParts = countdownValue.split(':');
var hours = parseInt(countdownParts[0]);
var minutes = parseInt(countdownParts[1]);
var seconds = parseInt(countdownParts[2]);

if (seconds > 0) {
  seconds--;
} else {
  if (minutes > 0) {
    minutes--;
    seconds = 59;
  } else {
    if (hours > 0) {
      hours--;
      minutes = 59;
      seconds = 59;
    }
  }
}

countdownValue = hours.toString().padStart(2, '0') + ':' + minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
countdownElement.textContent = countdownValue;

if (countdownValue !== '00:00:00') {
  setTimeout(updateCountdown, 1000);
}
}

if (countdownValue !== 'N/A') {
updateCountdown();
}


