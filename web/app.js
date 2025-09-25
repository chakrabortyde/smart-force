const $ = sel => document.querySelector(sel);
const messagesEl = $("#messages");
const form = $("#chat-form");
const input = $("#message");
const statusEl = $("#status");
const uploadBtn = $("#upload-btn");
const filesEl = $("#files");

// session id persisted in localStorage
const SESSION_KEY = "rag_session_id";
function getSession() {
  let sid = localStorage.getItem(SESSION_KEY);
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sid);
  }
  return sid;
}

function addMsg(text, who, sources=[]) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  if (sources && sources.length >0 && who === "bot") {
    const s = document.createElement("div");
    s.className = "sources";
    // s.textContent = "Sources: " + sources.map(x => x.path).join(", ");
    
    s.innerHTML = "Sources: " + sources.map(
          src => `<li><a href="${src}" target="_blank" download>📥 Download </a> </li>`
        ).join("");
    messagesEl.appendChild(s);
  }

  
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// async function pingStatus() {
//   try {
//     // const res = await fetch("/status");
//     // const j = await res.json();
//     // statusEl.textContent = j.ingesting ? "Ingestion in progress… answering from cache if possible." : "";
//   } catch (e) {
//     statusEl.textContent = "";
//   }
// }
// setInterval(pingStatus, 3000);
// pingStatus();

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  addMsg(q, "user");
  input.value = "";
  // Show loader
  document.getElementById("loader").style.display = "block";
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: q, session_id: getSession() })
    });
    const j = await res.json();
    if (j.error) throw new Error(j.error);
    
    addMsg(j.answer, "bot", j.sources || []);
    // Hide loader
    document.getElementById("loader").style.display = "none";
  } catch (err) {
    
    addMsg("Error: " + err.message, "bot");
    document.getElementById("loader").style.display = "none";
  }
});

// uploadBtn.addEventListener("click", async () => {
//   const files = filesEl.files;
//   if (!files || !files.length) {
//     $("#upload-msg").textContent = "Select one or more files first.";
//     return;
//   }
//   const formData = new FormData();
//   for (const f of files) formData.append("files", f);
//   $("#upload-msg").textContent = "Uploading & ingesting…";
//   try {
//     const res = await fetch("/upload", { method: "POST", body: formData });
//     const j = await res.json();
//     if (j.error) throw new Error(j.error);
//     $("#upload-msg").textContent = `Saved ${j.saved.length} file(s). Ingested ${j.ingested_chunks} chunks.`;
//     //pingStatus();
//   } catch (e) {
//     $("#upload-msg").textContent = "Upload failed: " + e.message;
//   }
// });
