var socket;
$(document).ready(function(){
    socket = io.connect('http://' + document.domain + ':' + location.port + '/group');
    socket.on('connect', function() {
        socket.emit('join', {});
    });
    socket.on('update', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
    });
});