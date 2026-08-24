"""
Quick diagnostic script to check model health and class mappings.
Run: python training/diagnose_model.py
"""
from ultralytics import YOLO
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "vision" / "best.pt"
DATA_PATH = PROJECT_ROOT / "data" / "vision" / "plantvillage_tomato"

print("=" * 60)
print("MODEL DIAGNOSTIC REPORT")
print("=" * 60)

# 1. Check model exists and load it
print(f"\n1. Model path: {MODEL_PATH}")
if not MODEL_PATH.exists():
    print("   ERROR: best.pt not found!")
    exit()

model = YOLO(str(MODEL_PATH))
print(f"   Model loaded successfully")
print(f"   Model type: {model.task}")
print(f"   Number of classes: {len(model.names)}")
print(f"\n2. Class mapping (index -> name):")
for idx, name in model.names.items():
    print(f"   {idx}: {name}")

# 2. Check dataset class distribution
print(f"\n3. Dataset class distribution:")
if DATA_PATH.exists():
    for split in ['train', 'val', 'test']:
        split_path = DATA_PATH / split
        if split_path.exists():
            print(f"\n   [{split.upper()}]")
            total = 0
            for cls_dir in sorted(split_path.iterdir()):
                if cls_dir.is_dir():
                    count = len(list(cls_dir.glob("*")))
                    total += count
                    print(f"   {cls_dir.name}: {count} images")
            print(f"   TOTAL: {total}")
else:
    print("   Dataset not found at expected path")

# 3. Test predictions on one image from each class
print(f"\n4. Test prediction on 1 image per class from TEST set:")
test_path = DATA_PATH / "test"
if test_path.exists():
    correct = 0
    total = 0
    for cls_dir in sorted(test_path.iterdir()):
        if not cls_dir.is_dir():
            continue
        images = list(cls_dir.glob("*"))
        if not images:
            continue
        
        # Predict on first image of each class
        result = model.predict(str(images[0]), verbose=False)[0]
        predicted = result.names[result.probs.top1]
        confidence = float(result.probs.top1conf)
        
        match = "✓" if predicted == cls_dir.name else "✗"
        if predicted == cls_dir.name:
            correct += 1
        total += 1
        
        print(f"   {match} Actual: {cls_dir.name}")
        print(f"     Predicted: {predicted} ({confidence:.1%})")
        print()
    
    print(f"   Quick accuracy: {correct}/{total} = {correct/total:.1%}")
else:
    print("   Test set not found")

# 4. Check if model predicts same class for everything
print(f"\n5. Bias check — predicting on 5 random images per class:")
if test_path.exists():
    prediction_counts = {}
    for cls_dir in sorted(test_path.iterdir()):
        if not cls_dir.is_dir():
            continue
        images = list(cls_dir.glob("*"))[:5]
        for img in images:
            result = model.predict(str(img), verbose=False)[0]
            predicted = result.names[result.probs.top1]
            prediction_counts[predicted] = prediction_counts.get(predicted, 0) + 1
    
    print("   Prediction distribution across all test samples:")
    for cls, count in sorted(prediction_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"   {cls}: {count} {bar}")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
