from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import json

from app.unbound_client import call_unbound
from app.executor import run_workflow
from app.schemas import WorkflowCreateSchema

from app.database import Base, engine, SessionLocal
from app.models import Workflow, Step, Run, RunLog


# =================================================
# App initialization
# =================================================

app = FastAPI(title="Agentic Workflow Builder")

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

Base.metadata.create_all(bind=engine)


# =================================================
# Sanity check
# =================================================

@app.get("/test-unbound")
def test_unbound():
    output = call_unbound(
        model="kimi-k2-instruct-0905",
        prompt="Say SUCCESS only"
    )
    return {"output": output}


# =================================================
# Prompt → Workflow (LLM-safe, 2-stage)
# =================================================

@app.post("/generate-workflow")
def generate_workflow_from_prompt(data: dict = Body(...)):
    user_prompt = data.get("prompt")
    if not user_prompt:
        return {"status": "error", "message": "Prompt is required"}

    llm_prompt = f"""
Break the following request into clear numbered steps.

Rules:
- One task per step
- Numbered list
- Plain text only
- No explanations

User request:
{user_prompt}
"""

    try:
        steps_text = call_unbound(
            model="kimi-k2-instruct-0905",
            prompt=llm_prompt
        )

        print("RAW STEP PLAN:\n", steps_text)

        steps = []

        for line in steps_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit():
                step_prompt = line.split(".", 1)[-1].strip()
                if step_prompt:
                    steps.append({
                        "model": "kimi-k2-instruct-0905",
                        "prompt": step_prompt,
                        "criteria_type": "length",
                        "criteria_value": {"min": 50},
                        "max_retries": 2
                    })

        if not steps:
            raise ValueError("LLM did not generate steps")

        workflow = {
            "name": "Generated Workflow",
            "steps": steps
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to generate workflow",
            "error": str(e),
            "raw_output": steps_text if "steps_text" in locals() else None
        }

    return {
        "status": "success",
        "workflow": workflow
    }


# =================================================
# Workflow CRUD
# =================================================

@app.post("/workflows")
def create_workflow(workflow: WorkflowCreateSchema):
    db = SessionLocal()
    workflow_id = str(uuid4())

    db_workflow = Workflow(id=workflow_id, name=workflow.name)
    db.add(db_workflow)

    for step in workflow.steps:
        db.add(
            Step(
                workflow_id=workflow_id,
                model=step.model,
                prompt=step.prompt,
                criteria_type=step.criteria_type,
                # 🔑 FIX: JSON-encode criteria_value
                criteria_value=json.dumps(step.criteria_value)
                if step.criteria_value is not None
                else None,
                max_retries=step.max_retries
            )
        )

    db.commit()
    db.close()

    return {"workflow_id": workflow_id}


# =================================================
# Run workflow
# =================================================

@app.post("/workflows/{workflow_id}/run")
def run_workflow_by_id(workflow_id: str):
    db = SessionLocal()

    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        db.close()
        return {"status": "error", "message": "Workflow not found"}

    steps = [
        {
            "model": s.model,
            "prompt": s.prompt,
            "criteria_type": s.criteria_type,
            # 🔑 FIX: JSON-decode criteria_value
            "criteria_value": json.loads(s.criteria_value)
            if s.criteria_value is not None
            else None,
            "max_retries": s.max_retries
        }
        for s in workflow.steps
    ]

    run_id = str(uuid4())
    result = run_workflow(steps)

    db_run = Run(
        id=run_id,
        workflow_id=workflow_id,
        status=result["status"]
    )
    db.add(db_run)

    for log in result["logs"]:
        db.add(
            RunLog(
                run_id=run_id,
                step=log["step"],
                attempt=log["attempt"],
                passed=(
                    1 if log.get("passed") is True
                    else 0 if log.get("passed") is False
                    else None
                ),
                output=log.get("output"),
                error_type=log.get("error_type"),
                error=log.get("error")
            )
        )

    db.commit()
    db.close()

    return {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "status": result["status"]
    }


# =================================================
# Run state + logs (UI polling)
# =================================================

@app.get("/runs/{run_id}")
def get_run(run_id: str):
    db = SessionLocal()

    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        db.close()
        return {"status": "error", "message": "Run not found"}

    logs = db.query(RunLog).filter(RunLog.run_id == run_id).all()
    db.close()

    state = run.status
    current_step = None
    current_attempt = None

    if logs:
        last = logs[-1]
        current_step = last.step
        current_attempt = last.attempt

        if run.status == "COMPLETED":
            state = "COMPLETED"
        elif run.status == "FAILED_PROVIDER":
            state = "WAITING_FOR_PROVIDER"
        elif run.status == "FAILED_OUTPUT":
            state = "FAILED_VALIDATION"
        else:
            state = "RUNNING"

    return {
        "run_id": run.id,
        "workflow_id": run.workflow_id,
        "status": run.status,
        "state": state,
        "current_step": current_step,
        "current_attempt": current_attempt,
        "retryable": run.status == "FAILED_PROVIDER",
        "logs": [
            {
                "step": l.step,
                "attempt": l.attempt,
                "passed": l.passed,
                "output": l.output,
                "error_type": l.error_type,
                "error": l.error
            }
            for l in logs
        ]
    }


@app.get("/runs")
def list_runs():
    db = SessionLocal()
    runs = db.query(Run).all()
    db.close()

    return [
        {
            "run_id": r.id,
            "workflow_id": r.workflow_id,
            "status": r.status
        }
        for r in runs
    ]
