/*var sendButton = document.getElementById('sendButton');
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
            socket.on('receive_message', function(data) {
                console.log('New message received:', data);
                display_new_message(data.msg, data.user);
            });

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
}*/




    const socket = io();

    let roomJoined;
    const createRoom = (user, friend)=>{
        roomJoined = false;  // Flag to track room join status
        // Join the room with your friend
        socket.emit('join_room', { user_id: user, friend_id: friend });
    }

    const chatBox = document.getElementById('chatBox');
    const createMessage = (message) => {
        const content = `
        <div>
            <span> ${message}</span>
        </div>
        `;
        chatBox.innerHTML += content;
    }
    // Listen for the confirmation that you've joined the room
    socket.on('joined_room', (data)=> {
        console.log('Joined rooms: ' + data.room_id);
        roomJoined = true;
    });


    socket.on("message", (data) => {
        console.log('roomJoined: ' + rm + roomJoined + ' id ');
        
        
    
    // Check if the chatBox exists
    if (chatBox) {
        console.log("ChatBox found, appending new message...");

        createMessage(data.content);
        
        // Optional: Scroll to the bottom to show the latest message
        chatBox.scrollTop = messageContainer.scrollHeight;
        } 
        else {
            console.error("ChatBox element not found on this page.");
        }
    });


    
    socket.on('new_message', function(data) {
        var messageList = document.getElementsByClassName('friend');
        console.log('Sending message...');
        console.log('roomJoined: ' + rm + roomJoined + ' id ');
        console.log('New message from user ' + data.sender_id + ': ' + data.content);
        if (data.room_id == rm) {
            console.log('the program sucess');
            
        } else {
            console.log('the program failed');
            
        }
        messageList.textcontent = data.content;
        alert('New message from user ' + data.sender_id + ': ' + data.content);
        
        const chatBox = document.getElementById('chatBox');
    
    // Check if the chatBox exists
    if (chatBox) {
        console.log("ChatBox found, appending new message...");

        // Create a new paragraph element to hold the new message
        const newMessageDiv = document.createElement('div');
        //newMessageDiv.style.backgroundColor = 'blue'; // Background color blue
        
        // Set the content of the new message (sender_id and message content)
        newMessageDiv.textContent = data.content;
        
        // Apply inline styles: text color red and background color blue
        newMessageDiv.style.color = 'red';           // Text color red
        newMessageDiv.style.backgroundColor = 'black'; // Background color blue
        newMessageDiv.style.padding = '10px';        // Add some padding
        newMessageDiv.style.marginTop = '10px';   // Add space between messages
        newMessageDiv.style.borderRadius = '5px';    // Optionally, round the corners

        // Generate a unique id for this message div
        const uniqueId = `message-${data.sender_id}-${Math.floor(Math.random() * 10000)}`;
        //newMessageDi.id = uniqueId;

        // Append the new message to the parent container
        chatBox.appendChild(newMessageDiv);
        //newMessageDi.appendChild(newMessageDiv);
        
        // Optional: Scroll to the bottom to show the latest message
        chatBox.scrollTop = messageContainer.scrollHeight;
        } 
        else {
            console.error("ChatBox element not found on this page.");
        }
        
        // Optionally, update the message list or notification badge
    });
    function sendMessage(user_id, receiver_id) {
        console.log('Sending message...');
        console.log('roomJoined: ' + roomJoined);
        alert('poopl');
        //if (roomJoined){
            var input = document.getElementById("message_input");
            socket.emit('send_message', {'sender_id': user_id, 'receiver_id': receiver_id, 'content': input.value});
            input.value = '';
        /*}
        else {
            console.warn('Cannot send message; not yet joined to room.');
        }*/
    }

    /*var user_id = "{{ tel }}";  // Embed the user_id from Jinja2
        var socket = io();
        socket.on('connect', function() {
            socket.emit('join', {'user_id': user_id});
        });*/
        
        /*var messageContainer = document.getElementById("messages");
        var newMessageDiv = document.createElement("div");
        newMessageDiv.className = 'friend';
        var newMessageSpan = document.createElement("span");
        newMessageSpan.textContent = data.content;
        newMessageDiv.appendChild(newMessageSpan);
        messageContainer.appendChild(newMessageDiv);*/