import time
from typing import List, Dict, Any

from app.llm_router import LLMRouter
from app.unbound_client import call_unbound
from app.completion import check_completion


llm_router = LLMRouter(
    providers=[call_unbound]
)


def run_workflow(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    context = ""
    logs = []

    for index, step in enumerate(steps, start=1):
        retries = 0
        step_success = False

        while retries <= step["max_retries"]:
            time.sleep(2)  # IMPORTANT: Unbound pacing

            prompt = (
                step["prompt"]
                + "\n\nPrevious step output:\n"
                + context
            )

            # ---- Provider call ----
            try:
                output = llm_router.call(step["model"], prompt)

            except Exception as e:
                logs.append({
                    "step": index,
                    "attempt": retries + 1,
                    "error_type": "provider_unavailable",
                    "error": str(e)
                })
                retries += 1
                continue

            # ---- Deterministic validation ----
            passed = check_completion(
                output=output,
                criteria_type=step["criteria_type"],
                criteria_value=step.get("criteria_value")
            )

            logs.append({
                "step": index,
                "attempt": retries + 1,
                "output": output,
                "passed": passed
            })

            if passed:
                context = output
                step_success = True
                break

            retries += 1

        if not step_success:
            return {
                "status": "FAILED_PROVIDER" if any(
                    l.get("error_type") == "provider_unavailable"
                    for l in logs
                ) else "FAILED_OUTPUT",
                "failed_step": index,
                "retryable": True,
                "logs": logs
            }

    return {
        "status": "COMPLETED",
        "logs": logs
    }
