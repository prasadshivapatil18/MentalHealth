/**
 * Aura AI & CDC Mental Health Analytics — Neo-Brutalist Frontend Controller
 * Handles real-time chat, Chart.js visualizations, PHQ-4 screener, and state explorer.
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initChat();
  initDashboard();
  initScreener();
});

/* ==========================================================================
   1. Tab Navigation Controller
   ========================================================================== */

function initNavigation() {
  const navButtons = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTabId = btn.getAttribute("data-tab");

      navButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(pane => pane.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetTabId);
      if (targetPane) {
        targetPane.classList.add("active");
      }

      // If switching to Dashboard, ensure charts are rendered
      if (targetTabId === "tab-dashboard") {
        if (!window.trendsChartLoaded) {
          loadDashboardData();
        }
      }
    });
  });
}

function switchToTab(tabId) {
  const targetBtn = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
  if (targetBtn) {
    targetBtn.click();
  }
}

/* ==========================================================================
   2. AI Chatbot (Aura) Controller
   ========================================================================== */

function initChat() {
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatMessages = document.getElementById("chatMessages");
  const typingIndicator = document.getElementById("typingIndicator");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const promptChips = document.querySelectorAll(".neo-chip");

  // Format initial timestamp
  const initialTime = document.getElementById("initialTime");
  if (initialTime) {
    initialTime.textContent = getCurrentTimeStr();
  }

  // Handle Send Form
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";
    appendUserMessage(text);
    showTyping(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      showTyping(false);
      appendBotMessage(data.reply, data.tag, data.confidence);
    } catch (err) {
      showTyping(false);
      appendBotMessage(
        "I'm experiencing a momentary connection issue. Please make sure the server is running or try again in a moment.",
        "error",
        0
      );
      console.error("Chat request failed:", err);
    }
  });

  // Prompt chips fill and submit
  promptChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      if (prompt) {
        chatInput.value = prompt;
        chatForm.dispatchEvent(new Event("submit"));
      }
    });
  });

  // Reset / Clear Chat
  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = `
      <div class="msg-group bot-group">
        <div class="bubble-avatar bot-avatar">🌿</div>
        <div class="bubble-content">
          <div class="bubble-header">
            <span class="sender-name">Aura</span>
            <span class="msg-timestamp">${getCurrentTimeStr()}</span>
            <span class="bubble-tag">RESET</span>
          </div>
          <div class="neo-bubble bot-bubble">
            Chat cleared! I'm here and ready to listen whenever you'd like to share. How can I support you right now?
          </div>
        </div>
      </div>
    `;
  });

  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "msg-group user-group";
    row.innerHTML = `
      <div class="bubble-avatar user-avatar">👤</div>
      <div class="bubble-content">
        <div class="bubble-header">
          <span class="sender-name">You</span>
          <span class="msg-timestamp">${getCurrentTimeStr()}</span>
        </div>
        <div class="neo-bubble user-bubble">${escapeHtml(text)}</div>
      </div>
    `;
    chatMessages.appendChild(row);
    scrollChatToEnd();
  }

  function appendBotMessage(text, tag, confidence) {
    const isCrisis = tag === "crisis" || text.includes("988") || text.includes("helpline");
    const row = document.createElement("div");
    row.className = "msg-group bot-group";

    const tagBadge = tag && tag !== "error" 
      ? `<span class="bubble-tag">${escapeHtml(tag.toUpperCase())} ${confidence ? Math.round(confidence * 100) + '%' : ''}</span>`
      : "";

    // Convert newlines to formatted line breaks
    const formattedText = escapeHtml(text).replace(/\n/g, "<br>");

    row.innerHTML = `
      <div class="bubble-avatar bot-avatar ${isCrisis ? 'crisis-avatar' : ''}">${isCrisis ? '🚨' : '🌿'}</div>
      <div class="bubble-content">
        <div class="bubble-header">
          <span class="sender-name">Aura</span>
          <span class="msg-timestamp">${getCurrentTimeStr()}</span>
          ${tagBadge}
        </div>
        <div class="neo-bubble bot-bubble ${isCrisis ? 'crisis-bubble' : ''}">
          ${formattedText}
        </div>
      </div>
    `;
    chatMessages.appendChild(row);
    scrollChatToEnd();
  }

  function showTyping(show) {
    if (show) {
      typingIndicator.style.display = "flex";
      chatMessages.appendChild(typingIndicator);
      scrollChatToEnd();
    } else {
      typingIndicator.style.display = "none";
    }
  }

  function scrollChatToEnd() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

/* ==========================================================================
   3. CDC Indicators Dashboard (Neo-Brutalist Charts)
   ========================================================================== */

let trendsChartInstance = null;
let demographicsChartInstance = null;
let cachedStatesData = [];

function initDashboard() {
  loadDashboardData();

  // Demographic buttons filter
  const demoButtons = document.querySelectorAll(".filter-tab");
  demoButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      demoButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const group = btn.getAttribute("data-group");
      loadDemographicsChart(group);
    });
  });

  // State selection change
  const stateSelect = document.getElementById("stateSelect");
  stateSelect.addEventListener("change", (e) => {
    const selectedState = e.target.value;
    updateStateDetails(selectedState);
  });
}

async function loadDashboardData() {
  try {
    // 1. Fetch Summary KPIs
    const summaryRes = await fetch("/api/dataset/summary");
    if (summaryRes.ok) {
      const summary = await summaryRes.json();
      populateKPIs(summary);
    }

    // 2. Fetch Trends for Line Chart
    const trendsRes = await fetch("/api/dataset/trends");
    if (trendsRes.ok) {
      const trends = await trendsRes.json();
      renderTrendsChart(trends);
      window.trendsChartLoaded = true;
    }

    // 3. Fetch Demographics for Bar Chart (Default: By Age)
    loadDemographicsChart("By Age");

    // 4. Fetch State Metrics
    const statesRes = await fetch("/api/dataset/states");
    if (statesRes.ok) {
      cachedStatesData = await statesRes.json();
      populateStateExplorer(cachedStatesData);
    }
  } catch (err) {
    console.error("Error loading CDC dashboard data:", err);
  }
}

function populateKPIs(summary) {
  if (!summary || !summary.national_stats) return;

  const nat = summary.national_stats;
  document.getElementById("kpiCombined").textContent = `${nat.combined_rate}%`;
  document.getElementById("kpiAnxiety").textContent = `${nat.anxiety_rate}%`;
  document.getElementById("kpiDepression").textContent = `${nat.depression_rate}%`;

  if (summary.highest_age_demographic) {
    document.getElementById("kpiHighestAge").textContent = summary.highest_age_demographic.group;
    document.getElementById("kpiHighestAgeVal").textContent = 
      `${summary.highest_age_demographic.average_prevalence}% Average Rate`;
  }

  if (summary.total_records) {
    const recordSpan = document.getElementById("dashRecordCount");
    if (recordSpan) recordSpan.textContent = summary.total_records.toLocaleString();
  }
}

function renderTrendsChart(trends) {
  const ctx = document.getElementById("trendsChart").getContext("2d");
  if (!ctx) return;

  if (trendsChartInstance) {
    trendsChartInstance.destroy();
  }

  const labels = trends.map(t => t.label || `P${t.period}`);
  const combinedData = trends.map(t => t.combined);
  const anxietyData = trends.map(t => t.anxiety);
  const depressionData = trends.map(t => t.depression);

  trendsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Combined Rate",
          data: combinedData,
          borderColor: "#FF5268",
          backgroundColor: "rgba(255, 82, 104, 0.12)",
          borderWidth: 3,
          tension: 0.3,
          pointRadius: 2,
          pointHoverRadius: 6,
          pointBackgroundColor: "#FF5268",
          pointBorderColor: "#111827",
          pointBorderWidth: 1.5,
          fill: true,
        },
        {
          label: "Anxiety Disorder",
          data: anxietyData,
          borderColor: "#FFC47F",
          backgroundColor: "transparent",
          borderWidth: 2.5,
          borderDash: [5, 4],
          tension: 0.3,
          pointRadius: 1,
          pointHoverRadius: 5,
        },
        {
          label: "Depressive Disorder",
          data: depressionData,
          borderColor: "#38BDF8",
          backgroundColor: "transparent",
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 1,
          pointHoverRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#FFF3D9",
          titleColor: "#111827",
          bodyColor: "#111827",
          borderColor: "#111827",
          borderWidth: 2,
          padding: 10,
          titleFont: { family: "'Space Grotesk', sans-serif", weight: "bold" },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", weight: "bold" },
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: "#596273",
            maxTicksLimit: 12,
            font: { family: "'Space Grotesk', sans-serif", size: 10, weight: "bold" },
          },
          border: { color: "#111827", width: 2 },
        },
        y: {
          grid: { color: "#E5E7EB" },
          ticks: {
            color: "#596273",
            callback: (v) => `${v}%`,
            font: { family: "'Space Grotesk', sans-serif", size: 10, weight: "bold" },
          },
          border: { color: "#111827", width: 2 },
          suggestedMin: 5,
          suggestedMax: 45,
        },
      },
    },
  });
}

async function loadDemographicsChart(group) {
  try {
    const res = await fetch(`/api/dataset/demographics?group=${encodeURIComponent(group)}`);
    if (!res.ok) return;

    const json = await res.json();
    const data = json.data || [];

    const ctx = document.getElementById("demographicsChart").getContext("2d");
    if (!ctx) return;

    if (demographicsChartInstance) {
      demographicsChartInstance.destroy();
    }

    const labels = data.map(d => d.subgroup);
    const combinedData = data.map(d => d.combined);
    const anxietyData = data.map(d => d.anxiety);
    const depressionData = data.map(d => d.depression);

    demographicsChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Combined Rate",
            data: combinedData,
            backgroundColor: "#FF5268",
            borderColor: "#111827",
            borderWidth: 2,
            borderRadius: 4,
          },
          {
            label: "Anxiety",
            data: anxietyData,
            backgroundColor: "#FFC47F",
            borderColor: "#111827",
            borderWidth: 2,
            borderRadius: 4,
          },
          {
            label: "Depression",
            data: depressionData,
            backgroundColor: "#BAE6FD",
            borderColor: "#111827",
            borderWidth: 2,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              color: "#111827",
              font: { family: "'Space Grotesk', sans-serif", weight: "bold", size: 11 },
              boxWidth: 12,
            },
          },
          tooltip: {
            backgroundColor: "#FFF3D9",
            titleColor: "#111827",
            bodyColor: "#111827",
            borderColor: "#111827",
            borderWidth: 2,
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`,
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: "#111827",
              font: { family: "'Space Grotesk', sans-serif", size: 10, weight: "bold" },
              maxRotation: 25,
            },
            border: { color: "#111827", width: 2 },
          },
          y: {
            grid: { color: "#E5E7EB" },
            ticks: {
              color: "#596273",
              callback: (v) => `${v}%`,
              font: { family: "'Space Grotesk', sans-serif", size: 10, weight: "bold" },
            },
            border: { color: "#111827", width: 2 },
            suggestedMax: 50,
          },
        },
      },
    });
  } catch (err) {
    console.error("Error loading demographics chart:", err);
  }
}

function populateStateExplorer(states) {
  const select = document.getElementById("stateSelect");
  const tableBody = document.getElementById("statesTableBody");
  if (!select || !states.length) return;

  select.innerHTML = "";
  states.forEach((st) => {
    const opt = document.createElement("option");
    opt.value = st.state;
    opt.textContent = `${st.state} (${st.combined}%)`;
    select.appendChild(opt);
  });

  // Default to first or California
  const defaultState = states.find(s => s.state === "California") || states[0];
  select.value = defaultState.state;
  updateStateDetails(defaultState.state);

  // Populate preview table
  if (tableBody) {
    tableBody.innerHTML = "";
    const previewList = [...states.slice(0, 5), ...states.slice(-3)];
    previewList.forEach(st => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${escapeHtml(st.state)}</strong></td>
        <td><strong>${st.combined}%</strong></td>
        <td>${escapeHtml(st.quartile || 'Standard')}</td>
      `;
      tableBody.appendChild(row);
    });
  }
}

function updateStateDetails(stateName) {
  const stateObj = cachedStatesData.find(s => s.state === stateName);
  if (!stateObj) return;

  document.getElementById("stateName").textContent = stateObj.state;
  document.getElementById("stateCombined").textContent = `${stateObj.combined}%`;
  document.getElementById("stateAnxiety").textContent = `${stateObj.anxiety}%`;
  document.getElementById("stateDepression").textContent = `${stateObj.depression}%`;
  document.getElementById("stateQuartile").textContent = `Quartile: ${stateObj.quartile || 'Standard'}`;

  const compEl = document.getElementById("stateComparisonText");
  const natRate = 21.4;
  const diff = Math.round((stateObj.combined - natRate) * 10) / 10;

  if (diff > 0) {
    compEl.textContent = `${stateObj.state} reports symptom frequency +${diff}% above the current national baseline (${natRate}%).`;
  } else if (diff < 0) {
    compEl.textContent = `${stateObj.state} reports symptom frequency ${Math.abs(diff)}% below the current national baseline (${natRate}%).`;
  } else {
    compEl.textContent = `${stateObj.state} closely matches the national baseline (${natRate}%).`;
  }
}

/* ==========================================================================
   4. PHQ-4 Self-Assessment Screener Controller
   ========================================================================== */

function initScreener() {
  const submitBtn = document.getElementById("submitScreenerBtn");
  const screenerResult = document.getElementById("screenerResult");
  const talkToAuraBtn = document.getElementById("talkToAuraBtn");

  submitBtn.addEventListener("click", async () => {
    const q1 = parseInt(document.querySelector('input[name="q1"]:checked')?.value || "0", 10);
    const q2 = parseInt(document.querySelector('input[name="q2"]:checked')?.value || "0", 10);
    const q3 = parseInt(document.querySelector('input[name="q3"]:checked')?.value || "0", 10);
    const q4 = parseInt(document.querySelector('input[name="q4"]:checked')?.value || "0", 10);

    try {
      const res = await fetch("/api/screen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          anxiety_q1: q1,
          anxiety_q2: q2,
          depression_q3: q3,
          depression_q4: q4,
        }),
      });

      if (!res.ok) throw new Error("Screening calculation error");

      const data = await res.json();
      displayScreenerResult(data);
    } catch (err) {
      console.error("Screening calculation error:", err);
    }
  });

  function displayScreenerResult(data) {
    screenerResult.style.display = "block";

    document.getElementById("resScore").textContent = `Total Score: ${data.total_score} / 12`;
    const severityBadge = document.getElementById("resSeverity");
    severityBadge.textContent = data.severity.toUpperCase();

    // Set Neo-brutalist badge color
    if (data.severity === "Minimal") {
      severityBadge.className = "neo-tag mint";
    } else if (data.severity === "Mild") {
      severityBadge.className = "neo-tag yellow";
    } else if (data.severity === "Moderate") {
      severityBadge.className = "neo-tag coral";
    } else {
      severityBadge.className = "neo-tag coral";
    }

    document.getElementById("resDesc").textContent = data.description;

    const sub = data.subscales;
    document.getElementById("resAnxietyScore").textContent = `${sub.anxiety_score} / 6`;
    document.getElementById("resAnxietyStatus").textContent = sub.anxiety_screen_positive
      ? "⚠️ Elevated anxiety indicators (>= 3)"
      : "Within typical baseline (< 3)";

    document.getElementById("resDepressionScore").textContent = `${sub.depression_score} / 6`;
    document.getElementById("resDepressionStatus").textContent = sub.depression_screen_positive
      ? "⚠️ Elevated depressive indicators (>= 3)"
      : "Within typical baseline (< 3)";

    if (data.population_benchmark) {
      document.getElementById("resPopRate").textContent = data.population_benchmark.national_reported_rate;
    }

    screenerResult.scrollIntoView({ behavior: "smooth" });
  }

  // Pre-fill conversation prompt when transitioning from screener to Aura
  talkToAuraBtn.addEventListener("click", () => {
    const scoreText = document.getElementById("resScore").textContent;
    const severityText = document.getElementById("resSeverity").textContent;
    const prompt = `I completed the PHQ-4 screener. My score was: ${scoreText} (${severityText}). Can you help me process this and share some supportive coping steps?`;

    switchToTab("tab-chat");
    const chatInput = document.getElementById("chatInput");
    const chatForm = document.getElementById("chatForm");
    if (chatInput && chatForm) {
      chatInput.value = prompt;
      chatForm.dispatchEvent(new Event("submit"));
    }
  });
}

/* ==========================================================================
   5. Utility Helpers
   ========================================================================== */

function getCurrentTimeStr() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
