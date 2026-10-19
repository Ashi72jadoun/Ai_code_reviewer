import subprocess
import os

def run_ruff(repo_path):
    """
    Runs the Ruff linter on the target repository to find code quality issues.
    """
    if not os.path.exists(repo_path):
        return f"Error: Path '{repo_path}' does not exist."
        
    try:
        # check=False is used because linters return a non-zero exit code when they find issues.
        # We want to capture that output, not crash our Python script.
        result = subprocess.run(
            ["ruff", "check", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return "✅ Ruff: No styling or linting issues found."
        else:
            return f"❌ Ruff found issues:\n{result.stdout}"
            
    except FileNotFoundError:
        return "Error: Ruff is not installed or not in PATH."

def run_bandit(repo_path):
    """
    Runs the Bandit security scanner to find security vulnerabilities.
    """
    try:
        # The '-r' flag tells bandit to scan recursively through the folder.
        # The '-ll' flag filters only medium and high severity issues (optional, we use basic -r here).
        result = subprocess.run(
            ["bandit", "-r", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return "✅ Bandit: No security issues found."
        else:
            return f"❌ Bandit found security risks:\n{result.stdout}"
            
    except FileNotFoundError:
        return "Error: Bandit is not installed or not in PATH."

# Testing the tools
if __name__ == "__main__":
    target_directory = "../sample-target-repo"
    
    print(f"🔍 Running Static Analysis on: {target_directory}\n")
    
    print(run_ruff(target_directory))
    print("-" * 40)
    print(run_bandit(target_directory))
    print("-" * 40)