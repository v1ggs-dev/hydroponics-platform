# ============================================================
# AgroEye AI-1: YOLO Plant Disease Classification
# Run this in Google Colab (Runtime > Change runtime type > T4 GPU)
# ============================================================

# Step 1: Install ultralytics
!pip install ultralytics -q

# Step 2: Clone PlantVillage dataset
!git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset.git

# Step 3: Prepare the dataset (filter tomato, split 80/10/10)
import os, shutil, hashlib, random
from pathlib import Path
from PIL import Image

random.seed(42)
SOURCE = "PlantVillage-Dataset/raw/color"
OUTPUT = "plantvillage_tomato"
CROP = "Tomato"

# Find tomato classes
all_dirs = [d for d in os.listdir(SOURCE) if os.path.isdir(os.path.join(SOURCE, d))]
classes = [d for d in all_dirs if d.lower().startswith(CROP.lower())]
print(f"Found {len(classes)} classes: {classes}")

# Clean + split
for cls in classes:
    cls_path = os.path.join(SOURCE, cls)
    files = [f for f in os.listdir(cls_path) if f.lower().endswith(('.png','.jpg','.jpeg'))]

    # Remove corrupt images
    valid = []
    seen = set()
    for f in files:
        fp = os.path.join(cls_path, f)
        try:
            with Image.open(fp) as img:
                img.verify()
            h = hashlib.md5(open(fp,'rb').read()).hexdigest()
            if h not in seen:
                seen.add(h)
                valid.append(fp)
        except:
            pass

    random.shuffle(valid)
    n = len(valid)
    splits = {
        'train': valid[:int(0.8*n)],
        'val': valid[int(0.8*n):int(0.9*n)],
        'test': valid[int(0.9*n):]
    }

    for split, split_files in splits.items():
        out = os.path.join(OUTPUT, split, cls)
        os.makedirs(out, exist_ok=True)
        for fp in split_files:
            shutil.copy2(fp, out)

    print(f"  {cls}: train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}")

print("\nDataset ready!")

# Step 4: Train YOLO11n-cls on T4 GPU (~15 min)
from ultralytics import YOLO

model = YOLO("yolo11n-cls.pt")  # pretrained nano classification model

results = model.train(
    data="plantvillage_tomato",
    epochs=50,
    imgsz=224,
    batch=32,       # T4 can handle batch=32 easily
    device=0,       # Use GPU
    project="runs",
    name="tomato_v1",
)

print("\nTraining complete!")

# Step 5: Validate
val_results = model.val()
print(f"Top-1 Accuracy: {val_results.top1}")
print(f"Top-5 Accuracy: {val_results.top5}")

# Step 6: Download the trained model
from google.colab import files
best_model = "runs/tomato_v1/weights/best.pt"
if os.path.exists(best_model):
    files.download(best_model)
    print("best.pt downloaded! Place it in: Hydroponics_ai/models/vision/best.pt")
else:
    print("Check runs/ folder for the model")

# Step 7: Quick test inference
results = model.predict("plantvillage_tomato/test/" + os.listdir("plantvillage_tomato/test")[0] + "/" + os.listdir("plantvillage_tomato/test/" + os.listdir("plantvillage_tomato/test")[0])[0])
r = results[0]
print(f"\nTest prediction: {r.names[r.probs.top1]} ({r.probs.top1conf:.2%})")
