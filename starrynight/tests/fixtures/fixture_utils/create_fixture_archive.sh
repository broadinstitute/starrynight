#!/bin/bash
#
# Create compressed archives of fixture data with checksums
#
# This script creates tar.gz archives of StarryNight test fixture directories
# and generates checksums for future validation.
#
# Usage:
#   ./create_fixture_archive.sh SOURCE_DIR [OUTPUT_DIR] [ARCHIVE_NAME] [ALGORITHM]
#
# Example:
#   ./create_fixture_archive.sh /path/to/fixture/data ./archives fixture_data sha256
#

# Default values
OUTPUT_DIR="./archives"
ALGORITHM="sha256"

# Function to show usage
show_usage() {
    echo "Usage: $0 SOURCE_DIR [OUTPUT_DIR] [ARCHIVE_NAME] [ALGORITHM]"
    echo ""
    echo "Arguments:"
    echo "  SOURCE_DIR    Source directory to archive (required)"
    echo "  OUTPUT_DIR    Directory where archive will be saved (default: ./archives)"
    echo "  ARCHIVE_NAME  Base name for the archive (default: basename of SOURCE_DIR)"
    echo "  ALGORITHM     Checksum algorithm to use: md5 or sha256 (default: sha256)"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/fixture/data ./archives fixture_data sha256"
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

# Set checksum algorithm if provided
if [ ! -z "$4" ]; then
    if [ "$4" != "md5" ] && [ "$4" != "sha256" ]; then
        echo "Error: Invalid algorithm. Use 'md5' or 'sha256'"
        exit 1
    fi
    ALGORITHM="$4"
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

# Generate checksum
echo "Generating $ALGORITHM checksum for $ARCHIVE_PATH"
if [ "$ALGORITHM" == "md5" ]; then
    md5sum "$ARCHIVE_PATH" > "$ARCHIVE_PATH.md5"
    CHECKSUM=$(cat "$ARCHIVE_PATH.md5" | cut -d ' ' -f 1)
    echo "Saved checksum to: $ARCHIVE_PATH.md5"
else
    # Default to sha256
    sha256sum "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
    CHECKSUM=$(cat "$ARCHIVE_PATH.sha256" | cut -d ' ' -f 1)
    echo "Saved checksum to: $ARCHIVE_PATH.sha256"
fi

# Print summary
echo ""
echo "Summary:"
echo "Archive: $ARCHIVE_PATH"
echo "${ALGORITHM^^}: $CHECKSUM"
echo ""
echo "To verify: ${ALGORITHM}sum -c $ARCHIVE_PATH.$ALGORITHM"

exit 0
