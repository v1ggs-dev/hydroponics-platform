import os
import argparse
import shutil
import tempfile
from pathlib import Path
from ultralytics import YOLO

# Project root = parent of the 'training' folder this script lives in
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def create_smoke_test_dataset(data_path, temp_dir):
    """Creates a miniature version of the dataset (50 images per class) for quick testing."""
    print("Creating smoke test dataset (50 images per class)...")
    
    data_path = Path(data_path)
    temp_dir = Path(temp_dir)
    
    # Iterate through train, val, test splits
    for split in ['train', 'val', 'test']:
        split_path = data_path / split
        if not split_path.exists():
            continue
            
        for class_dir in split_path.iterdir():
            if not class_dir.is_dir():
                continue
                
            out_class_dir = temp_dir / split / class_dir.name
            os.makedirs(out_class_dir, exist_ok=True)
            
            # Copy up to 50 images for this class
            images = list(class_dir.glob("*.*"))
            for img in images[:50]:
                shutil.copy2(img, out_class_dir)
                
    return str(temp_dir)

def main():
    parser = argparse.ArgumentParser(description="Train YOLO classification model for AgroEye.")
    parser.add_argument("--data", type=str, default=str(PROJECT_ROOT / "data" / "vision" / "plantvillage_tomato"), help="Path to prepared dataset directory")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs to train")
    parser.add_argument("--imgsz", type=int, default=224, help="Image size (YOLO standard for classification is 224)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (Keep small like 8 for CPU training)")
    parser.add_argument("--device", type=str, default="cpu", help="Device to use for training (e.g., 'cpu' or '0' for GPU)")
    parser.add_argument("--smoke-test", action="store_true", help="Run a quick smoke test with a small subset of data and fewer epochs")
    parser.add_argument("--project", type=str, default="runs/vision", help="Directory where training runs are saved")
    parser.add_argument("--name", type=str, default="tomato_v1", help="Name of this specific training run")
    args = parser.parse_args()

    print("="*50)
    print("STARTING YOLO TRAINING PIPELINE")
    print("="*50)

    data_path = args.data
    epochs = args.epochs

    # Check if smoke test flag is active
    if args.smoke_test:
        print("\n--- SMOKE TEST MODE ENABLED ---")
        temp_dir = tempfile.mkdtemp(prefix="agroeye_smoke_")
        data_path = create_smoke_test_dataset(args.data, temp_dir)
        epochs = 5  # Reduce epochs for quick verification
        print(f"Using temp dataset at {data_path} for {epochs} epochs.\n")

    # 1. Initialize YOLO Model
    print("Initializing YOLO11n classification model...")
    # Using 'yolo11n-cls.pt' downloads the pretrained Nano classification model
    model = YOLO("yolo11n-cls.pt")

    # 2. Train Model
    print(f"\nStarting training for {epochs} epochs on device: {args.device}...")
    results = model.train(
        data=data_path,
        epochs=epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
    )
    print("\nTraining complete.")

    # 3. Validate Model
    print("\nValidating model on validation set...")
    val_results = model.val()
    print("Validation metrics captured.")

    # 4. Save Best Model weights to a predictable location
    # Ultralytics saves runs in: <project>/<name>/weights/best.pt
    best_model_path = Path(args.project) / args.name / "weights" / "best.pt"
    
    target_models_dir = PROJECT_ROOT / "models" / "vision"
    os.makedirs(target_models_dir, exist_ok=True)
    target_model_path = target_models_dir / "best.pt"

    if best_model_path.exists():
        print(f"\nCopying best model from {best_model_path} to {target_model_path}")
        shutil.copy2(best_model_path, target_model_path)
    else:
        print(f"\nWarning: Best model not found at expected path: {best_model_path}")

    # Clean up the temporary directory if running smoke test
    if args.smoke_test:
        print("\nCleaning up smoke test temporary dataset...")
        shutil.rmtree(data_path, ignore_errors=True)

    print("\n" + "="*50)
    print("TRAINING PIPELINE FINISHED SUCCESSFULLY")
    print("="*50)

if __name__ == "__main__":
    main()
