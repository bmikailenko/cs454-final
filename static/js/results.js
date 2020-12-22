$(document).ready(function() {
    $(".redirect-button").click(function() {
        var win = window.open('https://www.metacritic.com' + $(this).val(), '_blank');
        if (win) {
            //Browser has allowed it to be opened
            win.focus();
        } else {
            //Browser has blocked it
            alert('Please allow popups for this website');
        }
    });
});

$(document).on('keypress',function(e) {
    if(e.which == 13) {
        window.location.replace("/");
    }
});