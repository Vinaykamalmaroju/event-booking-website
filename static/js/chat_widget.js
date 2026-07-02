// ======================================
// Toggle Chat Window
// ======================================

const toggle = document.getElementById("chat-toggle");
const windowBox = document.getElementById("chat-window");

toggle.addEventListener("click", function () {

    if (windowBox.style.display === "block") {

        windowBox.style.display = "none";

    } else {

        windowBox.style.display = "block";

    }

});


// ======================================
// Send Chat
// ======================================

function sendChat() {

    const input = document.getElementById("chat-input");

    const message = input.value.trim();

    if (message === "") {
        return;
    }

    const messages = document.getElementById("messages");

    // Display customer message

    messages.innerHTML += `
        <div class="user">
            ${message}
        </div>
    `;

    messages.scrollTop = messages.scrollHeight;

    input.value = "";

    fetch("/chatbot", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    })

    .then(response => {

        if (!response.ok) {
            throw new Error("Network response was not OK");
        }

        return response.json();

    })

    .then(data => {

        // Display bot reply

        messages.innerHTML += `
            <div class="bot">
                ${data.reply}
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;

        // ----------------------------------
        // Connect to Human Support
        // ----------------------------------

        if (data.redirect) {

            messages.innerHTML += `
                <div class="bot">
                    🔄 Redirecting you to Human Support...
                </div>
            `;

            messages.scrollTop = messages.scrollHeight;

            setTimeout(function () {

                window.location.href = data.redirect;

            }, 2000);

        }

    })

    .catch(error => {

        console.error(error);

        messages.innerHTML += `
            <div class="bot">
                ❌ Server Error! Please try again later.
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;

    });

}


// ======================================
// Send on Enter Key
// ======================================

const chatInput = document.getElementById("chat-input");

if (chatInput) {

    chatInput.addEventListener("keypress", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendChat();

        }

    });

}