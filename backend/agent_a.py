"""
agent_a.py  –  The Orchestrator Agent
──────────────────────────────────────
Agent A is the "brain":
  1. Receives a free-form user request.
  2. Uses Gemini to decompose it into smaller sub-tasks.
  3. Sends each sub-task to Agent B for execution.
  4. Collects the results and uses Gemini to compile a final answer.

No task types are hardcoded — Gemini decides how to split any query.
"""

import json
import re
from typing import List

from google import genai
from google.genai import types

from config import GEMINI_API_KEY
from agent_b import AgentB

# ── Gemini client ─────────────────────────────────────────────────────
client = genai.Client(api_key=GEMINI_API_KEY)


class AgentA:
    """Orchestrator agent – decomposes requests, delegates, and compiles."""

    NAME = "agent_a"

    def __init__(self):
        self.agent_b = AgentB()

    # ──────────────────────────────────────────────────────────────────
    #  PUBLIC  –  end-to-end processing
    # ──────────────────────────────────────────────────────────────────

    def process_request(self, user_input: str) -> dict:
        """
        Full pipeline: decompose → delegate (with dependency resolution) → compile.

        Returns
        -------
        dict  {"steps": [...], "final_answer": str}
        """
        # Step 1 – break the request into sub-tasks via Gemini
        tasks = self._decompose(user_input)

        # Step 2 – execute tasks in order, injecting context for dependencies
        results_by_id = {}  # task_id → result string
        steps = []

        for task in tasks:
            # Resolve dependencies: gather results from tasks this one depends on
            depends_on = task.get("depends_on", [])
            context_parts = [
                f"[{dep_id}]: {results_by_id[dep_id]}"
                for dep_id in depends_on
                if dep_id in results_by_id
            ]
            if context_parts:
                task["context"] = "\n".join(context_parts)

            # Delegate to Agent B
            result = self.agent_b.execute_task(task)
            steps.append({"task": task, **result})

            # Store result for downstream dependencies
            task_id = task.get("task_id", "")
            if "result" in result:
                results_by_id[task_id] = result["result"]
            else:
                results_by_id[task_id] = f"ERROR: {result.get('error', 'unknown')}"

        # Step 3 – compile a final human-readable answer using Gemini
        final_answer = self._compile(user_input, steps)

        return {"steps": steps, "final_answer": final_answer}

    # ──────────────────────────────────────────────────────────────────
    #  PRIVATE  –  decompose via Gemini
    # ──────────────────────────────────────────────────────────────────

    def _decompose(self, user_input: str) -> List[dict]:
        """
        Use Gemini to break any user request into sub-tasks.
        Returns a list of dicts, each with:
          - "task_id"     : a short identifier (e.g. "task_1")
          - "description" : what this sub-task should accomplish
          - "depends_on"  : list of task_ids this depends on (empty if none)
        """
        prompt = (
            "You are a task-decomposition engine for a multi-agent AI system.\n"
            "Given the user request below, break it into the smallest logical sub-tasks.\n\n"
            "Rules:\n"
            "• Each sub-task must be self-contained and clearly actionable.\n"
            "• If a later task needs output from an earlier one, list the dependency in 'depends_on'.\n"
            "• Output ONLY a valid JSON array — no markdown fences, no extra text.\n"
            "• Each element must have exactly these keys:\n"
            '    "task_id"     : string (e.g. "task_1", "task_2")\n'
            '    "description" : string (clear instruction for the executor)\n'
            '    "depends_on"  : array of task_id strings (empty [] if independent)\n\n'
            "• If the request is already simple (single action), return an array with one task.\n\n"
            f"User request:\n{user_input}"
        )

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            raw = response.text.strip()

            # Strip markdown code fences if the model wraps them
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            tasks = json.loads(raw)

            # Validate structure
            if isinstance(tasks, list) and all(
                "task_id" in t and "description" in t for t in tasks
            ):
                # Ensure depends_on exists on every task
                for t in tasks:
                    t.setdefault("depends_on", [])
                return tasks

        except Exception as exc:
            print(f"[AgentA] Gemini decomposition failed: {exc}")

        # Minimal fallback — treat the whole request as a single task
        return [{
            "task_id": "task_1",
            "description": user_input,
            "depends_on": [],
        }]

    # ──────────────────────────────────────────────────────────────────
    #  PRIVATE  –  compile final answer via Gemini
    # ──────────────────────────────────────────────────────────────────

    def _compile(self, user_input: str, steps: List[dict]) -> str:
        """
        Use Gemini to weave all step results into a coherent final answer.
        """
        # Build a readable summary of what each step produced
        step_summaries = []
        for i, step in enumerate(steps, 1):
            desc = step["task"].get("description", "")
            if "error" in step:
                step_summaries.append(f"Step {i} ({desc}): ERROR – {step['error']}")
            else:
                step_summaries.append(f"Step {i} ({desc}): {step['result']}")

        steps_text = "\n".join(step_summaries)

        prompt = (
            "You are a helpful assistant compiling a final answer for the user.\n\n"
            f"Original user request:\n{user_input}\n\n"
            f"Sub-task results:\n{steps_text}\n\n"
            "Using the results above, write a clear, well-formatted answer to "
            "the user's original request. Be concise but complete. "
            "If any step had an error, acknowledge it gracefully.\n\n"
            "IMPORTANT: Respond with a direct plain-text answer ONLY. "
            "DO NOT output any code, tool calls, or API requests."
        )

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as exc:
            print(f"[AgentA] Gemini compile failed: {exc}")
            # Fallback: just concatenate the step results
            return steps_text
