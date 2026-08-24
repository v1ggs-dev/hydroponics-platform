# ============================================================
# AgroEye AI-1 v2: YOLO Training with Web Images + Augmentation
# Run in Google Colab (Runtime > Change runtime type > T4 GPU)
# ============================================================
# BEFORE RUNNING: Upload your web_images folder to Colab
# (or run the download script directly in Colab)

# Step 1: Install dependencies
!pip install ultralytics icrawler -q

# Step 2: Clone PlantVillage dataset
import os
if not os.path.exists("PlantVillage-Dataset"):
    !git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset.git

# Step 3: Prepare dataset (same as before)
import shutil, hashlib, random
from pathlib import Path
from PIL import Image

random.seed(42)
SOURCE = "PlantVillage-Dataset/raw/color"
OUTPUT = "plantvillage_tomato"
CROP = "Tomato"

all_dirs = [d for d in os.listdir(SOURCE) if os.path.isdir(os.path.join(SOURCE, d))]
classes = [d for d in all_dirs if d.lower().startswith(CROP.lower())]
print(f"Found {len(classes)} classes")

for cls in classes:
    cls_path = os.path.join(SOURCE, cls)
    files = [f for f in os.listdir(cls_path) if f.lower().endswith(('.png','.jpg','.jpeg'))]
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

# Step 4: Download web images directly in Colab
print("\n--- Downloading web images for diversity ---")
from icrawler.builtin import BingImageCrawler
import logging
logging.getLogger("icrawler").setLevel(logging.ERROR)

QUERIES = {
    "Tomato___Bacterial_spot": ["tomato bacterial spot leaf disease", "tomato bacterial spot symptoms"],
    "Tomato___Early_blight": ["tomato early blight leaf", "tomato early blight disease symptoms"],
    "Tomato___Late_blight": ["tomato late blight leaf disease", "tomato late blight symptoms photo"],
    "Tomato___Leaf_Mold": ["tomato leaf mold disease", "tomato leaf mold fungus symptoms"],
    "Tomato___Septoria_leaf_spot": ["tomato septoria leaf spot disease", "septoria leaf spot tomato symptoms"],
    "Tomato___Spider_mites Two-spotted_spider_mite": ["tomato spider mites damage leaf", "two spotted spider mite tomato"],
    "Tomato___Target_Spot": ["tomato target spot leaf disease", "tomato target spot corynespora"],
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": ["tomato yellow leaf curl virus", "TYLCV tomato leaf curling"],
    "Tomato___Tomato_mosaic_virus": ["tomato mosaic virus leaf symptoms", "ToMV tomato mosaic virus"],
    "Tomato___healthy": ["healthy tomato leaf green", "tomato plant healthy leaves"],
}

PER_QUERY = 30  # ~60 images per class total

for cls_name, queries in QUERIES.items():
    train_dir = os.path.join(OUTPUT, "train", cls_name)
    os.makedirs(train_dir, exist_ok=True)
    
    temp_dir = f"web_temp/{cls_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    for query in queries:
        crawler = BingImageCrawler(
            storage={"root_dir": temp_dir},
            feeder_threads=1, parser_threads=1, downloader_threads=2,
        )
        crawler.crawl(keyword=query, max_num=PER_QUERY, min_size=(100, 100), file_idx_offset="auto")
    
    # Validate and copy to train
    added = 0
    for img_path in Path(temp_dir).glob("*"):
        try:
            with Image.open(img_path) as img:
                img.verify()
            shutil.copy2(img_path, os.path.join(train_dir, f"web_{img_path.name}"))
            added += 1
        except:
            pass
    print(f"  {cls_name}: +{added} web images added to train/")

# Cleanup temp
shutil.rmtree("web_temp", ignore_errors=True)

# Step 5: Train with STRONG AUGMENTATION
from ultralytics import YOLO

model = YOLO("yolo11n-cls.pt")

results = model.train(
    data="plantvillage_tomato",
    epochs=60,          # Slightly more epochs to learn diverse images
    imgsz=224,
    batch=32,
    device=0,
    project="runs",
    name="tomato_v2_augmented",
    
    # STRONG AUGMENTATION (key difference from v1!)
    hsv_h=0.02,         # Hue variation
    hsv_s=0.5,          # Saturation variation (handles different lighting)
    hsv_v=0.4,          # Brightness variation
    degrees=15,          # Rotation (leaves can be at angles)
    translate=0.15,      # Position shift
    scale=0.4,           # Zoom variation
    fliplr=0.5,          # Horizontal flip
    flipud=0.1,          # Slight vertical flip
    erasing=0.2,         # Random erasing (robustness)
    crop_fraction=0.8,   # Random crop
)

print("\n✅ Training complete!")

# Step 6: Validate
val_results = model.val()
print(f"Top-1 Accuracy: {val_results.top1}")
print(f"Top-5 Accuracy: {val_results.top5}")

# Step 7: Download model
from google.colab import files
best_model = "runs/tomato_v2_augmented/weights/best.pt"
if os.path.exists(best_model):
    files.download(best_model)
    print("\n🎉 best.pt downloaded! Replace your old models/vision/best.pt with this one.")
else:
    print("Check runs/ folder for the model weights")

# Step 8: Quick sanity test
test_dir = "plantvillage_tomato/test"
test_classes = os.listdir(test_dir)
print("\nQuick test predictions:")
for cls in sorted(test_classes)[:5]:
    imgs = os.listdir(os.path.join(test_dir, cls))
    if imgs:
        r = model.predict(os.path.join(test_dir, cls, imgs[0]), verbose=False)[0]
        pred = r.names[r.probs.top1]
        conf = float(r.probs.top1conf)
        match = "✓" if pred == cls else "✗"
        print(f"  {match} Actual: {cls} → Predicted: {pred} ({conf:.1%})")
