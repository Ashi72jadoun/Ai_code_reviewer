import os
from dotenv import load_dotenv
from groq import Groq
from diff_extractor import get_git_diff
from static_analyzer import run_ruff, run_bandit
from context_gatherer import get_modified_files_context

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env file!")

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert Senior Software Engineer and Security Auditor.
Review the provided code changes (Git Diff) using the full file context and static analysis findings.

Focus on:
1. Logical bugs or runtime errors.
2. Security risks (e.g., insecure functions, unvalidated inputs).
3. Maintainability and refactoring suggestions.

Instructions:
- Base your review primarily on the Git Diff, using the full file context only to understand the surrounding code.
- If Bandit reports a security issue, emphasize it in your review.
- Provide a concise summary followed by structured findings.
- For each finding, include: Severity, Issue Name, Location, Description, and Recommended Fix (with code snippet).
"""

def generate_code_review(repo_path):
    print("\n🚀 Starting Advanced AI Code Review Process...\n")
    
    # Step 1: Extract Diff
    print("1️⃣ Extracting Git Diff...")
    diff = get_git_diff(repo_path)
    if diff == "No uncommitted changes found." or diff.startswith("Error"):
        print("❌ No changes to review or error occurred.")
        return
        
    # Step 2: Gather Context
    print("2️⃣ Gathering Full File Context...")
    context = get_modified_files_context(repo_path)
    
    # Step 3: Run Static Analyzers
    print("3️⃣ Running Bandit & Ruff (Static Analyzers)...")
    static_report = f"{run_ruff(repo_path)}\n{run_bandit(repo_path)}"
    
    # Step 4: Send to Groq LLM
    print("4️⃣ Sending compiled data to Groq LLM (Qwen model)...\n")
    
    user_prompt = f"""
--- GIT DIFF (The actual changes) ---
{diff}

--- STATIC ANALYSIS FINDINGS ---
{static_report}

--- FULL FILE CONTEXT (For reference only) ---
{context}
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model="qwen/qwen3.8-27b",
            temperature=0.2,
        )
        
        # Output ko print karne ke sath-sath return bhi kar rahe hain taaki UI isko use kar sake
        review_result = response.choices[0].message.content
        print("=" * 60)
        print("🤖 AI CODE REVIEW REPORT:")
        print("=" * 60)
        print(review_result)
        print("=" * 60)
        
        return review_result
        
    except Exception as e:
        error_msg = f"❌ Error connecting to Groq API: {e}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    target_dir = "../sample-target-repo"
    generate_code_review(target_dir)