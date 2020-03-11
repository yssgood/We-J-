var socket;
$(document).ready(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/group');
    socket.on('connect', function() {
        socket.emit('joinGroup', {});
    });
    socket.on('update', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
    });
    socket.on('message', function(data) {
        $("#EmbeddedSong iframe").remove();
        $("#EmbeddedSong").append("<iframe width='560' height='315' src='https://www.youtube.com/embed/" + data.msg + "?autoplay=1&controls=0&loop=1&playlist=" + data.msg + "' allow='autoplay'></iframe>");
    });
    document.getElementById("leaveButton").onclick = function () {
        socket.emit('leaveGroup', {}, function(){
            socket.disconnect();
            window.location.href = "/home";
        });
    }
    $('#DJInput').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var song = $('#DJInput input').val();
            $('#DJInput input').val('');
            socket.emit('broadcastSong', {
                msg: song
            });
        }
    })
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
        return false;
    }
    setInterval(showInputFieldToDJ, 1000);
});