# ============================================================
# AgroEye AI-1: Fine-tune v1 model on Web Images Only
# Much faster! Uses your already-trained model as starting point.
# Run in Google Colab (Runtime > T4 GPU)
# ============================================================

# Step 1: Install
!pip install ultralytics icrawler -q

# Step 2: Upload your best.pt from v1
# Click the 📁 folder icon on left sidebar → Upload → select best.pt
from google.colab import files
import os

if not os.path.exists("best.pt"):
    print("⬆️ Upload your best.pt (from models/vision/best.pt)")
    uploaded = files.upload()  # This opens a file picker dialog
    print("✅ Model uploaded!")

# Step 3: Download web images for each class
print("\n--- Downloading web images ---")
from icrawler.builtin import BingImageCrawler
from PIL import Image
from pathlib import Path
import shutil, logging
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

OUTPUT = "web_dataset"
PER_QUERY = 30  # ~60 per class

for cls_name, queries in QUERIES.items():
    # We need train/ and val/ splits for YOLO
    train_dir = os.path.join(OUTPUT, "train", cls_name)
    val_dir = os.path.join(OUTPUT, "val", cls_name)
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    temp_dir = f"web_temp/{cls_name}"
    os.makedirs(temp_dir, exist_ok=True)

    for query in queries:
        crawler = BingImageCrawler(
            storage={"root_dir": temp_dir},
            feeder_threads=1, parser_threads=1, downloader_threads=2,
        )
        crawler.crawl(keyword=query, max_num=PER_QUERY, min_size=(100, 100), file_idx_offset="auto")

    # Validate and split 80/20 into train/val
    valid_images = []
    for img_path in Path(temp_dir).glob("*"):
        try:
            with Image.open(img_path) as img:
                img.verify()
            valid_images.append(img_path)
        except:
            pass

    split_idx = int(0.8 * len(valid_images))
    for img in valid_images[:split_idx]:
        shutil.copy2(img, train_dir)
    for img in valid_images[split_idx:]:
        shutil.copy2(img, val_dir)

    print(f"  {cls_name}: train={split_idx}, val={len(valid_images)-split_idx}")

shutil.rmtree("web_temp", ignore_errors=True)

# Step 4: Fine-tune v1 on web images (FAST!)
from ultralytics import YOLO

# Load YOUR trained model (not the pretrained one!)
model = YOLO("best.pt")

results = model.train(
    data="web_dataset",
    epochs=20,           # Fewer epochs — just adapting, not learning from scratch
    imgsz=224,
    batch=32,
    device=0,
    project="runs",
    name="tomato_v2_finetuned",
    lr0=0.001,           # Lower learning rate — don't forget PlantVillage knowledge
    lrf=0.01,            # Final LR even lower
    warmup_epochs=2,
    
    # Augmentation
    hsv_h=0.02,
    hsv_s=0.5,
    hsv_v=0.4,
    degrees=15,
    translate=0.15,
    scale=0.4,
    fliplr=0.5,
    erasing=0.2,
    crop_fraction=0.8,
)

print("\n✅ Fine-tuning complete!")

# Step 5: Validate
val_results = model.val()
print(f"Top-1 Accuracy: {val_results.top1}")
print(f"Top-5 Accuracy: {val_results.top5}")

# Step 6: Download the fine-tuned model
best_model = "runs/tomato_v2_finetuned/weights/best.pt"
if os.path.exists(best_model):
    files.download(best_model)
    print("\n🎉 Fine-tuned model downloaded!")
    print("Replace your old models/vision/best.pt with this one.")
else:
    print("Check runs/ folder for the model")
