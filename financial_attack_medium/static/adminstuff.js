// I don't remember even ever using this
// to be honest I think I didn't actually ever press it
// it's no different than just ctrl+r lol
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('waiting').style.display = 'none'
    var refreshButton = document.getElementById('refreshbutton');

    sendButton.addEventListener('click', function() {
        location.reload();
    });
});