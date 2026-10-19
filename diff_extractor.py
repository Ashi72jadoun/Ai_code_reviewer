import subprocess
import os

def get_git_diff(repo_path):
    """
    Runs the 'git diff' command in the target repository
    and returns the output as a string.
    """
    # First, check if the specified directory exists
    if not os.path.exists(repo_path):
        return f"Error: The path '{repo_path}' does not exist."
        
    try:
        # Using subprocess to run terminal commands directly from Python
        result = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,          # The directory where the command should run
            capture_output=True,    # Capture the standard output and error
            text=True,              # Return the output as a readable string
            check=True              # Throw an error if the command fails
        )
        
        # Check if there are any uncommitted changes
        if not result.stdout.strip():
            return "No uncommitted changes found."
            
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        return f"Error running git diff: {e.stderr}"

# Testing the function directly
if __name__ == "__main__":
    # Since the agent and target repo are side-by-side in the same parent folder:
    target_directory = "../sample-target-repo" 
    
    print(f"🔍 Extracting diff from: {target_directory}")
    print("-" * 40)
    
    diff_output = get_git_diff(target_directory)
    
    print(diff_output)
    print("-" * 40)