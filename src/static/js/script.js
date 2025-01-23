let lastKnownHistoryLength = 0; // Keep track of the last known length of the conversation history
let isTyping = false; // Flag to ensure typing effect is not triggered multiple times

document.getElementById('modeToggle').addEventListener('click', () => {
    const body = document.body;
    body.classList.toggle('light-mode');
    const isLightMode = body.classList.contains('light-mode');
    document.getElementById('modeToggle').textContent = isLightMode ? 'Switch to Dark Mode' : 'Switch to Light Mode';
});

function updateTime() {
    const now = new Date();
    const dateString = now.toLocaleDateString();
    const timeString = now.toLocaleTimeString();

    document.getElementById('dateDisplay').textContent = dateString;
    document.getElementById('timeDisplay').textContent = timeString;
}

function startTypingEffect(textToDisplay) {
    const responseContainer = document.getElementById('responseContainer');
    if (isTyping) return; // Prevent starting a new typing effect while one is still running

    isTyping = true;
    responseContainer.innerHTML = ''; // Clear content first (for a new response)
    
    let index = 0;
    const typingInterval = setInterval(() => {
        if (index < textToDisplay.length) {
            responseContainer.innerHTML += textToDisplay[index]; // Append one character at a time
            index++;
        } else {
            clearInterval(typingInterval); // Stop when all characters are typed
            isTyping = false; // Unlock typing effect
        }
    }, 50);  // Adjust speed (50 ms per character)
}

function fetchResponse() {
    fetch('/api/responses')  // Fetch the response from your backend
        .then(response => response.json())
        .then(data => {
            if (data.length > lastKnownHistoryLength) {  // Check if new data has been added
                const latestResponse = data[data.length - 1];
                startTypingEffect(latestResponse.text); // Start typing the latest response
                lastKnownHistoryLength = data.length; // Update the known history length
            }
        })
        .catch(() => {
            document.getElementById('responseContainer').textContent = "Error fetching response.";
        });
}

// Call fetchResponse initially to load the first response
window.addEventListener('load', () => {
    updateTime();
    setInterval(updateTime, 1000);  // Update the time every second
    setInterval(fetchResponse, 500);  // Poll the backend for new responses every 500ms
});

function toggleMenu(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('dropdown');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

function hideMenu() {
    document.getElementById('dropdown').style.display = 'none';
}

window.addEventListener('click', hideMenu);
