$(document).ready((fuction) {
    var calendar = $('calendar').fullCalendar({
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
                var start = $.fullCalendar.formatDate(start,"Y-M-DD HH:mm:ss");
                var end = $.fullCalendar.formatDate(end, "Y-MM-DD HH:mm:ss");
                
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
            var start = $.fullCalendar.formatDate(event.start, "Y-MM-DD HH:mm:ss");
            var start = $.fullCalendar.formatDate(event.end, "Y-MM-DD HH:mm:ss");
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
        var start = $.fullCalendar.formatDate(event.start, "Y-MM-DD HH:mm:ss");
        var end = $.fullCalendar.formatDate(event.end, "Y-MM-DD HH:mm:ss");
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
});