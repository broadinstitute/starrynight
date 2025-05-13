#!/bin/bash
#
# Create compressed archives of fixture data with SHA256 checksums
#
# This script creates tar.gz archives of StarryNight test fixture directories
# and generates SHA256 checksums for future validation.
#
# Usage:
#   ./create_fixture_archive.sh SOURCE_DIR [OUTPUT_DIR] [ARCHIVE_NAME]
#
# Example:
#   ./create_fixture_archive.sh /path/to/fixture/data ./archives fixture_data
#

# Default values
OUTPUT_DIR="./archives"

# Function to show usage
show_usage() {
    echo "Usage: $0 SOURCE_DIR [OUTPUT_DIR] [ARCHIVE_NAME]"
    echo ""
    echo "Arguments:"
    echo "  SOURCE_DIR    Source directory to archive (required)"
    echo "  OUTPUT_DIR    Directory where archive will be saved (default: ./archives)"
    echo "  ARCHIVE_NAME  Base name for the archive (default: basename of SOURCE_DIR)"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/fixture/data ./archives fixture_data"
    exit 1
}

# Check if source directory is provided
if [ -z "$1" ]; then
    echo "Error: Source directory not specified"
    show_usage
fi

SOURCE_DIR="$1"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Set output directory if provided
if [ ! -z "$2" ]; then
    OUTPUT_DIR="$2"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Set archive name if provided, otherwise use basename of source directory
if [ ! -z "$3" ]; then
    ARCHIVE_NAME="$3"
else
    ARCHIVE_NAME=$(basename "$SOURCE_DIR")
fi

# Full path to the archive file
ARCHIVE_PATH="$OUTPUT_DIR/$ARCHIVE_NAME.tar.gz"

# Create the archive
echo "Creating archive: $ARCHIVE_PATH"
tar -czf "$ARCHIVE_PATH" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

# Check if archive creation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to create archive"
    exit 1
fi

# Generate SHA256 checksum
echo "Generating SHA256 checksum for $ARCHIVE_PATH"
sha256sum "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
CHECKSUM=$(cut -d ' ' -f 1 "$ARCHIVE_PATH.sha256")
echo "Saved checksum to: $ARCHIVE_PATH.sha256"

# Print summary
echo ""
echo "Summary:"
echo "Archive: $ARCHIVE_PATH"
echo "SHA256: $CHECKSUM"
echo ""
echo "To verify: sha256sum -c $ARCHIVE_PATH.sha256"

exit 0
