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
        self.results = []  # To store summary info for each backend

    def run(self):
        for backend in self.backends:
            print(f"\n--- Benchmarking {backend.name} ---")
            self.logger.log(f"\n--- Benchmarking {backend.name} ---")
            add_times = []
            retrieve_times = []
            # Add all test data
            for i, (user_msg, agent_resp) in enumerate(TEST_DATA[:self.num_iterations]):
                text = f"User: {user_msg}\nAgent: {agent_resp}"
                add_start = time.time()
                backend.add(text, agent_id=self.agent_id)
                add_time = time.time() - add_start
                add_times.append(add_time)
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
                retrieve_times.append(retrieve_time)
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
            # Store summary
            self.results.append({
                'name': backend.name,
                'avg_add_time': sum(add_times) / len(add_times),
                'avg_retrieve_time': sum(retrieve_times) / len(retrieve_times),
                'accuracy': accuracy
            })
        self.print_summary()

    def print_summary(self):
        summary_lines = []
        summary_lines.append("\n===== BENCHMARK SUMMARY =====")
        summary_lines.append(f"{'Backend':<20} {'Avg Add Time (s)':<18} {'Avg Retrieve Time (s)':<22} {'Accuracy':<10}")
        summary_lines.append("-" * 70)
        for result in self.results:
            summary_lines.append(f"{result['name']:<20} {result['avg_add_time']:<18.6f} {result['avg_retrieve_time']:<22.6f} {result['accuracy']:<10.2%}")
        summary_lines.append("============================\n")
        # Print to screen
        for line in summary_lines:
            print(line)
        # Log to file
        for line in summary_lines:
            self.logger.log(line)

def main():
    logger = TimingLogger('timing_benchmark.log')
    backends = [ChromaMem0Backend()]  # Add more as you implement them
    benchmark = MemoryBenchmark(backends, logger, num_iterations=100)
    benchmark.run()

if __name__ == '__main__':
    main() 