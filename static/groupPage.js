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
        $("#EmbeddedSong").append("<iframe width='560' height='315' src='https://www.youtube.com/embed/" + data.msg + "?autoplay=1&controls=0&mute=1'></iframe>");
    });
    $('#DJInput').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var song = $('#DJInput input').val()
            $('#DJInput input').val('');
            socket.emit('broadcastSong', {
                msg: song
            });
            $("#DJInput input").remove();
            $("#EmbeddedSong iframe").remove();
        }
    })
    $('.EmbeddedSong').on('click', function(event) { });
});

function showInputFieldToDJ() {
    $.ajax({
        type: 'POST',
        url: '/isDJ',
        success: function(response) {
            if (JSON.parse(response).isDJ) {
                var input = document.createElement("input");
                input.id = "song";
                input.type = "text";
                document.getElementById("DJInput").appendChild(input);
            }
        }
    });
    return false;
}