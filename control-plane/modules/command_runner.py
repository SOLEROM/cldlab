"""
Async command execution — runs shell commands in a thread, logs output.
"""
import os
import subprocess
import threading
import time
import logging

logger = logging.getLogger('command_runner')


class CommandResult:
    def __init__(self, returncode, stdout, stderr, elapsed):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.elapsed = elapsed
        self.success = returncode == 0

    def to_dict(self):
        return {
            'returncode': self.returncode,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'elapsed': round(self.elapsed, 2),
            'success': self.success,
        }


def run_sync(cmd, cwd=None, timeout=60, env=None):
    """Run command synchronously, return CommandResult."""
    t0 = time.time()
    merged_env = {**os.environ, **(env or {})}
    try:
        result = subprocess.run(
            cmd, shell=isinstance(cmd, str),
            cwd=cwd, capture_output=True, text=True,
            timeout=timeout, env=merged_env
        )
        return CommandResult(result.returncode, result.stdout, result.stderr, time.time() - t0)
    except subprocess.TimeoutExpired:
        return CommandResult(1, '', 'Command timed out', time.time() - t0)
    except Exception as e:
        return CommandResult(1, '', str(e), time.time() - t0)


def run_async(cmd, cwd=None, timeout=60, callback=None, env=None):
    """Run command in a background thread, call callback(result) when done."""
    def worker():
        result = run_sync(cmd, cwd=cwd, timeout=timeout, env=env)
        logger.info(f"cmd={cmd!r} rc={result.returncode} elapsed={result.elapsed:.2f}s")
        if callback:
            callback(result)
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t
