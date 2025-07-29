import argparse
import sys
from pathlib import Path
from shutil import move

from PIL import Image

def process_images(source_dir: Path):
    """
    Organizes images from a source directory into subdirectories named after
    the image, creates a detail version, and a 100x100 thumbnail.

    Args:
        source_dir (Path): The path to the directory containing the images.
    """
    print(f"Scanning directory: {source_dir}\n")

    # Define valid image extensions
    image_extensions = ['.png', '.jpg', '.jpeg']

    # Find all image files directly within the source directory
    image_files = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print("No image files found to process.")
        return

    for image_path in image_files:
        try:
            # 1. Create the species-specific directory
            species_id = image_path.stem  # Filename without extension
            output_dir = source_dir / species_id
            output_dir.mkdir(exist_ok=True)
            print(f"Processing '{species_id}':")

            # 2. Move the original image and rename it to 'detail'
            detail_filename = f"detail{image_path.suffix}"
            detail_path = output_dir / detail_filename
            thumbnail_size = (512, 512)

            with Image.open(image_path) as img:
                # Use thumbnail() to maintain aspect ratio while fitting into 100x100
                img.thumbnail(thumbnail_size)

                # If the image has an alpha channel (like PNG), convert it to RGB
                # before saving as a JPEG to avoid errors.
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.save(detail_path, "jpeg")
                print(f"  -> Created 224x224 thumbnail as 'detail.jpg'")


            # 3. Create the thumbnail
            thumbnail_size = (100, 100)
            thumbnail_path = output_dir / "thumbnail.jpg"

            with Image.open(detail_path) as img:
                # Use thumbnail() to maintain aspect ratio while fitting into 100x100
                img.thumbnail(thumbnail_size)

                # If the image has an alpha channel (like PNG), convert it to RGB
                # before saving as a JPEG to avoid errors.
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                img.save(thumbnail_path, 'jpeg')
                print(f"  -> Created 100x100 thumbnail as 'thumbnail.jpg'")

        except Exception as e:
            print(f"  -> ERROR: Could not process {image_path.name}. Reason: {e}")

        print("-" * 20)

    print("\nScript finished.")


def main():
    """Main function to parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Organize species images into folders and create thumbnails.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "image_directory",
        help="The path to the directory containing the source images (e.g., 'species')."
    )

    args = parser.parse_args()
    source_directory = Path(args.image_directory)

    if not source_directory.is_dir():
        print(f"Error: The specified directory does not exist: {source_directory}", file=sys.stderr)
        sys.exit(1)

    process_images(source_directory)


if __name__ == "__main__":
    main()