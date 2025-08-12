#!/usr/bin/env python3
"""
Script to package the downloaded UI-TARS model for SageMaker deployment
"""

import tarfile
import os
import shutil

def create_sagemaker_model_package():
    """Package the UI-TARS model for SageMaker deployment"""
    
    model_dir = "UI-TARS-1.5-7B"
    output_file = "ui-tars-model.tar.gz"
    
    if not os.path.exists(model_dir):
        print(f"Error: Model directory {model_dir} not found!")
        print("Please run download_model.py first to download the model.")
        return False
    
    print(f"Packaging {model_dir} into {output_file}...")
    
    try:
        # Create tar.gz file
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(model_dir, arcname=".")
        
        # Get file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"Successfully created {output_file}")
        print(f"Package size: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error packaging model: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_sagemaker_model_package()
    if success:
        print("\nModel packaging completed successfully!")
        print("Next step: Upload ui-tars-model.tar.gz to S3")
    else:
        print("\nModel packaging failed!")
