import os
import time

class TimingLogger:
    def __init__(self, log_filename='timing.log'):
        self.timing_log_path = os.path.join(os.path.dirname(__file__), f'../{log_filename}')
        self._log_session_start()

    def log(self, message: str):
        with open(self.timing_log_path, 'a') as f:
            f.write(message + '\n')

    def _log_session_start(self):
        if not os.path.exists(self.timing_log_path) or os.path.getsize(self.timing_log_path) == 0:
            self.log('--- Starting session ---')

    def log_timing(self, label: str, duration: float, exception: bool = False):
        suffix = ' (EXCEPTION)' if exception else ''
        self.log(f"{label}: {duration:.4f} seconds{suffix}")

    def log_memories(self, label: str, memories):
        self.log(f"{label}: {memories}")

    def log_stored(self, label: str, content, exception: Exception = None):
        if exception:
            self.log(f"{label}: [ERROR] {str(exception)}")
        else:
            self.log(f"{label}: {content}") 