let isProcessing = false;

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
    chat.prepend(msg); // Works with column-reverse CSS
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

            data = await fetch("http://127.0.0.1:8000/upload-pdf", {
                method: "POST",
                body: formData
            }).then(res => res.json());
        } else {
            data = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input })
            }).then(res => res.json());
        }
        thinkingMsg.innerHTML = `<b>AI:</b> ${data.answer}`;
    } catch (err) {
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