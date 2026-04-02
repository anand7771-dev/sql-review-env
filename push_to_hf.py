import os
from huggingface_hub import HfApi

def main():
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable is not set.")
        return

    api = HfApi(token=token)
    repo_id = "ananddev7771/sql-review-env"
    
    print(f"Uploading files to {repo_id}...")
    
    # Upload all files in the current directory except some ignores
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["*.pyc", "__pycache__/*", ".venv/*", "push_to_hf.py", ".git/*", "*.webp", "*.png", "val_out*.txt", "validate_output.txt"],
        commit_message="Add uv.lock for multi-mode deployment validation"
    )
    
    print("Upload complete!")

if __name__ == "__main__":
    main()
