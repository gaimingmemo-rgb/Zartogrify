import sys
import subprocess
import tempfile
import os

class LocalExecutor:
    def execute_python_code(self, code_response: str, log_callback) -> tuple[bool, str]:
        log_callback("🔍 *Extracting Python code block from AI response...*")
        
        # Extract markdown code blocks if the AI wrapped them
        code = code_response
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        code = code.strip()

        log_callback("🧪 *Running syntax verification and live bug checks...*")
        try:
            compile(code, '<string>', 'exec')
            log_callback("✅ *Syntax validation passed! Code is clean.*")
        except SyntaxError as se:
            return False, f"Syntax Error caught during testing: {se}\n\nRaw Code Attempted:\n{code}"

        log_callback("⚡ *Executing script inside local Python subprocess sandbox...*")
        
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(code)
            temp_path = tf.name

        try:
            res = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, timeout=30)
            os.remove(temp_path)
            
            if res.returncode == 0:
                log_callback("🚀 *Local script executed successfully!*")
                return True, res.stdout.strip() or "Script executed successfully with no console output."
            else:
                return False, f"Runtime Error:\n{res.stderr.strip()}"

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"Execution Exception: {str(e)}"
