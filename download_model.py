#!/usr/bin/env python3
"""
Script to download the UI-TARS-1.5-7B model from Hugging Face
"""

from huggingface_hub import snapshot_download
import os

def download_ui_tars_model():
    """Download UI-TARS-1.5-7B model from Hugging Face"""
    
    model_id = "ByteDance-Seed/UI-TARS-1.5-7B"
    local_dir = "UI-TARS-1.5-7B"
    
    print(f"Downloading {model_id} to {local_dir}...")
    
    try:
        snapshot_download(
            repo_id=model_id, 
            local_dir=local_dir,
            local_dir_use_symlinks=False  # Download actual files, not symlinks
        )
        print(f"Successfully downloaded model to {local_dir}/")
        
        # List the downloaded files
        print("\nDownloaded files:")
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"  {file_path}")
                
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = download_ui_tars_model()
    if success:
        print("\nModel download completed successfully!")
    else:
        print("\nModel download failed!")
