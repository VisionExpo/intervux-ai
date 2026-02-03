import io
import contextlib
import threading
from typing import Tuple


class CodeExecutionTimeout(Exception):
    pass


class CodeExecutor:
    """
    Executes user-submitted Python code in a restricted environment.
    NOTE: This is NOT a full sandbox. Docker isolation is required for production.
    """

    # Allowed safe builtins
    SAFE_BUILTINS = {
        "print": print,
        "range": range,
        "len": len,
        "int": int,
        "float": float,
        "str": str,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "enumerate": enumerate,
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
    }

    @staticmethod
    def run_code(
        code_snippet: str,
        timeout_sec: int = 2
    ) -> Tuple[str, str]:
        """
        Executes Python code safely with timeout.
        Returns: (stdout, error)
        """

        output_buffer = io.StringIO()
        error_message = None

        def target():
            nonlocal error_message
            try:
                exec_globals = {
                    "__builtins__": CodeExecutor.SAFE_BUILTINS
                }

                with contextlib.redirect_stdout(output_buffer):
                    exec(code_snippet, exec_globals)

            except Exception as e:
                error_message = f"❌ Runtime Error: {e}"

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=timeout_sec)

        if thread.is_alive():
            error_message = "⏱️ Execution timed out."
            return "", error_message

        return output_buffer.getvalue(), error_message
