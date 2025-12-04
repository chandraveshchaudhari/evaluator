import threading, traceback

class ComparisonService:
    def run_assertions(self, student_namespace, assertions, question_name=None, timeout=3):
        results = []

        def safe_exec(code, globals_ns, result_container):
            try:
                exec(code, globals_ns)
                result_container.append(("passed", None))
            except Exception:
                result_container.append(("failed", traceback.format_exc()))

        for code in assertions:
            result = []
            t = threading.Thread(target=safe_exec, args=(code, student_namespace, result))
            t.daemon = True
            t.start()
            t.join(timeout)  # seconds

            if t.is_alive():
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "error": f"TimeoutError: Code exceeded {timeout}s limit (possible infinite loop)",
                    "score": 0
                })
                continue

            status, err = result[0] if result else ("failed", "Unknown execution failure")
            results.append({
                "question": question_name,
                "assertion": code,
                "status": status,
                "error": err,
                "score": 1 if status == "passed" else 0
            })

        return results
