// This sets up a listener for button clicks whenever the assistant page loads
// It also trims the chatbox text on submission like everyone and their grandmother expects from a chatbox
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('waiting').style.display = 'none'
    var chatbox = document.getElementById('chatbox');
    var sendButton = document.getElementById('send');

    sendButton.addEventListener('click', function() {
        // debugging    
        console.log("buton clik")
        var usermessage = chatbox.value;
        chatbox.value = "";

        if (usermessage.trim() != '') {
            sendMessage(usermessage);
        }
    });
});

function sendMessage(usermessage) {
    // Update elements, additionally helps to make sure the user does not spam messages by accident 
    document.getElementById('send').disabled = true;
    document.getElementById('waiting').style.display = 'block'
    document.getElementById('chathistory').value += "\n\nUser: " + usermessage;

    // Actually send the chat to the server
    fetch('/send_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: "user", content: usermessage })
    })
    // i hate javascript so much man this stuff looks disgusting
    // we're just json formatting it and then updating stuff based on the content generated
    .then(response => response.json())
    .then(data => {
        var chatHistory = document.getElementById('chathistory');

        chatHistory.value += "\n\nAssistant: " + data.content;

        // Makes sure the scrolling of the textarea isn't total garbage
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // Undo the lock on the button and remove the awaiting message text
        document.getElementById('send').disabled = false;
        document.getElementById('waiting').style.display = 'none'
    })
    .catch(error => {
        // If we get an error somewhere, we still want to reenable the buttons
        console.error('Error:', error);
        document.getElementById('send').disabled = false;
        document.getElementById('waiting').style.display = 'none'
    });
}