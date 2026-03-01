"""
message_queue.py
────────────────
A simple in-process async message queue that lets Agent A and Agent B
communicate without tight coupling.

Each message has:
  - sender   : "agent_a" | "agent_b" | "user"
  - receiver : "agent_a" | "agent_b"
  - type     : a string label (e.g. "task", "result", "error")
  - payload  : arbitrary dict
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Message:
    """A single message exchanged between agents."""
    sender: str
    receiver: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)


class MessageQueue:
    """
    Async queue that routes messages between named agents.

    Usage:
        queue = MessageQueue()
        await queue.send(Message(sender="agent_a", receiver="agent_b", type="task", payload={...}))
        msg = await queue.receive("agent_b")
    """

    def __init__(self):
        # One asyncio.Queue per agent name
        self._queues: Dict[str, asyncio.Queue] = {}

    # ── helpers ────────────────────────────────────────────────────────

    def _ensure_queue(self, agent_name: str) -> asyncio.Queue:
        """Create the queue for *agent_name* if it doesn't exist yet."""
        if agent_name not in self._queues:
            self._queues[agent_name] = asyncio.Queue()
        return self._queues[agent_name]

    # ── public API ────────────────────────────────────────────────────

    async def send(self, message: Message) -> None:
        """Put a message into the receiver's inbox."""
        queue = self._ensure_queue(message.receiver)
        await queue.put(message)

    async def receive(self, agent_name: str, timeout: float = 30.0) -> Message:
        """
        Wait for the next message addressed to *agent_name*.
        Raises asyncio.TimeoutError if nothing arrives within *timeout* seconds.
        """
        queue = self._ensure_queue(agent_name)
        return await asyncio.wait_for(queue.get(), timeout=timeout)
