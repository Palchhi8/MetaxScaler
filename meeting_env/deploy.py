import sys
import argparse
from huggingface_hub import HfApi, login, whoami

def main():
    print("="*60)
    print("🚀 Meeting Env HF Deployer")
    print("="*60)
    
    # 1. Verify token
    try:
        user_info = whoami()
        username = user_info['name']
        print(f"✅ Logged in as: {username}")
    except Exception:
        print("❌ You are not logged in. Please run: python -c \"from huggingface_hub import login; login()\" first")
        sys.exit(1)
        
    repo_id = f"{username}/meeting-env"
    print(f"\n📦 Preparing to upload to Space: {repo_id}")
    
    api = HfApi()
    
    # 2. Create the Space if it doesn't exist
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
            private=False
        )
        print("✅ Space prepared on Hugging Face")
    except Exception as e:
        print(f"❌ Failed to create Space: {e}")
        sys.exit(1)
        
    # 3. Upload all files from the current folder (meeting_env)
    print("\n⬆️ Uploading files... (This might take a minute)")
    try:
        api.upload_folder(
            folder_path=".",        # We run this from inside meeting_env
            repo_id=repo_id,
            repo_type="space",
            commit_message="Initial OpenEnv Meeting Environment Deployment"
        )
        print(f"🎉 SUCCESS! Environment perfectly deployed to: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"❌ Failed to upload files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
