#!/usr/bin/env python3
"""Create compressed archives of fixture data with checksums.

This script creates tar.gz archives of StarryNight test fixture directories
and generates checksums for future validation.

Usage:
    python create_fixture_archive.py --source-dir <source_dir> [--output-dir <output_dir>]
                                     [--algorithm <algorithm>]

Example:
    python create_fixture_archive.py --source-dir /path/to/fixture/data --algorithm sha256

"""

import argparse
import hashlib
import subprocess
import sys
import tarfile
from pathlib import Path


def get_repo_root():
    """Get the absolute path of the repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository or git command failed")
        sys.exit(1)


def generate_checksum(file_path, algorithm="sha256"):
    """Generate a checksum for a file using the specified algorithm.

    Args:
        file_path: Path to the file to checksum
        algorithm: Hash algorithm to use (md5, sha256)

    Returns:
        str: Hexadecimal checksum

    """
    if algorithm == "md5":
        hash_func = hashlib.md5()
    elif algorithm == "sha256":
        hash_func = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with Path(file_path).open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def create_tarball(source_dir, output_path):
    """Create a compressed tar archive of a directory.

    Args:
        source_dir: Path to the directory to archive
        output_path: Path where the archive will be saved

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        source_path = Path(source_dir)
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(source_dir, arcname=source_path.name)
        return True
    except Exception as e:
        print(f"Error creating archive {output_path}: {e}")
        return False


def process_directory(
    source_dir, output_dir, algorithm="sha256", base_name=None
):
    """Process a directory: create archive and generate checksum.

    Args:
        source_dir: Path to the directory to process
        output_dir: Directory where the archive will be saved
        algorithm: Hash algorithm to use
        base_name: Base name for the archive (defaults to directory name)

    Returns:
        tuple: (archive_path, checksum) or (None, None) on failure

    """
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return None, None

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate archive name
    if base_name is None:
        base_name = source_path.name

    archive_name = f"{base_name}.tar.gz"
    archive_path = Path(output_dir) / archive_name

    # Create archive
    print(f"Creating archive: {archive_path}")
    if not create_tarball(source_dir, archive_path):
        return None, None

    # Generate checksum
    print(f"Generating {algorithm} checksum for {archive_path}")
    checksum = generate_checksum(archive_path, algorithm)

    # Save checksum to file
    checksum_path = f"{archive_path}.{algorithm}"
    with Path(checksum_path).open("w") as f:
        f.write(f"{checksum}  {archive_name}\n")

    print(f"Saved checksum to: {checksum_path}")

    return archive_path, checksum


def main():
    parser = argparse.ArgumentParser(
        description="Create archive for StarryNight fixtures"
    )

    parser.add_argument(
        "--source-dir", required=True, help="Source directory to archive"
    )
    parser.add_argument(
        "--output-dir",
        default="./archives",
        help="Directory where archive will be saved",
    )
    parser.add_argument(
        "--algorithm",
        default="sha256",
        choices=["md5", "sha256"],
        help="Checksum algorithm to use",
    )
    parser.add_argument(
        "--base-name",
        help="Base name for the archive (defaults to directory name)",
    )

    args = parser.parse_args()

    # Process the directory
    archive_path, checksum = process_directory(
        args.source_dir, args.output_dir, args.algorithm, args.base_name
    )

    if archive_path and checksum:
        print("\nSummary:")
        print(f"Archive: {archive_path}")
        print(f"{args.algorithm.upper()}: {checksum}")
        print(
            f"\nTo verify: {args.algorithm}sum -c {archive_path}.{args.algorithm}"
        )
    else:
        print("Failed to create archive")
        sys.exit(1)


if __name__ == "__main__":
    main()
