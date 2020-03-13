var socket;
var currentSong = 0;
$(document).ready(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/group');
    socket.on('connect', function() {
        socket.emit('joinGroup', {});
    });
    socket.on('update', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
    });
    socket.on('video', function(data) {
        currentSong = data.msg;
        $("#EmbeddedSong iframe").remove();
        $("#EmbeddedSong").append("<iframe width='560' height='315' src='https://www.youtube.com/embed/" + data.msg + "?autoplay=1&controls=0' allow='autoplay'></iframe>");
    });
    document.getElementById("leaveButton").onclick = function() {
        socket.emit('leaveGroup', {}, function() {
            window.location.href = '/home';
        });
    };
    document.getElementById("saveSongButton").onclick = function() {
        $.ajax({
            type: 'POST',
            url: '/saveSong/' + encodeURIComponent(currentSong),
            success: function(response) {
               if(JSON.parse(response).savedSong){
                 alert("Successfully saved the song!");
               }
               else{
                alert("Unable to save the song! Please try again.");
               }
            }
        });
    };
    $('#messageInput').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var message = $('#messageInput input').val();
            $('#messageInput input').val('');
            socket.emit('sendMessage', {
                msg: message
            });
        }
    });
    $('#DJInput').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var song = $('#DJInput input').val();
            $('#DJInput input').val('');
            socket.emit('broadcastSong', {
                msg: song
            });
        }
    });
    function showMemberCount() {
        $.ajax({
            type: 'GET',
            url: '/getMemberCount',
            success: function(response) {
                $("#MemberCount p").remove();
                $("#MemberCount").append("<p>Active Members: " + JSON.parse(response).memberCount + "</p>");
            }
        });
    }
    function showInputFieldToDJ() {
        $.ajax({
            type: 'POST',
            url: '/isDJ/' + encodeURIComponent(socket.id),
            success: function(response) {
                if (JSON.parse(response).isDJ) {
                    $("#DJInput input").show();
                }
                else{
                    $("#DJInput input").hide();
                }
            }
        });
    }
    setInterval(function() {
        showMemberCount();
        showInputFieldToDJ();
    }, 1000);
});