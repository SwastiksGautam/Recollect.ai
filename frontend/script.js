let isProcessing = false;

// --- CONFIGURATION ---
// Ensure this has NO trailing slash. 
// It points to your live Render backend.
const BACKEND_URL = "https://recollect-ai.onrender.com";

const pdfInputEl = document.getElementById("pdfInput");
const filePreview = document.getElementById("filePreview");
const fileNameDisplay = document.getElementById("fileNameDisplay");
const cancelFileBtn = document.getElementById("cancelFile");
const inputEl = document.getElementById("input");

// 1. Handle File Selection UI
document.getElementById("addFile").addEventListener("click", () => pdfInputEl.click());

pdfInputEl.addEventListener("change", () => {
    if (pdfInputEl.files.length > 0) {
        fileNameDisplay.innerText = `📄 ${pdfInputEl.files[0].name} (Ready)`;
        filePreview.style.display = "flex";
    }
});

cancelFileBtn.addEventListener("click", () => {
    pdfInputEl.value = "";
    filePreview.style.display = "none";
});

// 2. Message Display
function addMessage(text, sender) {
    const chat = document.getElementById("chat");
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerHTML = `<b>${sender === "user" ? "You" : "AI"}:</b> ${text}`;
    chat.prepend(msg); // Newest messages on top
    return msg;
}

// 3. Unified Send Logic
async function send() {
    if (isProcessing) return;

    const input = inputEl.value.trim();
    const pdfFile = pdfInputEl.files[0];

    if (!input && !pdfFile) return;

    isProcessing = true;

    // UI Feedback
    if (input) addMessage(input, "user");
    if (pdfFile) addMessage(`Attached PDF: ${pdfFile.name}`, "user");

    // Reset Inputs
    inputEl.value = "";
    pdfInputEl.value = "";
    filePreview.style.display = "none";

    const thinkingMsg = addMessage("Thinking...", "ai");

    try {
        let data;
        if (pdfFile) {
            const formData = new FormData();
            formData.append("file", pdfFile);
            if (input) formData.append("initial_query", input);

            // Fetch to /upload-pdf on Render
            data = await fetch(`${BACKEND_URL}/upload-pdf`, {
                method: "POST",
                body: formData
            }).then(res => res.json());

        } else {
            // Fetch to /chat on Render (Explicitly hitting the /chat endpoint)
            data = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input })
            }).then(res => res.json());
        }

        // Check if data.answer exists to avoid "undefined"
        if (data && data.answer) {
            thinkingMsg.innerHTML = `<b>AI:</b> ${data.answer}`;
        } else {
            thinkingMsg.innerHTML = `<b>AI:</b> Received a response, but no answer was found.`;
        }

    } catch (err) {
        console.error("Fetch Error:", err);
        thinkingMsg.innerHTML = `<b>AI:</b> Error: Could not connect to backend.`;
    } finally {
        isProcessing = false;
    }
}

// 4. Event Listeners for sending
document.getElementById("sendBtn").addEventListener("click", send);
inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
    }
});

// Clear memory automatically when the page is refreshed
window.onload = async () => {
    try {
        await fetch(`${BACKEND_URL}/clear-memory`, { method: "POST" });
        console.log("Memory cleared for new session.");
    } catch (err) {
        console.error("Auto-clear failed:", err);
    }
};