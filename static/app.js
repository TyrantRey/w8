let currentSessionId = null;
let currentAttachmentId = null;

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

function formatTime(ts) {
  if (!ts) return "";
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return ts;
  }
}

async function loadSessions() {
  const sessions = await fetchJSON("/api/sessions");
  const list = document.getElementById("sessionList");
  list.innerHTML = "";

  sessions.forEach((session) => {
    const item = document.createElement("div");
    item.className =
      "session-item" + (session.id === currentSessionId ? " active" : "");
    item.innerHTML = `
      <div class="session-title">${escapeHtml(session.title)}</div>
      <div class="session-time">${formatTime(session.updated_at)}</div>
    `;
    item.onclick = () => selectSession(session.id);
    list.appendChild(item);
  });

  if (!currentSessionId && sessions.length > 0) {
    await selectSession(sessions[0].id);
  }
}

async function createSession() {
  const session = await fetchJSON("/api/sessions", { method: "POST" });
  currentSessionId = session.id;
  await loadSessions();
  await loadMessages();
}

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  currentAttachmentId = null;
  document.getElementById("uploadStatus").textContent = "";
  await loadSessions();
  await loadMessages();
}

async function loadMessages() {
  if (!currentSessionId) return;
  const messages = await fetchJSON(
    `/api/sessions/${currentSessionId}/messages`,
  );
  const container = document.getElementById("chatMessages");
  container.innerHTML = "";

  messages.forEach((msg) => {
    const el = document.createElement("div");
    el.className = `message ${msg.role}`;
    const attachmentInfo = msg.original_name
      ? `<div class="attachment">Attachment: ${escapeHtml(msg.original_name)}</div>`
      : "";

    const regenBtn =
      msg.role === "assistant"
        ? `<button class="regen-btn" data-id="${msg.id}">Regenerate</button>`
        : "";

    el.innerHTML = `
      <div class="message-meta">
        <span class="role">${escapeHtml(msg.role)}</span>
        <span class="time">${formatTime(msg.timestamp)}</span>
        <span class="status">${escapeHtml(msg.status || "")}</span>
      </div>
      <div class="message-content">${escapeHtml(msg.content).replace(/\n/g, "<br>")}</div>
      ${attachmentInfo}
      <div class="message-actions">${regenBtn}</div>
    `;
    container.appendChild(el);
  });

  container.querySelectorAll(".regen-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-id");
      await regenerateMessage(id);
    });
  });

  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  if (!currentSessionId) {
    alert("Please create or select a session first.");
    return;
  }

  const input = document.getElementById("messageInput");
  const message = input.value.trim();
  if (!message) {
    alert("Message cannot be empty.");
    return;
  }

  const formData = new FormData();
  formData.append("session_id", currentSessionId);
  formData.append("message", message);
  if (currentAttachmentId) {
    formData.append("attachment_id", currentAttachmentId);
  }

  try {
    document.getElementById("sendBtn").disabled = true;
    const res = await fetch("/api/chat", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Chat failed");
    }

    input.value = "";
    currentAttachmentId = null;
    document.getElementById("uploadStatus").textContent = "";
    await loadSessions();
    await loadMessages();
  } catch (err) {
    alert(err.message);
  } finally {
    document.getElementById("sendBtn").disabled = false;
  }
}

async function uploadFile() {
  if (!currentSessionId) {
    alert("Please create or select a session first.");
    return;
  }

  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Please choose a file.");
    return;
  }

  const formData = new FormData();
  formData.append("session_id", currentSessionId);
  formData.append("file", fileInput.files[0]);

  try {
    const data = await fetchJSON("/api/upload", {
      method: "POST",
      body: formData,
    });
    currentAttachmentId = data.id;
    document.getElementById("uploadStatus").textContent =
      `Uploaded: ${data.original_name} (attachment_id=${data.id})`;
  } catch (err) {
    alert(err.message);
  }
}

async function regenerateMessage(messageId) {
  try {
    await fetchJSON(`/api/messages/${messageId}/regenerate`, {
      method: "POST",
    });
    await loadSessions();
    await loadMessages();
  } catch (err) {
    alert(err.message);
  }
}

async function stopResponse() {
  if (!currentSessionId) {
    alert("No active session.");
    return;
  }

  const formData = new FormData();
  formData.append("session_id", currentSessionId);

  try {
    const data = await fetchJSON("/api/stop", {
      method: "POST",
      body: formData,
    });
    alert(data.message);
  } catch (err) {
    alert(err.message);
  }
}

async function loadPreferences() {
  try {
    const prefs = await fetchJSON("/api/preferences");
    const map = {};
    prefs.forEach((p) => (map[p.key] = p.value));
    document.getElementById("prefName").value = map.name || "";
    document.getElementById("prefLanguage").value = map.language || "";
    document.getElementById("prefTone").value = map.tone || "";
  } catch (err) {
    console.error(err);
  }
}

async function savePreferences() {
  const formData = new FormData();
  formData.append("name", document.getElementById("prefName").value);
  formData.append("language", document.getElementById("prefLanguage").value);
  formData.append("tone", document.getElementById("prefTone").value);

  try {
    await fetchJSON("/api/preferences", {
      method: "POST",
      body: formData,
    });
    alert("Preferences saved.");
  } catch (err) {
    alert(err.message);
  }
}

document
  .getElementById("newSessionBtn")
  .addEventListener("click", createSession);
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("uploadBtn").addEventListener("click", uploadFile);
document.getElementById("stopBtn").addEventListener("click", stopResponse);
document
  .getElementById("savePrefsBtn")
  .addEventListener("click", savePreferences);

window.addEventListener("load", async () => {
  await loadPreferences();
  await loadSessions();
  if (!currentSessionId) {
    await createSession();
  }
});
