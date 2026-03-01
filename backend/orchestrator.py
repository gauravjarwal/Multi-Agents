"""
orchestrator.py
───────────────
Async orchestrator that wires Agent A and Agent B together through the
MessageQueue — satisfying the "asynchronous communication" bonus.

This module is used by app.py for the async endpoint.
"""

import asyncio
from message_queue import Message, MessageQueue
from agent_a import AgentA
from agent_b import AgentB


class Orchestrator:
    """
    Coordinates the full request lifecycle using async message passing.

    Flow:
      1. User request → Agent A decomposes into sub-tasks.
      2. Each sub-task is sent as a Message to Agent B's queue.
      3. Agent B processes messages and posts results back.
      4. Agent A reads the results and compiles the final answer.
    """

    def __init__(self):
        self.queue = MessageQueue()
        self.agent_a = AgentA()
        self.agent_b = AgentB()

    async def handle_request(self, user_input: str) -> dict:
        """
        Process *user_input* end-to-end using async message passing.
        Returns the same shape as AgentA.process_request().
        """
        # 1. Decompose
        tasks = self.agent_a._decompose(user_input)

        # 2. Process tasks sequentially (respecting dependencies)
        results_by_id = {}
        steps = []

        for task in tasks:
            # Resolve dependencies — inject context from earlier results
            depends_on = task.get("depends_on", [])
            context_parts = [
                f"[{dep_id}]: {results_by_id[dep_id]}"
                for dep_id in depends_on
                if dep_id in results_by_id
            ]
            if context_parts:
                task["context"] = "\n".join(context_parts)

            # Send task to Agent B via the queue
            msg = Message(
                sender=AgentA.NAME,
                receiver=AgentB.NAME,
                type="task",
                payload=task,
            )
            await self.queue.send(msg)

            # Agent B picks up the message and processes it
            incoming = await self.queue.receive(AgentB.NAME)
            result = self.agent_b.execute_task(incoming.payload)

            # Agent B sends the result back to Agent A
            reply = Message(
                sender=AgentB.NAME,
                receiver=AgentA.NAME,
                type="result",
                payload={**incoming.payload, **result},
            )
            await self.queue.send(reply)

            # Agent A collects the reply
            reply_msg = await self.queue.receive(AgentA.NAME)
            steps.append({"task": incoming.payload, **result})

            # Store result for downstream dependencies
            task_id = task.get("task_id", "")
            if "result" in result:
                results_by_id[task_id] = result["result"]
            else:
                results_by_id[task_id] = f"ERROR: {result.get('error', 'unknown')}"

        # 3. Compile final answer
        final_answer = self.agent_a._compile(user_input, steps)

        return {"steps": steps, "final_answer": final_answer}
