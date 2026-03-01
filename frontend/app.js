/**
 * app.js  –  Multi-Agent AI Frontend
 * ───────────────────────────────────
 * Handles user input, calls the backend API, and renders chat bubbles
 * with step-by-step agent results.
 */

// ── Configuration ──────────────────────────────────────────────────
const API_BASE = "http://localhost:5000";
const ENDPOINT = `${API_BASE}/api/query/async`;  // sync endpoint (change to /api/query/async for async)

// ── DOM references ─────────────────────────────────────────────────
const chatArea = document.getElementById("chat-area");
const queryInput = document.getElementById("query-input");
const sendBtn = document.getElementById("send-btn");
const welcomeMessage = document.getElementById("welcome-message");
const suggestions = document.getElementById("suggestions");
const badgeA = document.getElementById("badge-a");
const badgeB = document.getElementById("badge-b");


// ── State ──────────────────────────────────────────────────────────
let isProcessing = false;


// ═════════════════════════════════════════════════════════════════════
//  EVENT LISTENERS
// ═════════════════════════════════════════════════════════════════════

sendBtn.addEventListener("click", () => handleSend());

queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// Suggestion chips
suggestions.addEventListener("click", (e) => {
    const chip = e.target.closest(".suggestion-chip");
    if (!chip) return;
    queryInput.value = chip.dataset.query;
    handleSend();
});


// ═════════════════════════════════════════════════════════════════════
//  CORE LOGIC
// ═════════════════════════════════════════════════════════════════════

async function handleSend() {
    const query = queryInput.value.trim();
    if (!query || isProcessing) return;

    // Hide welcome screen on first query
    if (welcomeMessage) welcomeMessage.remove();

    // Show user bubble
    appendBubble(query, "user");
    queryInput.value = "";

    // Show thinking indicator & activate agent badges
    const thinkingEl = showThinking();
    setAgentActive("a", true);
    isProcessing = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch(ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        // Remove thinking indicator
        thinkingEl.remove();

        if (!response.ok) {
            appendError(data.error || "Something went wrong.");
        } else {
            renderAgentResponse(data);
        }
    } catch (err) {
        thinkingEl.remove();
        appendError(`Could not reach the backend at ${API_BASE}. Is the server running?`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        setAgentActive("a", false);
        setAgentActive("b", false);
        scrollToBottom();
    }
}


// ═════════════════════════════════════════════════════════════════════
//  RENDERING HELPERS
// ═════════════════════════════════════════════════════════════════════

/**
 * Append a chat bubble to the chat area.
 */
function appendBubble(content, type) {
    const el = document.createElement("div");
    el.className = `bubble bubble--${type}`;

    if (type === "user") {
        el.textContent = content;
    } else {
        el.innerHTML = content;
    }

    chatArea.appendChild(el);
    scrollToBottom();
    return el;
}

/**
 * Display an error bubble.
 */
function appendError(message) {
    const html = `
    <div class="bubble__label">⚠️ Error</div>
    <p>${escapeHtml(message)}</p>
  `;
    const el = document.createElement("div");
    el.className = "bubble bubble--agent bubble--error";
    el.innerHTML = html;
    chatArea.appendChild(el);
    scrollToBottom();
}

/**
 * Render the full agent response with step cards and final answer.
 */
function renderAgentResponse(data) {
    const { steps, final_answer } = data;

    // Build step cards HTML
    let stepsHtml = '<div class="bubble__label">Agent Pipeline</div>';

    if (steps && steps.length > 0) {
        steps.forEach((step, i) => {
            const task = step.task || {};
            const description = task.description || "Task";
            const taskId = task.task_id || `task_${i + 1}`;
            const hasError = !!step.error;

            const cardClass = hasError ? "step-card step-card--error" : "step-card";
            const tagLabel = hasError ? "error" : taskId;

            let body = "";
            if (hasError) {
                body = escapeHtml(step.error);
            } else {
                body = escapeHtml(String(step.result));
            }

            stepsHtml += `
        <div class="${cardClass}">
          <div class="step-card__header">
            ⚙️ Step ${i + 1}: ${escapeHtml(description)}
            <span class="tag">${tagLabel}</span>
          </div>
          <div class="step-card__body">${body}</div>
        </div>
      `;
        });
    }

    // Final answer
    if (final_answer) {
        stepsHtml += `
      <div class="final-answer">
        <div class="final-answer__title">✨ Final Answer</div>
        ${formatFinalAnswer(final_answer)}
      </div>
    `;
    }

    // Activate Agent B briefly for visual effect
    setAgentActive("b", true);
    setTimeout(() => setAgentActive("b", false), 2000);

    appendBubble(stepsHtml, "agent");
}

/**
 * Show the "thinking" indicator.
 */
function showThinking() {
    const el = document.createElement("div");
    el.className = "thinking";
    el.innerHTML = `
    <div class="thinking__dots">
      <span class="thinking__dot"></span>
      <span class="thinking__dot"></span>
      <span class="thinking__dot"></span>
    </div>
    Agents are working…
  `;
    chatArea.appendChild(el);
    scrollToBottom();
    return el;
}

/**
 * Format the final answer (supports bold markdown-ish syntax).
 */
function formatFinalAnswer(text) {
    return escapeHtml(text)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");
}

// (icon logic removed — tasks are now generic, no hardcoded types)

/**
 * Set an agent badge to active / inactive.
 */
function setAgentActive(agent, active) {
    const badge = agent === "a" ? badgeA : badgeB;
    badge.classList.toggle("active", active);
}

/**
 * Scroll chat area to the bottom.
 */
function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/**
 * Escape HTML to prevent XSS.
 */
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
