# StarryNight Walkthrough - Topics Discussed

## Layer Enforcement

Issue: [#120](https://github.com/broadinstitute/starrynight/issues/120)

Discussion about enforcement between layers - no current enforcement that algorithms have corresponding CLI commands or modules. Considered decorator approach to automatically create CLI from algorithms. Decided enforcement at test level might be useful, not at code level.

## Terminology Clarification

**Needs Issue Creation**

Terminology confusion emerged about "pipeline" vs "workflow". CellProfiler uses "pipeline", Snakemake uses "pipeline", StarryNight also uses "pipeline" - all mean different things. Decided to keep "pipeline" term but disambiguate in documentation. "Workflow" defined loosely as scientific image processing sequence implemented in modules.

## Channel Mapping and Multi-Cycle Experiments

Issue: [#125](https://github.com/broadinstitute/starrynight/issues/125)

Channel mapping problem surfaced as major issue. Current system hardcoded for 3 channels: nucleus, cell, mitochondria. These are "special" channels needed for segmentation. Other channels processed in aggregate but can't be named. Real experiments have many channels with different meanings across cycles. Example: AF488 in cycle 0 means DNA, but AF488 in cycle 1 means RNA.

Biologists need semantic names (DNA, RNA) not microscope names (AF488, AF750). Different microscopes call same thing different names - Texas Red vs 594. Currently adding new channels requires going to algorithm layer and changing code. This is unacceptable for biologists.

Configuration vs parser debate. Channel mapping could be handled at parser level or configuration level. Parser uses Lark grammar, originally written in Rust then moved to Python. Biologists find parser modification too technical. Agreement that channel mapping belongs in configuration not parser.

Example channel dictionary structure discussed - uses folder names as keys to handle multiple cycles. Load data CSV generation needs to support this complexity. Need 2 levels of nesting: file level and channel within file. Biologists won't follow strict file naming conventions even with clear documentation.

SABER experiments particularly challenging - multiple rounds of acquisition on same well. Published Periscope data was single phenotyping cycle so didn't hit this issue. SBS arm handles multiple files per site but channels have consistent meaning. Phenotyping with multiple rounds has channels that change meaning.

File naming chaos - biologists add random strings, periods, hashes. Microscopes have configurable output names. Can't rely on consistent naming even with strict guidelines. Erin enforced conventions for gallery but still had issues.

Parser configuration allows custom grammar definitions. Users can implement own parsers but this is too complex for biologists. Need to hide this complexity while maintaining flexibility.

LoadData CSV creator needs to handle arbitrary nesting and mappings. Current implementation supports standard single cycle or SABER throughout. Runs as Python script on AWS.

## Installation Options

Issue: [#121](https://github.com/broadinstitute/starrynight/issues/121)

Installation barriers discussed. Nix provides reproducible builds but scares biologists - "might nuke my computer". Need multiple installation options: Docker for simplicity, pip/uv for familiarity, Nix for developers. Current getting started guide too technical.

## Documentation Structure

Issue: [#114](https://github.com/broadinstitute/starrynight/issues/114)

Documentation structure needs different entry points. Current docs start with architecture which loses biologists. Need "I just want to run my images" path separate from developer path. Architecture for biologists document exists but might not be discoverable enough.
