var sendButton = document.getElementById('sendButton');
var messageForm = document.getElementById('messageForm');

sendButton.addEventListener('submit', ()=> {
    console.log("Button clicked");
    var messageInput = document.getElementById('messageInput');
    var message = messageInput.value;
    console.log(message);
    messageInput.value = '';
});

function online(user, friend, friendName) {
    $(document).ready(function() {
        console.log('====================================')
        console.log("Loged")
        console.log('====================================')
        var socket = io.connect('http://' + document.domain + ':' + location.port);

        socket.on('connect', function() {
            console.log('WebSocket connection established');

            // Join the room
            socket.emit('join', { user: user, friend: friend });

            // Fetch initial data
            socket.emit('fetch_user_login_data', { friend: friend });
            socket.emit('fetch_unread_count', { user: user, friend: friend });

            // Handle received messages
            /*socket.on('receive_message', function(data) {
                console.log('New message received:', data);
                display_new_message(data.msg, data.user);
            });*/

            socket.on('receive_message', function(data) {
                if (data.user === friend) {
                    $('.message_chat').append('<div class="friend"><span>' + data.msg + '</span></div>');
                } else if (data.user === user) {
                    $('.message_chat').append('<div class="user"><span>' + data.msg + '</span></div>');
                }
            });

            // Handle user status
            socket.on('user_status', function(data) {
                console.log('User status:', data);
                var activeElement = $('#active' + friendName.replace(' ', ''));
                if (data.online) {
                    activeElement.addClass('active');
                } else {
                    activeElement.removeClass('active');
                }
            });

            // Handle unread count
            socket.on('unread_count', function(data) {
                console.log('Unread count:', data);
                var messageId = "#" + friendName.replace(' ', '');
                if (data.count > 0) {
                    $(messageId).addClass('unread').html(data.count);
                } else {
                    $(messageId).removeClass('unread').html('');
                }
            });

            // Send a message
            $('#messageForm').submit(function(event) {
                event.preventDefault(); // Prevent the form from submitting the traditional way
                console.log("Successful");
                var message = $('#messageInput').val();
                console.log(message);
                socket.emit('send_message', { user: user, friend: friend, message: message });
                $('#messageInput').val('');
            });

            // Mark messages as seen when the user clicks on a conversation
            $(document).on('click', '#change' + friendName.replace(' ', ''), function() {
                socket.emit('mark_as_seen', { user: user, friend: friend });
            });

            // Update user activity periodically
            setInterval(function() {
                socket.emit('update_user_activity', { user: user });
                socket.emit('fetch_user_login_data', { friend: friend });
                socket.emit('fetch_unread_count', { user: user, friend: friend });
            }, 100000); // Adjust the interval as needed
        });
    });
}
