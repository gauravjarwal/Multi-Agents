"""
agent_b.py  –  The Executor Agent
──────────────────────────────────
Agent B receives individual sub-tasks from Agent A and executes them
using Gemini (with Google Search grounding enabled so it can fetch
real-time information like weather, news, sports scores, etc.).

If a sub-task depends on earlier results, the caller passes them in
via the 'context' field so Agent B has the information it needs.
"""

from google import genai
from google.genai import types

from config import GEMINI_API_KEY

# ── Gemini client ─────────────────────────────────────────────────────
client = genai.Client(api_key=GEMINI_API_KEY)

# ── Google Search tool — lets Gemini fetch real-time data ─────────────
google_search_tool = types.Tool(google_search=types.GoogleSearch())


class AgentB:
    """Executor agent – uses Gemini (with Google Search) to carry out any sub-task."""

    NAME = "agent_b"

    # ── public API ────────────────────────────────────────────────────

    def execute_task(self, task: dict) -> dict:
        """
        Execute a single sub-task using Gemini.

        Parameters
        ----------
        task : dict
            Must contain:
              - "description" : str   (what to do)
            May contain:
              - "context"     : str   (results from earlier tasks)
              - "depends_on"  : list  (task IDs this depends on)

        Returns
        -------
        dict  with either  {"result": str}  or  {"error": str}
        """
        description = task.get("description", "")
        context = task.get("context", "")

        if not description:
            return {"error": "Task has no description."}

        # Build the prompt
        prompt = self._build_prompt(description, context)

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[google_search_tool],
                ),
            )
            result = response.text.strip()
            return {"result": result}
        except Exception as exc:
            return {"error": f"Gemini execution failed: {exc}"}

    # ── private helpers ───────────────────────────────────────────────

    def _build_prompt(self, description: str, context: str) -> str:
        """
        Construct a clear prompt for Gemini to execute the sub-task.
        """
        parts = [
            "You are an AI executor agent. Answer or complete the task below "
            "accurately and concisely. Give a direct plain-text answer.\n",
        ]

        if context:
            parts.append(f"Context from previous steps:\n{context}\n")

        parts.append(f"Task:\n{description}")

        return "\n".join(parts)
