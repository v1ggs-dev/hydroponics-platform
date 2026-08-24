"""
Downloads diverse plant disease images from the web for each tomato class.
Uses icrawler (Bing) to fetch real-world images that differ from PlantVillage.

Install: pip install icrawler
Run: python training/download_web_images.py --per-class 50
"""
import os
import argparse
from pathlib import Path

# Search queries mapped to PlantVillage class names
TOMATO_QUERIES = {
    "Tomato___Bacterial_spot": [
        "tomato bacterial spot leaf disease",
        "tomato bacterial spot symptoms",
    ],
    "Tomato___Early_blight": [
        "tomato early blight leaf",
        "tomato early blight disease symptoms",
    ],
    "Tomato___Late_blight": [
        "tomato late blight leaf disease",
        "tomato late blight symptoms photo",
    ],
    "Tomato___Leaf_Mold": [
        "tomato leaf mold disease",
        "tomato leaf mold fungus symptoms",
    ],
    "Tomato___Septoria_leaf_spot": [
        "tomato septoria leaf spot disease",
        "septoria leaf spot tomato symptoms",
    ],
    "Tomato___Spider_mites Two-spotted_spider_mite": [
        "tomato spider mites damage leaf",
        "two spotted spider mite tomato",
    ],
    "Tomato___Target_Spot": [
        "tomato target spot leaf disease",
        "tomato target spot corynespora",
    ],
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": [
        "tomato yellow leaf curl virus",
        "TYLCV tomato leaf curling",
    ],
    "Tomato___Tomato_mosaic_virus": [
        "tomato mosaic virus leaf symptoms",
        "ToMV tomato mosaic virus",
    ],
    "Tomato___healthy": [
        "healthy tomato leaf green",
        "tomato plant healthy leaves",
    ],
}


def main():
    parser = argparse.ArgumentParser(description="Download web images for each tomato disease class.")
    parser.add_argument("--per-class", type=int, default=50, help="Number of images to download per class (default: 50)")
    parser.add_argument("--output", type=str, default=None, help="Output directory (default: data/vision/web_images)")
    args = parser.parse_args()

    # Try importing icrawler
    try:
        from icrawler.builtin import BingImageCrawler
    except ImportError:
        print("icrawler not installed! Run: pip install icrawler")
        print("Then run this script again.")
        return

    project_root = Path(__file__).resolve().parent.parent
    output_dir = Path(args.output) if args.output else project_root / "data" / "vision" / "web_images"

    per_class = args.per_class
    # Split queries evenly
    per_query = per_class // 2 + 1  

    print("=" * 60)
    print(f"DOWNLOADING WEB IMAGES ({per_class} per class)")
    print("=" * 60)

    for class_name, queries in TOMATO_QUERIES.items():
        class_dir = output_dir / class_name
        os.makedirs(class_dir, exist_ok=True)

        print(f"\n📥 {class_name}:")
        
        for query in queries:
            print(f"   Searching: '{query}'")
            crawler = BingImageCrawler(
                storage={"root_dir": str(class_dir)},
                feeder_threads=1,
                parser_threads=1,
                downloader_threads=2,
            )
            # Suppress icrawler logs
            import logging
            logging.getLogger("icrawler").setLevel(logging.WARNING)

            crawler.crawl(
                keyword=query,
                max_num=per_query,
                min_size=(100, 100),  # Skip tiny images
                file_idx_offset="auto",
            )

        # Count downloaded images
        count = len(list(class_dir.glob("*")))
        print(f"   ✅ Downloaded: {count} images")

    # Validate images (remove corrupt ones)
    print("\n\nValidating downloaded images...")
    from PIL import Image
    removed = 0
    total = 0
    for class_dir in output_dir.iterdir():
        if not class_dir.is_dir():
            continue
        for img_path in class_dir.glob("*"):
            total += 1
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception:
                img_path.unlink()
                removed += 1

    print(f"Validated {total} images, removed {removed} corrupt files.")

    # Final report
    print("\n" + "=" * 60)
    print("DOWNLOAD REPORT")
    print("=" * 60)
    for class_dir in sorted(output_dir.iterdir()):
        if class_dir.is_dir():
            count = len(list(class_dir.glob("*")))
            print(f"  {class_dir.name}: {count} images")

    print(f"\nImages saved to: {output_dir}")
    print("\nNext step: Review the images manually — delete any")
    print("that are NOT actual tomato leaf disease photos.")
    print("(Some web results may be irrelevant diagrams, logos, etc.)")


if __name__ == "__main__":
    main()
