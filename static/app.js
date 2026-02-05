let lastRunId = null;
let pollInterval = null;

/* ------------------------------
   MODE 1: Prompt → Workflow
-------------------------------- */
async function generateWorkflow() {
  const prompt = document.getElementById("promptInput").value;
  if (!prompt) {
    alert("Please enter a prompt first.");
    return;
  }

  const workflowBox = document.getElementById("workflowJson");
  workflowBox.value = "Generating workflow using LLM...\nPlease wait.";

  try {
    const res = await fetch("/generate-workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const text = await res.text();
    let data;

    try {
      data = JSON.parse(text);
    } catch {
      workflowBox.value = "Invalid server response:\n\n" + text;
      return;
    }

    if (data.status !== "success") {
      workflowBox.value =
        "ERROR generating workflow:\n\n" +
        (data.message || "Unknown error") +
        (data.raw_output ? "\n\nLLM OUTPUT:\n" + data.raw_output : "");
      return;
    }

    workflowBox.value = JSON.stringify(data.workflow, null, 2);
  } catch (err) {
    workflowBox.value = "Network / server error while generating workflow.";
  }
}

/* ------------------------------
   MODE 2: Create Workflow
-------------------------------- */
async function createWorkflow() {
  const text = document.getElementById("workflowJson").value;
  if (!text) {
    alert("Workflow JSON is empty.");
    return;
  }

  let workflow;
  try {
    workflow = JSON.parse(text);   // ✅ CRITICAL FIX
  } catch (err) {
    alert("Workflow JSON is invalid:\n" + err.message);
    return;
  }

  try {
    const res = await fetch("/workflows", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(workflow)   // ✅ send JSON
    });

    const responseText = await res.text();
    let data;

    try {
      data = JSON.parse(responseText);
    } catch {
      alert("Server returned invalid JSON:\n\n" + responseText);
      return;
    }

    if (!res.ok) {
      alert("Backend error:\n\n" + JSON.stringify(data, null, 2));
      return;
    }

    if (!data.workflow_id) {
      alert("Failed to create workflow:\n\n" + JSON.stringify(data, null, 2));
      return;
    }

    document.getElementById("workflowId").value = data.workflow_id;
    alert("Workflow created successfully.");

  } catch (err) {
    alert("Network / server error while creating workflow.\n\n" + err.message);
  }
}

/* ------------------------------
   Run Workflow
-------------------------------- */
async function runWorkflow() {
  const workflowId = document.getElementById("workflowId").value;
  if (!workflowId) {
    alert("Workflow ID is missing.");
    return;
  }

  document.getElementById("stateText").textContent = "RUNNING";
  document.getElementById("stateText").className = "status running";
  document.getElementById("stateHint").textContent =
    "Workflow execution started...";
  document.getElementById("logs").innerHTML = "";
  document.getElementById("retryBtn").style.display = "none";

  try {
    const res = await fetch(`/workflows/${workflowId}/run`, {
      method: "POST"
    });

    const data = await res.json();

    if (!data.run_id) {
      alert("Failed to start workflow run:\n\n" + JSON.stringify(data, null, 2));
      return;
    }

    lastRunId = data.run_id;

    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => loadRun(lastRunId), 2000);

  } catch (err) {
    alert("Network / server error while running workflow.");
  }
}

/* ------------------------------
   Fetch Run State
-------------------------------- */
async function loadRun(runId) {
  try {
    const res = await fetch(`/runs/${runId}`);
    const run = await res.json();

    const stateText = document.getElementById("stateText");
    const stateHint = document.getElementById("stateHint");
    const logsEl = document.getElementById("logs");

    stateText.textContent = run.state || run.status;

    if (run.state === "COMPLETED") {
      stateText.className = "status success";
      stateHint.textContent = "Workflow completed successfully.";
      clearInterval(pollInterval);

    } else if (run.state === "WAITING_FOR_PROVIDER") {
      stateText.className = "status running";
      stateHint.textContent =
        "LLM provider temporarily unavailable.";
      document.getElementById("retryBtn").style.display = "inline-block";
      clearInterval(pollInterval);

    } else if (run.state === "FAILED_VALIDATION") {
      stateText.className = "status failed";
      stateHint.textContent =
        "LLM output did not meet completion criteria.";
      clearInterval(pollInterval);

    } else {
      stateText.className = "status running";
      stateHint.textContent =
        `Executing step ${run.current_step}, attempt ${run.current_attempt}`;
    }

    logsEl.innerHTML = "";
    (run.logs || []).forEach(log => {
      const div = document.createElement("div");
      div.className = "log";
      div.textContent =
        `Step ${log.step} (Attempt ${log.attempt})\n\n` +
        (log.output ? `OUTPUT:\n${log.output}\n\n` : "") +
        (log.error ? `ERROR:\n${log.error}` : "");
      logsEl.appendChild(div);
    });

  } catch (err) {
    console.error("Failed to load run state", err);
  }
}

/* ------------------------------
   Retry (placeholder)
-------------------------------- */
function retryRun() {
  alert("Retry support can be added next.");
}
