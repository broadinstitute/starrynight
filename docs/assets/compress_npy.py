#!/usr/bin/env python3
"""
Compress a single NPY file to NPZ format.
Usage: python compress_npy.py <npy_file>
"""

import numpy as np
import os
import sys


def compress_npy_file(npy_file):
    try:
        # Load the array
        arr = np.load(npy_file)
        # Save with compression directly to .npz extension
        npz_file = npy_file.replace(".npy", ".npz")
        np.savez_compressed(npz_file, data=arr)
        print(f"Compressed {npy_file} to {npz_file}")
        return True
    except Exception as e:
        print(f"Error processing {npy_file}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <npy_file>", file=sys.stderr)
        sys.exit(1)

    npy_file = sys.argv[1]
    if not os.path.exists(npy_file):
        print(f"Error: File {npy_file} not found", file=sys.stderr)
        sys.exit(1)

    if not npy_file.endswith(".npy"):
        print(f"Error: File {npy_file} is not an NPY file", file=sys.stderr)
        sys.exit(1)

    success = compress_npy_file(npy_file)
    sys.exit(0 if success else 1)
