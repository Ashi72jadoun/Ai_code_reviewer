import subprocess
import os

def get_modified_files_context(repo_path):
    """
    Finds which files were modified and reads their entire content.
    This gives the LLM the full context of the changed files.
    """
    if not os.path.exists(repo_path):
        return "Error: Repository path does not exist."

    try:
        # Get just the names of the files that changed
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        changed_files = result.stdout.strip().split('\n')
        
        # If no files are changed or the string is empty
        if not changed_files or changed_files == ['']:
            return "No modified files found to gather context."

        context_data = ""
        
        for file_name in changed_files:
            file_path = os.path.join(repo_path, file_name)
            
            # Read the entire file content if it exists
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                
                context_data += f"\n--- FULL CONTENT OF: {file_name} ---\n"
                context_data += file_content
                context_data += "\n" + ("-" * 40) + "\n"
                
        return context_data

    except subprocess.CalledProcessError as e:
        return f"Error getting modified files: {e.stderr}"
    except Exception as e:
        return f"Error reading file context: {e}"

# Testing the context gatherer
if __name__ == "__main__":
    target_dir = "../sample-target-repo"
    print("🔍 Gathering Context from modified files...\n")
    
    full_context = get_modified_files_context(target_dir)
    print(full_context)