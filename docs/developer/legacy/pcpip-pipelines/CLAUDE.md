# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# StarryNight PCPIP-Pipelines Reference Collection

## Purpose
This folder contains a curated collection of CellProfiler pipeline files that serve as references for the PCPIP workflow. While located in the tests directory, these are primarily reference pipelines that may be used as test fixtures for the StarryNight pipeline parser and validation tools.

## Commands
- Compare pipelines: `diff -w pipeline1.cppipe pipeline2.cppipe > comparison.diff`
- Visualize pipelines: Use cp_graph tool (see README.md)

## Directory Structure
- `ref_*.cppipe`: Reference pipeline files used for testing
- `_pcpip_12cycles/`: Original 12-cycle pipelines from PCPIP
- `_refsource/`: Source pipeline variants with comparison diffs
- `_ref_graph_format/`: Pipeline visualizations (JSON, DOT, SVG, PNG)

## Working with Reference Pipelines
- These files are carefully selected reference implementations of the PCPIP workflow
- Reference pipelines document important pipeline configurations and variations
- When comparing pipelines, use `diff -w` to ignore whitespace differences
- Any modifications should be documented in commit messages
- Visualizations help understand pipeline structure without requiring CellProfiler
