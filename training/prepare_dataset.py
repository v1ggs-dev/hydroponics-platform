import os
import argparse
import subprocess
import hashlib
import random
import shutil
from pathlib import Path
from PIL import Image

def get_file_hash(filepath):
    """Computes MD5 hash of a file to detect duplicates."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def is_valid_image(filepath):
    """Verifies if an image can be opened and is not corrupt."""
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="Prepare PlantVillage dataset for YOLO classification.")
    parser.add_argument("--crop", type=str, default="Tomato", help="Crop name to filter (e.g., Tomato, Pepper, Potato)")
    args = parser.parse_args()

    crop_name = args.crop
    
    # Project root = parent of the 'training' folder this script lives in
    project_root = Path(__file__).resolve().parent.parent
    print(f"Project root: {project_root}")
    print(f"Preparing dataset for crop: {crop_name}")

    # 1. Clone the repository if it doesn't exist
    repo_url = "https://github.com/spMohanty/PlantVillage-Dataset.git"
    repo_dir = str(project_root / "PlantVillage-Dataset")
    
    if not os.path.exists(repo_dir):
        print(f"Cloning dataset repository ({repo_url}) --depth 1 ...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url], check=True)
    else:
        print("Dataset repository already cloned locally.")

    source_dir = os.path.join(repo_dir, "raw", "color")
    
    if not os.path.exists(source_dir):
        print(f"Error: Source directory {source_dir} not found. Ensure repository was cloned properly.")
        return

    # Base output directory (relative to project root)
    base_out_dir = project_root / "data" / "vision"
    out_dir = base_out_dir / f"plantvillage_{crop_name.lower()}"
    
    # Create output directories for train, val, test
    splits = ['train', 'val', 'test']
    for split in splits:
        os.makedirs(out_dir / split, exist_ok=True)

    # 2. Find and filter classes for the target crop
    all_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    classes = [d for d in all_dirs if d.lower().startswith(crop_name.lower())]
    
    print(f"\nFound {len(classes)} classes for {crop_name}:")
    for c in classes:
        print(f"  - {c}")

    if not classes:
        print(f"No classes found starting with '{crop_name}'.")
        return

    report = {}
    total_train, total_val, total_test = 0, 0, 0
    total_removed = 0

    # Fix random seed for reproducibility
    random.seed(42)

    for class_name in classes:
        print(f"\nProcessing class: {class_name}")
        class_dir = os.path.join(source_dir, class_name)
        
        valid_files = []
        seen_hashes = set()
        
        # 3. Clean images: Remove corrupt and duplicate files
        files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for f in files:
            filepath = os.path.join(class_dir, f)
            
            # Check for corruption
            if not is_valid_image(filepath):
                total_removed += 1
                continue
                
            # Check for exact duplicates using MD5
            file_hash = get_file_hash(filepath)
            if not file_hash or file_hash in seen_hashes:
                total_removed += 1
                continue
                
            seen_hashes.add(file_hash)
            valid_files.append(filepath)
            
        print(f"  Valid images: {len(valid_files)}")
        if len(valid_files) == 0:
            print("  Skipping class due to no valid images.")
            continue
            
        # 4. Split 80/10/10
        random.shuffle(valid_files)
        
        n_total = len(valid_files)
        n_train = int(0.8 * n_total)
        n_val = int(0.1 * n_total)
        
        train_files = valid_files[:n_train]
        val_files = valid_files[n_train:n_train+n_val]
        test_files = valid_files[n_train+n_val:]
        
        # 5. Copy files to output directory structure
        for split, files_to_copy in zip(splits, [train_files, val_files, test_files]):
            split_class_dir = out_dir / split / class_name
            os.makedirs(split_class_dir, exist_ok=True)
            
            for fpath in files_to_copy:
                shutil.copy2(fpath, split_class_dir)
                
        # Update counts for the report
        report[class_name] = {
            'train': len(train_files),
            'val': len(val_files),
            'test': len(test_files)
        }
        total_train += len(train_files)
        total_val += len(val_files)
        total_test += len(test_files)

    # 6. Print Summary Report
    print("\n" + "="*50)
    print("DATASET PREPARATION REPORT")
    print("="*50)
    print(f"Total Removed (Corrupt/Duplicates): {total_removed}")
    print("\nPer-class splits:")
    for class_name, counts in report.items():
        print(f"  {class_name}: Train={counts['train']}, Val={counts['val']}, Test={counts['test']}")
        
    print(f"\nTotal Splits:")
    print(f"  Train: {total_train}")
    print(f"  Val:   {total_val}")
    print(f"  Test:  {total_test}")
    print(f"  TOTAL: {total_train + total_val + total_test}")
    print(f"\nDataset successfully prepared at: {out_dir}")

if __name__ == "__main__":
    main()
