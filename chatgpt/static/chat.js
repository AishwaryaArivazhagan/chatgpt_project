function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const chatBox = document.getElementById("chat-box");

    fetch("/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `message=${userInput}`,
    })
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<div>You: ${userInput}</div>`;
            chatBox.innerHTML += `<div>Bot: ${data.response}</div>`;
            document.getElementById("user-input").value = "";
        })
        .catch(error => console.error("Error:", error));
}
