import time
from typing import List, Tuple
from timing_utils import TimingLogger
from memory_chroma import ChromaMem0Backend
import os
import json
from similarity_utils import get_similarity_func, AVAILABLE_ALGORITHMS
import argparse
# Add imports for other backends here as you implement them

QA_DATA_ROOT = os.path.join(os.path.dirname(__file__), '../qa_data')
ADD_SAMPLE_SIZE = 100  # Number of questions to add to memory
RETRIEVAL_SAMPLE_SIZE = 10  # Number of questions to use for retrieval/accuracy
DEFAULT_SIMILARITY = 'simple'


def load_qa_pairs(root_dir: str) -> List[Tuple[str, str]]:
    qa_pairs = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith('.jsonl'):
                fpath = os.path.join(dirpath, fname)
                with open(fpath, 'r') as f:
                    for line in f:
                        try:
                            obj = json.loads(line)
                            q = obj.get('question')
                            a = obj.get('answer')
                            if q and a:
                                qa_pairs.append((q, a))
                        except Exception:
                            continue
    return qa_pairs

class MemoryBenchmark:
    def __init__(self, backends: List, logger: TimingLogger, add_sample_size: int = 1000, retrieval_sample_size: int = 100, agent_id: str = "benchmark-agent", similarity: str = DEFAULT_SIMILARITY):
        self.backends = backends
        self.logger = logger
        self.agent_id = agent_id
        self.qa_pairs = load_qa_pairs(QA_DATA_ROOT)
        self.add_sample_size = min(add_sample_size, len(self.qa_pairs))
        self.retrieval_sample_size = min(retrieval_sample_size, len(self.qa_pairs))
        self.results = []  # To store summary info for each backend
        if similarity not in AVAILABLE_ALGORITHMS:
            raise ValueError(f"Similarity algorithm '{similarity}' is not available. Available: {AVAILABLE_ALGORITHMS}")
        self.similarity_name = similarity
        self.similarity_func = get_similarity_func(similarity)

    def run(self):
        print(f"Loaded {len(self.qa_pairs)} QA pairs from {QA_DATA_ROOT}")
        print(f"Using similarity algorithm: {self.similarity_name}")
        self.logger.log(f"Loaded {len(self.qa_pairs)} QA pairs from {QA_DATA_ROOT}")
        self.logger.log(f"Using similarity algorithm: {self.similarity_name}")
        for backend in self.backends:
            print(f"\n--- Benchmarking {backend.name} ---")
            self.logger.log(f"\n--- Benchmarking {backend.name} ---")
            add_times = []
            retrieve_times = []
            # Add a limited number of QA pairs
            for i, (user_msg, agent_resp) in enumerate(self.qa_pairs[:self.add_sample_size]):
                text = f"User: {user_msg}\nAgent: {agent_resp}"
                add_start = time.time()
                backend.add(text, agent_id=self.agent_id)
                add_time = time.time() - add_start
                add_times.append(add_time)
                self.logger.log_timing(f"{backend.name} store/update timing", add_time)
                self.logger.log_stored(f"{backend.name} memory stored", text)
                if (i + 1) % 10 == 0 or (i + 1) == self.add_sample_size:
                    print(f"  Added {i + 1}/{self.add_sample_size} items...")
            # Retrieval and accuracy check
            correct = 0
            total_similarity = 0.0
            for i, (user_msg, expected_answer) in enumerate(self.qa_pairs[:self.retrieval_sample_size]):
                query = user_msg
                retrieve_start = time.time()
                results = backend.search(query, agent_id=self.agent_id)
                retrieve_time = time.time() - retrieve_start
                retrieve_times.append(retrieve_time)
                self.logger.log_timing(f"{backend.name} retrieve time", retrieve_time)
                self.logger.log_memories(f"{backend.name} memory retrieved", results)
                # Accuracy: check if expected answer is similar to any retrieved memory's answer
                best_sim = 0.0
                for m in results:
                    mem_text = m['memory'] if isinstance(m, dict) and 'memory' in m else str(m)
                    # Try to extract the answer part
                    if 'Agent:' in mem_text:
                        mem_answer = mem_text.split('Agent:', 1)[-1].strip()
                    else:
                        mem_answer = mem_text
                    sim = self.similarity_func(expected_answer, mem_answer)
                    if sim > best_sim:
                        best_sim = sim
                total_similarity += best_sim
                if best_sim > 0.8:  # Consider correct if similarity > 0.8
                    correct += 1
                if (i + 1) % 10 == 0 or (i + 1) == self.retrieval_sample_size:
                    print(f"  Retrieved {i + 1}/{self.retrieval_sample_size} items...")
            accuracy = correct / self.retrieval_sample_size
            avg_similarity = total_similarity / self.retrieval_sample_size
            print(f"{backend.name} accuracy: {accuracy:.2%}, avg similarity: {avg_similarity:.2%}")
            self.logger.log(f"{backend.name} accuracy: {accuracy:.2%}, avg similarity: {avg_similarity:.2%}")
            self.logger.log(f"--- End of {backend.name} benchmark ---\n")
            print(f"--- End of {backend.name} benchmark ---\n")
            # Store summary
            self.results.append({
                'name': backend.name,
                'avg_add_time': sum(add_times) / len(add_times),
                'avg_retrieve_time': sum(retrieve_times) / len(retrieve_times),
                'accuracy': accuracy,
                'avg_similarity': avg_similarity,
                'num_added': self.add_sample_size,
                'num_retrieved': self.retrieval_sample_size,
                'similarity': self.similarity_name
            })
        self.print_summary()

    def print_summary(self):
        summary_lines = []
        summary_lines.append("\n===== BENCHMARK SUMMARY =====")
        summary_lines.append(f"Similarity: {self.similarity_name}")
        summary_lines.append(f"{'Backend':<20} {'#Added':<8} {'#Tested':<8} {'Avg Add Time (s)':<18} {'Avg Retrieve Time (s)':<22} {'Accuracy':<10} {'AvgSim':<10}")
        summary_lines.append("-" * 90)
        for result in self.results:
            summary_lines.append(f"{result['name']:<20} {result['num_added']:<8} {result['num_retrieved']:<8} {result['avg_add_time']:<18.6f} {result['avg_retrieve_time']:<22.6f} {result['accuracy']:<10.2%} {result['avg_similarity']:<10.2%}")
        summary_lines.append("============================\n")
        # Print to screen
        for line in summary_lines:
            print(line)
        # Log to file
        for line in summary_lines:
            self.logger.log(line)

def main():
    parser = argparse.ArgumentParser(description="Memory Benchmark Script")
    parser.add_argument('--similarity', type=str, default=DEFAULT_SIMILARITY, help=f"Similarity algorithm to use. Available: {AVAILABLE_ALGORITHMS}")
    args = parser.parse_args()
    similarity = args.similarity
    if similarity not in AVAILABLE_ALGORITHMS:
        print(f"Error: Similarity algorithm '{similarity}' is not available. Available: {AVAILABLE_ALGORITHMS}")
        return
    logger = TimingLogger('timing_benchmark.log')
    backends = [ChromaMem0Backend()]  # Add more as you implement them
    benchmark = MemoryBenchmark(backends, logger, add_sample_size=ADD_SAMPLE_SIZE, retrieval_sample_size=RETRIEVAL_SAMPLE_SIZE, similarity=similarity)
    benchmark.run()

if __name__ == '__main__':
    main() 