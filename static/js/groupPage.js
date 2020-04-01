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
            aysnc: false,
            url: '/saveSong/' + encodeURIComponent(currentSong),
            success: function(response) {
               if(JSON.parse(response).savedSong){
                 alert("Successfully saved the song!");
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
            socket.emit('fetchSong', {
                msg: song
            });
        }
    });
    $('#rateGroup').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var rating = parseInt($('#rateGroup input').val());
            if(!Number.isInteger(rating) || rating < 1 || rating > 5){
                alert("Please enter an integer rating between 1 and 5.")
            }
            else{
                $('#rateGroup input').val('');
                socket.emit('rateGroup', {
                    msg: rating
                });
                $("#rateGroup input").hide();
                alert("Successfully submitted rating!");
            }
        }
    });
    $('#reportProblem').on('keypress', function(key) {
        if (key.keyCode == 13) {
            var report = $('#reportProblem input').val();
            $('#reportProblem input').val('');
            socket.emit('reportProblem', {
                msg: report
            });
            alert("Successfully submitted report!");
        }
    });
    function showMemberCount() {
        $.ajax({
            type: 'GET',
            aysnc: false,
            url: '/getMemberCount',
            success: function(response) {
                var memberCount = JSON.parse(response).memberCount;
                if(memberCount == -1){
                    window.location.href = '/home';
                }
                $("#MemberCount p").remove();
                $("#MemberCount").append("<p>Active Members: " + memberCount + "</p>");
            }
        });
    }
    function showRatingAverage() {
        $.ajax({
            type: 'GET',
            aysnc: false,
            url: '/getRatingAverage',
            success: function(response) {
                var ratingAverage = JSON.parse(response).averageRating;
                if(ratingAverage == -1){
                    window.location.href = '/home';
                }
                $("#RatingAverage p").remove();
                $("#RatingAverage").append("<p>Average Rating: " + ratingAverage + "</p>");
            }
        });
    }
    function showInputFieldToDJ() {
        $.ajax({
            type: 'GET',
            aysnc: false,
            url: '/isDJ/' + encodeURIComponent(socket.id).slice(-32),
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
        //showMemberCount();
        //showRatingAverage();
        showInputFieldToDJ();
    }, 1000);
});
