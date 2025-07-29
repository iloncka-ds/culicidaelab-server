#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line script to rename mosquito image files based on species names.

This script scans a specified directory for image files and renames them
according to a predefined list of mosquito species. The new filename will
be the species ID followed by the original file extension.

Example Usage:
    python rename_mosquito_images.py "/path/to/your/image/folder"
"""

import os
import glob
import argparse

# A dictionary mapping species IDs to their names. The script will look for these names.
SPECIES_MAP = {
    0: "aedes_aegypti",
    1: "aedes_albopictus",
    2: "aedes_canadensis",
    3: "aedes_dorsalis",
    4: "aedes_geniculatus",
    5: "aedes_koreicus",
    6: "aedes_triseriatus",
    7: "aedes_vexans",
    8: "anopheles_arabiensis",
    9: "anopheles_freeborni",
    10: "anopheles_sinensis",
    12: "culex_inatomii",
    13: "culex_pipiens",
    14: "culex_quinquefasciatus",
    15: "culex_tritaeniorhynchus",
    16: "culiseta_annulata",
    17: "culiseta_longiareolata",
}
# A list of species names derived from the map for efficient searching.
SPECIES_LIST = list(SPECIES_MAP.values())


def process_and_rename_files(directory_path: str):
    """
    Scans a directory, finds files matching species names, and renames them.

    Args:
        directory_path (str): The full path to the directory containing images.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at '{directory_path}'")
        return

    print(f"Scanning for files in: {directory_path}\n")

    # Use glob to find all items in the directory.
    search_pattern = os.path.join(directory_path, '*')
    items_in_directory = glob.glob(search_pattern)

    processed_count = 0
    skipped_count = 0

    for old_path in items_in_directory:
        # Ensure we are only processing files, not subdirectories.
        if not os.path.isfile(old_path):
            continue

        filename = os.path.basename(old_path)
        _, file_ext = os.path.splitext(filename)

        found_species = None
        # Iterate through the species list to find a match in the filename.
        for species_name in SPECIES_LIST:
            if species_name.lower() in filename.lower():
                found_species = species_name
                break  # Stop after the first match.

        if found_species:
            new_filename = f"{found_species}{file_ext}"
            new_path = os.path.join(directory_path, new_filename)

            if old_path == new_path:
                print(f'INFO: Skipping (already named correctly): "{filename}"')
                continue

            try:
                os.rename(old_path, new_path)
                print(f'SUCCESS: Renamed "{filename}" to "{new_filename}"')
                processed_count += 1
            except FileExistsError:
                print(f'WARNING: Could not rename "{filename}" because "{new_filename}" already exists.')
                skipped_count += 1
            except OSError as e:
                print(f'ERROR: Could not rename "{filename}". Reason: {e}')
                skipped_count += 1
        else:
            # This handles files that don't match any species (e.g., "non_vectors").
            print(f'SKIPPED: No matching species found for "{filename}"')
            skipped_count +=1

    print(f"\nProcessing complete. Renamed {processed_count} files, skipped {skipped_count} files.")


def main():
    """Parses command-line arguments and initiates the renaming process."""
    parser = argparse.ArgumentParser(
        description="Renames mosquito image files in a directory to their corresponding species ID.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The path to the directory containing the image files to be renamed."
    )

    args = parser.parse_args()
    process_and_rename_files(args.directory)


if __name__ == "__main__":
    main()