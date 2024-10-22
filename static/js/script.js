function online(user,friend,friendName){
    $(document).ready(function(){
        var use = friendName;
        var replace = use.replace(' ','');
        
        function update_user_activity(){    
            var action = 'update_time';
            var other = friend;
            var person = user;
            $.ajax({
            url:"/action",
            method:"POST",
            data:{action:action,
                other:other,
                person:person},
            success:function(data)
            {
                
            }
            });
        }

        /*setInterval(function(){ 
        update_user_activity();
        }, 5000);

        //fetch_user_login_data();

        setInterval(function(){
        fetch_user_login_data();
        }, 5000);*/


        function fetch_user_login_data(){
            var action = "fetch_data";
            var other = friend;
            var person = user;
            var active = "#active"+ replace;
            $.ajax({
            url:"/action",
            method:"POST",
            data:{action:action,
                other:other,
                person:person},
            success:function(data)
            {
                if(data == 0)'' ;
                else{
                $(active).addClass('active');
                }
            }
            });
        }

       /*unread();
        setInterval(function(){
            unread();
        }, 20000);*/


        function unread(){    
            var action = "unseen";
            var other = friend;
            var person = user;

            $.ajax({
            url:"/action",
            method:"POST",
            data:{action:action,
                other:other,
                person:person},
            success:function(data)
            {
                if(data == 0)'' ;
                else{
                        var messageId = "#"+ replace;
                        
                        $(messageId).addClass('unread').html(data);
                    }
                    var changeId = "#change"+replace;
                    $(changeId).click(function(){
                        var action = "seen";
                        var other = friend;
                        var person = user;
                        $.ajax({
                            url:"/action",
                            method:"POST",
                            data:{action:action,
                                other:other,
                                person:person},
                            success:function(data){
                                }
                        });
                    });
                }
            });
        }

        // Function to refresh the page
        function refreshPage() {
            location.reload();
        }

        // Example: Call refreshPage function every minute (60000 ms)
        /*setInterval(function() {
            refreshPage();
        }, 60000); // Adjust the interval as needed*/

        function performAllActions() {
            update_user_activity();
            fetch_user_login_data();
            unread();
            //refreshPage();
        }

        // Call all functions initially
        performAllActions();

        // Call performAllActions function every 5000 ms (5 seconds)
        setInterval(performAllActions, 10000);
        
    });
}