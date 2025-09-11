"""
A simplified skeleton for a multi-agent system architecture. 
It demonstrates how an orchestrator assigns tasks to agents based on roles, using 
a simple in-memory message queue. This is a starting point for implementing the 
state-of-the-art architecture described earlier.

Note: This is a prototype; actual production systems should use robust 
message brokers (e.g., Kafka or RabbitMQ), persistent storage, and proper 
error handling.
"""
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List

# Define a simple Task dataclass
@dataclass
class Task:
    id: int
    description: str
    domain: str  # e.g., 'architecture', 'algorithm', 'context', 'scalability'

# Define the Agent class
class Agent(threading.Thread):
    def __init__(self, name: str, domains: List[str], task_queue: queue.Queue):
        super().__init__(daemon=True)
        self.name = name
        self.domains = set(domains)
        self.task_queue = task_queue
        self.processed: List[int] = []

    def run(self):
        while True:
            try:
                task: Task = self.task_queue.get(timeout=1)
                self.process(task)
                self.task_queue.task_done()
            except queue.Empty:
                # No task available, continue
                continue

    def can_handle(self, domain: str) -> bool:
        return domain in self.domains

    def process(self, task: Task):
        # Simulate processing
        print(f"[Agent {self.name}] processing task {task.id}: {task.description}")
        time.sleep(0.1)  # simulate work
        self.processed.append(task.id)

# Orchestrator class to route tasks
class Orchestrator:
    def __init__(self):
        self.agents: List[Agent] = []
        self.queues: Dict[str, queue.Queue] = {}
        self.task_counter = 0

    def register_agent(self, agent: Agent):
        self.agents.append(agent)
        for domain in agent.domains:
            if domain not in self.queues:
                self.queues[domain] = queue.Queue()

    def start(self):
        # Start all agents
        for agent in self.agents:
            agent.start()

    def submit_task(self, description: str, domain: str):
        self.task_counter += 1
        task = Task(id=self.task_counter, description=description, domain=domain)
        # Route task to appropriate queue
        if domain in self.queues:
            self.queues[domain].put(task)
        else:
            print(f"[Orchestrator] No agent available for domain '{domain}'. Task {task.id} discarded.")

    def run_dispatcher(self):
        """Continuously dispatch tasks from queues to eligible agents."""
        while True:
            for domain, q in self.queues.items():
                if q.empty():
                    continue
                # Find first available agent that can handle this domain
                for agent in self.agents:
                    if agent.can_handle(domain):
                        try:
                            task = q.get_nowait()
                            agent.task_queue.put(task)
                        except queue.Empty:
                            pass
                        break
            time.sleep(0.05)


def main():
    # Create orchestrator
    orchestrator = Orchestrator()

    # Define agents with their domains (niches)
    architecture_agent = Agent("Claude", ["architecture", "resilience"], queue.Queue())
    algorithm_agent = Agent("DeepSeek", ["algorithm", "complexity"], queue.Queue())
    context_agent = Agent("Gemini", ["context", "interoperability"], queue.Queue())
    scalability_agent = Agent("GPT5Max", ["scalability", "performance"], queue.Queue())

    # Register agents
    orchestrator.register_agent(architecture_agent)
    orchestrator.register_agent(algorithm_agent)
    orchestrator.register_agent(context_agent)
    orchestrator.register_agent(scalability_agent)

    # Start agents
    orchestrator.start()

    # Start dispatcher in a separate thread
    dispatcher_thread = threading.Thread(target=orchestrator.run_dispatcher, daemon=True)
    dispatcher_thread.start()

    # Submit some sample tasks
    tasks = [
        ("Design high-availability architecture", "architecture"),
        ("Optimise sorting algorithm", "algorithm"),
        ("Analyse API context interoperability", "context"),
        ("Scale up distributed system", "scalability"),
        ("Evaluate resilience patterns", "resilience"),
        ("Benchmark algorithmic complexity", "complexity"),
        ("Handle unknown domain task", "unknown"),
    ]

    for desc, domain in tasks:
        orchestrator.submit_task(desc, domain)

    # Allow some time for processing
    time.sleep(2)

    # Summary
    for agent in orchestrator.agents:
        print(f"Agent {agent.name} processed tasks: {agent.processed}")

if __name__ == "__main__":
    main()
