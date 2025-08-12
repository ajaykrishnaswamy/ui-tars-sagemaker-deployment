#!/usr/bin/env python3
"""
Check for latest Hugging Face containers with newer Transformers versions
"""
import boto3
import json

def check_latest_hf_containers():
    """Check available HF containers and their versions"""
    
    # Known HF container repositories
    regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    for region in regions:
        print(f"\n🔍 Checking {region}...")
        ecr = boto3.client('ecr', region_name=region)
        
        # Common HF container patterns
        patterns = [
            'huggingface-pytorch-inference',
            'huggingface-tensorflow-inference',
            'huggingface-pytorch-training'
        ]
        
        for pattern in patterns:
            try:
                # List repositories matching pattern
                repos = ecr.describe_repositories()
                hf_repos = [r for r in repos['repositories'] if pattern in r['repositoryName']]
                
                for repo in hf_repos:
                    repo_name = repo['repositoryName']
                    print(f"  📦 {repo_name}")
                    
                    # Get recent images
                    try:
                        images = ecr.describe_images(
                            repositoryName=repo_name,
                            maxResults=10
                        )
                        
                        for image in images['imageDetails'][:3]:  # Show top 3
                            tags = image.get('imageTags', ['<no-tag>'])
                            print(f"    🏷️  {', '.join(tags)}")
                            
                    except Exception as e:
                        print(f"    ❌ Cannot list images: {e}")
                        
            except Exception as e:
                print(f"  ❌ Error checking {pattern}: {e}")

def get_transformers_version_from_tag(image_tag):
    """Extract transformers version from image tag"""
    import re
    match = re.search(r'transformers([\d.]+)', image_tag)
    if match:
        return match.group(1)
    return "unknown"

def find_compatible_containers():
    """Find containers with Transformers >= 4.40.0"""
    
    # AWS Deep Learning Container repository
    # These are the official container URIs
    containers = {
        'us-east-1': '763104351884.dkr.ecr.us-east-1.amazonaws.com',
        'us-west-2': '763104351884.dkr.ecr.us-west-2.amazonaws.com', 
        'eu-west-1': '763104351884.dkr.ecr.eu-west-1.amazonaws.com'
    }
    
    print("\n🔍 Checking for newer HuggingFace containers...")
    
    # Known newer container tags to try
    potential_containers = [
        "huggingface-pytorch-inference:2.1.0-transformers4.40.0-gpu-py310-cu118-ubuntu20.04",
        "huggingface-pytorch-inference:2.2.0-transformers4.41.0-gpu-py310-cu121-ubuntu20.04",
        "huggingface-pytorch-inference:2.3.0-transformers4.42.0-gpu-py310-cu121-ubuntu20.04"
    ]
    
    for region, base_uri in containers.items():
        print(f"\n📍 Region: {region}")
        for container in potential_containers:
            full_uri = f"{base_uri}/{container}"
            print(f"  🧪 Try: {full_uri}")
            
    return potential_containers

if __name__ == "__main__":
    print("🚀 Checking for UI-TARS compatible containers...")
    
    # Check what's available
    check_latest_hf_containers()
    
    # Show potential newer containers
    find_compatible_containers()
    
    print("""
    
🎯 Next Steps:
1. Try the newer container URIs above in your deployment scripts
2. If none work, build custom container with build_custom_container.sh
3. Or use a compatible model like BLIP-2 or Qwen2-VL
    """)