import time
from typing import List
from timing_utils import TimingLogger
from memory_chroma import ChromaMem0Backend
# Add imports for other backends here as you implement them

TEST_DATA = [
    (f"Test message {i}", f"Agent response {i}") for i in range(100)
]

class MemoryBenchmark:
    def __init__(self, backends: List, logger: TimingLogger, num_iterations: int = 100, agent_id: str = "benchmark-agent"):
        self.backends = backends
        self.logger = logger
        self.num_iterations = num_iterations
        self.agent_id = agent_id

    def run(self):
        for backend in self.backends:
            print(f"\n--- Benchmarking {backend.name} ---")
            self.logger.log(f"\n--- Benchmarking {backend.name} ---")
            # Add all test data
            for i, (user_msg, agent_resp) in enumerate(TEST_DATA[:self.num_iterations]):
                text = f"User: {user_msg}\nAgent: {agent_resp}"
                add_start = time.time()
                backend.add(text, agent_id=self.agent_id)
                add_time = time.time() - add_start
                self.logger.log_timing(f"{backend.name} store/update timing", add_time)
                self.logger.log_stored(f"{backend.name} memory stored", text)
                if (i + 1) % 10 == 0 or (i + 1) == self.num_iterations:
                    print(f"  Added {i + 1}/{self.num_iterations} items...")
            # Retrieval and accuracy check
            correct = 0
            for i, (user_msg, agent_resp) in enumerate(TEST_DATA[:self.num_iterations]):
                query = user_msg
                expected = agent_resp
                retrieve_start = time.time()
                results = backend.search(query, agent_id=self.agent_id)
                retrieve_time = time.time() - retrieve_start
                self.logger.log_timing(f"{backend.name} retrieve time", retrieve_time)
                self.logger.log_memories(f"{backend.name} memory retrieved", results)
                # Accuracy: check if expected response is in any retrieved memory
                found = any(expected in (m['memory'] if isinstance(m, dict) and 'memory' in m else str(m)) for m in results)
                if found:
                    correct += 1
                if (i + 1) % 10 == 0 or (i + 1) == self.num_iterations:
                    print(f"  Retrieved {i + 1}/{self.num_iterations} items...")
            accuracy = correct / self.num_iterations
            print(f"{backend.name} accuracy: {accuracy:.2%}")
            self.logger.log(f"{backend.name} accuracy: {accuracy:.2%}")
            self.logger.log(f"--- End of {backend.name} benchmark ---\n")
            print(f"--- End of {backend.name} benchmark ---\n")

def main():
    logger = TimingLogger('timing_benchmark.log')
    backends = [ChromaMem0Backend()]  # Add more as you implement them
    benchmark = MemoryBenchmark(backends, logger, num_iterations=100)
    benchmark.run()

if __name__ == '__main__':
    main() 