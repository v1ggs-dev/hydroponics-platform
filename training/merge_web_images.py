"""
Merges web-downloaded images into the existing PlantVillage training set.
Run AFTER downloading web images and manually cleaning them.

Usage: python training/merge_web_images.py
"""
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "data" / "vision" / "web_images"
DATASET_DIR = PROJECT_ROOT / "data" / "vision" / "plantvillage_tomato"

def main():
    if not WEB_DIR.exists():
        print(f"Web images not found at {WEB_DIR}")
        print("Run download_web_images.py first!")
        return

    print("=" * 60)
    print("MERGING WEB IMAGES INTO TRAINING SET")
    print("=" * 60)

    total_added = 0

    for class_dir in sorted(WEB_DIR.iterdir()):
        if not class_dir.is_dir():
            continue

        class_name = class_dir.name
        target_dir = DATASET_DIR / "train" / class_name

        if not target_dir.exists():
            # Try to find matching class (handle naming differences)
            found = False
            for existing in (DATASET_DIR / "train").iterdir():
                if existing.is_dir() and existing.name.lower() == class_name.lower():
                    target_dir = existing
                    found = True
                    break
            if not found:
                os.makedirs(target_dir, exist_ok=True)

        images = list(class_dir.glob("*"))
        count = 0
        for img in images:
            # Add 'web_' prefix to avoid filename conflicts
            target = target_dir / f"web_{img.name}"
            if not target.exists():
                shutil.copy2(img, target)
                count += 1

        total_added += count
        print(f"  {class_name}: added {count} web images to train/")

    print(f"\nTotal added: {total_added} images")
    print("Dataset is ready for retraining!")

if __name__ == "__main__":
    main()
