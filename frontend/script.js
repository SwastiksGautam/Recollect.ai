let isProcessing = false;
let activeFileName = null; // 🌟 Track the current file

const BACKEND_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://recollect-ai.onrender.com";

const pdfInputEl = document.getElementById("pdfInput");
const filePreview = document.getElementById("filePreview");
const fileNameDisplay = document.getElementById("fileNameDisplay");
const cancelFileBtn = document.getElementById("cancelFile");
const inputEl = document.getElementById("input");

document.getElementById("addFile").addEventListener("click", () => pdfInputEl.click());

pdfInputEl.addEventListener("change", () => {
    if (pdfInputEl.files.length > 0) {
        activeFileName = pdfInputEl.files[0].name; // 🌟 Capture name
        fileNameDisplay.innerText = `📄 ${activeFileName} (Ready)`;
        filePreview.style.display = "flex";
    }
});

cancelFileBtn.addEventListener("click", () => {
    pdfInputEl.value = "";
    activeFileName = null; // 🌟 Reset name
    filePreview.style.display = "none";
});

function addMessage(text, sender) {
    const chat = document.getElementById("chat");
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerHTML = `<b>${sender === "user" ? "You" : "AI"}:</b> ${text}`;
    chat.prepend(msg);
    return msg;
}

async function send() {
    if (isProcessing) return;
    const input = inputEl.value.trim();
    const pdfFile = pdfInputEl.files[0];
    if (!input && !pdfFile) return;

    isProcessing = true;
    if (input) addMessage(input, "user");
    if (pdfFile) addMessage(`Attached PDF: ${pdfFile.name}`, "user");

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

            data = await fetch(`${BACKEND_URL}/upload-pdf`, {
                method: "POST",
                body: formData
            }).then(res => res.json());

        } else {
            data = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    input: input,
                    current_file: activeFileName // 🌟 Send filename to backend
                })
            }).then(res => res.json());
        }

        thinkingMsg.innerHTML = `<b>AI:</b> ${data.answer || "No response."}`;

    } catch (err) {
        console.error("Fetch Error:", err);
        thinkingMsg.innerHTML = `<b>AI:</b> Error: Could not connect to backend.`;
    } finally {
        isProcessing = false;
    }
}

document.getElementById("sendBtn").addEventListener("click", send);
inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
    }
});

window.onload = async () => {
    console.log("Initializing new session...");
    try {
        const response = await fetch(`${BACKEND_URL}/clear-memory`, { 
            method: "POST" 
        });
        const data = await response.json();
        console.log("Session Reset:", data.answer);
    } catch (err) {
        console.warn("Auto-clear failed. Backend might be waking up...", err);
    }
};