import argparse
import json
import re
from collections import defaultdict, Counter
import networkx as nx
import difflib


def parse_cppipe(filepath):
    """Parse a CellProfiler pipeline into structured data"""
    with open(filepath, "r") as f:
        content = f.read()

    # Parse header
    header_match = re.search(
        r"(CellProfiler Pipeline.*?)ModuleCount:", content, re.DOTALL
    )
    header = header_match.group(1) if header_match else ""

    # Extract module count
    module_count_match = re.search(r"ModuleCount:(\d+)", content)
    module_count = int(module_count_match.group(1)) if module_count_match else 0

    # Extract modules
    modules = []
    module_blocks = re.findall(
        r"(\w+):\[module_num:(\d+)\|.*?variable_revision_number:(\d+).*?enabled:(True|False).*?\](.*?)(?=\w+:\[module_num|\Z)",
        content,
        re.DOTALL,
    )

    for module_type, module_num, revision, enabled, params in module_blocks:
        parameters = {}
        param_lines = [p.strip() for p in params.strip().split("\n") if p.strip()]
        for line in param_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                parameters[key.strip()] = value.strip()

        modules.append(
            {
                "type": module_type,
                "module_num": int(module_num),
                "revision": int(revision),
                "enabled": enabled == "True",
                "parameters": parameters,
            }
        )

    return {"header": header, "module_count": module_count, "modules": modules}


def extract_channels(pipeline, enabled_only=True):
    """Identify channels used in the pipeline"""
    channels = set()

    # Look for channel patterns in image names
    for module in pipeline["modules"]:
        if enabled_only and not module["enabled"]:
            continue

        for param, value in module["parameters"].items():
            if param in [
                "Select the input image",
                "Name the output image",
                "Select the image to save",
            ]:
                # Extract channel from image name using common patterns
                if value.startswith("Orig"):
                    channels.add(value[4:])  # e.g., OrigDNA -> DNA
                elif "DNA" in value:
                    channels.add("DNA")
                elif "ER" in value:
                    channels.add("ER")
                elif "Mito" in value:
                    channels.add("Mito")
                elif "Phalloidin" in value:
                    channels.add("Phalloidin")
                elif "WGA" in value:
                    channels.add("WGA")
                elif "ZEB1" in value:
                    channels.add("ZEB1")
                elif "ZO1" in value:
                    channels.add("ZO1")
                elif "Overlay" in value:
                    channels.add("Overlay")
                elif any(nucl in value for nucl in ["A_", "C_", "G_", "T_"]):
                    for nucl in ["A", "C", "G", "T"]:
                        if f"{nucl}_" in value:
                            channels.add(nucl)

            # Also check multi-image parameters
            elif "Select images" in param and isinstance(value, str):
                image_list = [img.strip() for img in value.split(",")]
                for img in image_list:
                    if "DNA" in img:
                        channels.add("DNA")
                    elif "ER" in img:
                        channels.add("ER")
                    elif "Mito" in img:
                        channels.add("Mito")
                    elif "Phalloidin" in img:
                        channels.add("Phalloidin")
                    elif "WGA" in img:
                        channels.add("WGA")
                    elif "ZEB1" in img:
                        channels.add("ZEB1")
                    elif "ZO1" in img:
                        channels.add("ZO1")
                    elif "Overlay" in img:
                        channels.add("Overlay")
                    elif "ConA" in img:
                        channels.add("ConA")

    return channels


def get_module_processing_channel(module):
    """Determine which channel a module is processing"""
    for param, value in module["parameters"].items():
        if param in [
            "Select the input image",
            "Name the output image",
            "Select the image to save",
        ]:
            # Extract channel from image name
            if value.startswith("Orig"):
                return value[4:]
            elif "DNA" in value:
                return "DNA"
            elif "ER" in value:
                return "ER"
            elif "Mito" in value:
                return "Mito"
            elif "Phalloidin" in value:
                return "Phalloidin"
            elif "WGA" in value:
                return "WGA"
            elif "ZEB1" in value:
                return "ZEB1"
            elif "ZO1" in value:
                return "ZO1"
            elif "Overlay" in value:
                return "Overlay"
    return None


def group_modules_by_channel(pipeline):
    """Group modules by the channel they process"""
    channel_modules = defaultdict(list)

    for module in pipeline["modules"]:
        if not module["enabled"]:
            continue

        channel = get_module_processing_channel(module)
        if channel:
            channel_modules[channel].append(module)

    return channel_modules


def build_pipeline_graph(pipeline):
    """Build a directed graph representing data flow through the pipeline"""
    G = nx.DiGraph()

    # Track image and object output names
    output_map = {}  # Maps output names to creating modules

    for module in pipeline["modules"]:
        if not module["enabled"]:
            continue

        G.add_node(module["module_num"], module=module)

        # Find inputs this module depends on
        for param, value in module["parameters"].items():
            if (
                "Select" in param and "image" in param.lower()
            ) or "Select objects" in param:
                if value in output_map:
                    # Add edge from producer to consumer
                    G.add_edge(output_map[value], module["module_num"], data=value)

                # Also handle comma-separated lists of inputs
                if isinstance(value, str) and "," in value:
                    for item in [i.strip() for i in value.split(",")]:
                        if item in output_map:
                            G.add_edge(
                                output_map[item], module["module_num"], data=item
                            )

        # Track outputs this module creates
        for param, value in module["parameters"].items():
            if "Name the output" in param or (
                "Name the" in param and "objects" in param.lower()
            ):
                output_map[value] = module["module_num"]

    return G, output_map


def identify_channel_workflows(G, pipeline):
    """Extract subgraphs representing complete processing for each channel"""
    channel_graphs = {}
    channel_modules = defaultdict(list)

    # First pass: identify the starting module for each channel
    for module in pipeline["modules"]:
        if not module["enabled"]:
            continue

        channel = get_module_processing_channel(module)
        if channel:
            channel_modules[channel].append(module["module_num"])

    # Second pass: expand each channel's workflow by traversing the graph
    for channel, seed_modules in channel_modules.items():
        subgraph_nodes = set(seed_modules)

        # Expand to include upstream and downstream modules
        for seed in seed_modules:
            # Only proceed if seed is in the graph (it might be isolated)
            if seed in G:
                # Get all descendants (modules that use this module's output)
                try:
                    descendants = list(nx.descendants(G, seed))
                    subgraph_nodes.update(descendants)
                except:  # noqa: E722
                    pass

                # Get all ancestors (modules that produce inputs for this module)
                try:
                    ancestors = list(nx.ancestors(G, seed))
                    subgraph_nodes.update(ancestors)
                except:  # noqa: E722
                    pass

        # Create the subgraph for this channel if it has nodes
        if subgraph_nodes:
            # Filter to ensure all nodes are in G
            valid_nodes = [n for n in subgraph_nodes if n in G]
            if valid_nodes:
                channel_graphs[channel] = G.subgraph(valid_nodes)

    return channel_graphs


def detect_refactoring_patterns(pipeline1, pipeline2):
    """Identify high-level refactoring patterns between pipeline versions"""
    # Build pipeline graphs
    try:
        G1, outputs1 = build_pipeline_graph(pipeline1)
        G2, outputs2 = build_pipeline_graph(pipeline2)

        channel_graphs1 = identify_channel_workflows(G1, pipeline1)
        channel_graphs2 = identify_channel_workflows(G2, pipeline2)

        refactoring_patterns = []

        # Detect channel replacements
        removed_channels = set(channel_graphs1.keys()) - set(channel_graphs2.keys())
        added_channels = set(channel_graphs2.keys()) - set(channel_graphs1.keys())

        if removed_channels and added_channels:
            # Check if processing steps are similar
            for removed in removed_channels:
                for added in added_channels:
                    # Compare processing steps in the workflows
                    removed_steps = [
                        pipeline1["modules"][n - 1]["type"]
                        for n in channel_graphs1[removed].nodes()
                    ]
                    added_steps = [
                        pipeline2["modules"][n - 1]["type"]
                        for n in channel_graphs2[added].nodes()
                    ]

                    # Calculate similarity
                    removed_types = Counter(removed_steps)
                    added_types = Counter(added_steps)

                    # Use Jaccard similarity of module types
                    common_count = sum((removed_types & added_types).values())
                    total_count = sum((removed_types | added_types).values())

                    if total_count > 0:
                        similarity = common_count / total_count
                        if (
                            similarity > 0.5
                        ):  # Threshold for considering it a replacement
                            refactoring_patterns.append(
                                {
                                    "type": "channel_replacement",
                                    "removed_channel": removed,
                                    "added_channel": added,
                                    "similarity": similarity,
                                    "description": f"Channel {removed} was likely replaced by {added} with similar processing workflow ({int(similarity * 100)}% similar)",
                                }
                            )

        # Detect algorithm changes
        for channel in set(channel_graphs1.keys()) & set(channel_graphs2.keys()):
            g1 = channel_graphs1[channel]
            g2 = channel_graphs2[channel]

            # Extract module types for this channel in each pipeline
            types1 = [pipeline1["modules"][n - 1]["type"] for n in g1.nodes()]
            types2 = [pipeline2["modules"][n - 1]["type"] for n in g2.nodes()]

            # Check for major algorithm changes
            key_algorithms = [
                "RunCellpose",
                "IdentifyPrimaryObjects",
                "IdentifySecondaryObjects",
                "MeasureTexture",
                "MeasureGranularity",
                "MeasureObjectSizeShape",
            ]

            for algo in key_algorithms:
                if algo in types1 and algo not in types2:
                    alternatives = [
                        t for t in types2 if t not in types1 and t in key_algorithms
                    ]
                    if alternatives:
                        refactoring_patterns.append(
                            {
                                "type": "algorithm_change",
                                "channel": channel,
                                "from_algorithm": algo,
                                "to_algorithm": ", ".join(alternatives),
                                "description": f"Changed analytical approach for {channel} from {algo} to {', '.join(alternatives)}",
                            }
                        )

        # Detect processing reordering
        for channel in set(channel_graphs1.keys()) & set(channel_graphs2.keys()):
            modules1 = [
                m
                for m in pipeline1["modules"]
                if m["enabled"] and get_module_processing_channel(m) == channel
            ]
            modules2 = [
                m
                for m in pipeline2["modules"]
                if m["enabled"] and get_module_processing_channel(m) == channel
            ]

            # Get sequences of module types
            seq1 = [m["type"] for m in sorted(modules1, key=lambda x: x["module_num"])]
            seq2 = [m["type"] for m in sorted(modules2, key=lambda x: x["module_num"])]

            # If similar modules but different order
            if seq1 and seq2:
                # Get the longest common subsequence
                sm = difflib.SequenceMatcher(None, seq1, seq2)
                if sm.ratio() > 0.7 and seq1 != seq2:
                    refactoring_patterns.append(
                        {
                            "type": "process_reordering",
                            "channel": channel,
                            "description": f"Similar processing steps for {channel} but in different order",
                        }
                    )

        return refactoring_patterns
    except Exception:
        # If graph analysis fails, return empty list
        return []


def detect_version_migrations(param_diffs):
    """Identify parameter changes due to module version updates"""
    migration_patterns = []

    # Common parameter migration patterns
    version_patterns = [
        {
            "old_params": [
                "X Resizing factor",
                "Y Resizing factor",
                "Z Resizing factor",
            ],
            "new_params": ["Resizing factor"],
            "description": "Updated from separate X/Y/Z resize factors to single resize factor",
        },
        {
            "old_params": [
                "Width (x) of the final image",
                "Height (y) of the final image",
                "# of planes (z) in the final image",
            ],
            "new_params": ["Width of the final image", "Height of the final image"],
            "description": "Updated from X/Y/Z dimensions to simpler Width/Height parameters",
        },
        {
            "old_params": ["X Factor", "Y Factor", "Z Factor"],
            "new_params": ["Factor"],
            "description": "Updated from separate X/Y/Z factors to single factor",
        },
        {
            "old_params": ["Width (X)", "Height (Y)", "Planes (Z)"],
            "new_params": ["Width", "Height"],
            "description": "Updated from X/Y/Z dimensions to simpler Width/Height",
        },
        {
            "old_params": ["Allow fuzzy feature matching?"],
            "new_params": [],
            "description": "Removed deprecated fuzzy matching parameter",
        },
        {
            "old_params": ["Save with lossless compression?"],
            "new_params": [],
            "description": "Removed deprecated compression parameter",
        },
    ]

    # Check for each pattern
    for pattern in version_patterns:
        # Count how many old params are removed and new params are added
        old_params_found = sum(
            1
            for p in pattern["old_params"]
            if p in param_diffs and param_diffs[p]["change"] == "removed"
        )
        new_params_found = sum(
            1
            for p in pattern["new_params"]
            if p in param_diffs and param_diffs[p]["change"] == "added"
        )

        # If we found a substantial match
        if (
            (old_params_found > 0 or len(pattern["old_params"]) == 0)
            and (new_params_found > 0 or len(pattern["new_params"]) == 0)
            and (old_params_found + new_params_found > 0)
        ):
            migration_patterns.append(
                {
                    "pattern": pattern["description"],
                    "old_params": [
                        p
                        for p in pattern["old_params"]
                        if p in param_diffs and param_diffs[p]["change"] == "removed"
                    ],
                    "new_params": [
                        p
                        for p in pattern["new_params"]
                        if p in param_diffs and param_diffs[p]["change"] == "added"
                    ],
                    "confidence": (old_params_found + new_params_found)
                    / (len(pattern["old_params"]) + len(pattern["new_params"]) or 1),
                }
            )

    return migration_patterns


def analyze_parameter_changes(param_diffs):
    """Analyze parameter changes for significance and patterns"""
    result = {
        "high_impact": [],
        "medium_impact": [],
        "low_impact": [],
        "version_migrations": detect_version_migrations(param_diffs),
        "list_changes": {},
    }

    # Detect high-impact parameters
    high_impact_patterns = [
        "threshold",
        "method",
        "algorithm",
        "diameter",
        "size",
        "cycles",
        "deviations",
        "mode",
        "background",
        "calculate",
        "identify",
    ]

    # Medium impact parameters
    medium_impact_patterns = [
        "factor",
        "filter",
        "smooth",
        "scale",
        "distance",
        "output",
        "count",
    ]

    # Check each parameter change
    for param, diff in param_diffs.items():
        if diff["change"] == "modified":
            # Parse list changes
            if "," in str(diff["from"]) and "," in str(diff["to"]):
                from_list = [item.strip() for item in str(diff["from"]).split(",")]
                to_list = [item.strip() for item in str(diff["to"]).split(",")]

                removed = [item for item in from_list if item not in to_list]
                added = [item for item in to_list if item not in from_list]

                if added or removed:
                    result["list_changes"][param] = {"added": added, "removed": removed}

            # Determine impact level
            impact = "low_impact"
            param_lower = param.lower()

            if any(pattern in param_lower for pattern in high_impact_patterns):
                impact = "high_impact"
            elif any(pattern in param_lower for pattern in medium_impact_patterns):
                impact = "medium_impact"

            result[impact].append(
                {"parameter": param, "from": diff["from"], "to": diff["to"]}
            )

    return result


def compare_modules(module1, module2):
    """Compare two modules and determine if they should be considered the same module"""
    # If module types are different, they're not the same module
    if module1["type"] != module2["type"]:
        return False

    # For channel-specific modules, check if they're processing the same channel
    if module1["type"] in ["SaveImages", "CorrectIlluminationApply", "MaskImage"]:
        channel1 = get_module_processing_channel(module1)
        channel2 = get_module_processing_channel(module2)

        # If channels are explicitly defined and different, these are different modules
        if channel1 and channel2 and channel1 != channel2:
            return False

        # Check image parameters to see if they're processing the same images
        for param in ["Select the image to save", "Select the input image"]:
            if param in module1["parameters"] and param in module2["parameters"]:
                # If the image names are completely different (not just metadata changes)
                img1 = module1["parameters"][param]
                img2 = module2["parameters"][param]

                # Strip out metadata tags for comparison
                base_img1 = re.sub(r"\\g<[^>]+>", "", img1)
                base_img2 = re.sub(r"\\g<[^>]+>", "", img2)

                if base_img1.strip() != base_img2.strip():
                    return False

    return True


def create_module_signature(module):
    """Create a more precise signature that includes channel information"""
    # Extract channel info
    channel = get_module_processing_channel(module)

    # For modules that process specific channels (like SaveImages)
    if module["type"] in ["SaveImages", "CorrectIlluminationApply", "MaskImage"]:
        # Include channel in the signature to prevent cross-channel matches
        key_params = {
            k: v
            for k, v in module["parameters"].items()
            if k in ["Select the image to save", "Select the input image"]
        }
        return (module["type"], channel, frozenset(key_params.items()))
    else:
        # For non-channel-specific modules, use the original approach
        key_params = {
            k: v
            for k, v in module["parameters"].items()
            if k in ["Select the input image", "Name the output image"]
        }
        return (module["type"], frozenset(key_params.items()))


def compare_pipelines(pipeline1, pipeline2):
    """Compare two parsed pipelines and return structured differences"""
    # Get enabled module counts
    enabled_count1 = sum(1 for m in pipeline1["modules"] if m["enabled"])
    enabled_count2 = sum(1 for m in pipeline2["modules"] if m["enabled"])

    result = {
        "header_changes": {},
        "stats": {
            "total_modules_1": len(pipeline1["modules"]),
            "total_modules_2": len(pipeline2["modules"]),
            "enabled_modules_1": enabled_count1,
            "enabled_modules_2": enabled_count2,
            "disabled_modules_1": len(pipeline1["modules"]) - enabled_count1,
            "disabled_modules_2": len(pipeline2["modules"]) - enabled_count2,
        },
        "channels": {"added": [], "removed": [], "common": []},
        "module_changes": {"added": [], "removed": [], "modified": []},
        "channel_processing": {},
        "refactoring": detect_refactoring_patterns(pipeline1, pipeline2),
        "metadata_changes": [],
    }

    # Extract channels (respecting enabled_only flag)
    channels1 = extract_channels(pipeline1, True)
    channels2 = extract_channels(pipeline2, True)

    result["channels"]["added"] = list(channels2 - channels1)
    result["channels"]["removed"] = list(channels1 - channels2)
    result["channels"]["common"] = list(channels1 & channels2)

    # Filter enabled modules
    modules1 = [m for m in pipeline1["modules"] if m["enabled"]]
    modules2 = [m for m in pipeline2["modules"] if m["enabled"]]

    # Group modules by channel
    channel_modules1 = group_modules_by_channel(pipeline1)
    channel_modules2 = group_modules_by_channel(pipeline2)

    # Compare channel processing
    for channel in set(channel_modules1.keys()) | set(channel_modules2.keys()):
        if channel not in channel_modules1:
            result["channel_processing"][channel] = "added"
        elif channel not in channel_modules2:
            result["channel_processing"][channel] = "removed"
        else:
            # Compare module sequences for this channel
            mods1 = channel_modules1[channel]
            mods2 = channel_modules2[channel]

            # Simple sequence comparison
            if len(mods1) != len(mods2):
                result["channel_processing"][channel] = (
                    f"changed (module count: {len(mods1)} → {len(mods2)})"
                )
            else:
                diff_count = 0
                for m1, m2 in zip(mods1, mods2):
                    if m1["type"] != m2["type"]:
                        diff_count += 1

                if diff_count > 0:
                    result["channel_processing"][channel] = (
                        f"changed ({diff_count} modules differ)"
                    )
                else:
                    # Check parameters
                    param_diffs = {}
                    for m1, m2 in zip(mods1, mods2):
                        for param in set(m1["parameters"].keys()) | set(
                            m2["parameters"].keys()
                        ):
                            if param not in m1["parameters"]:
                                param_diffs[param] = (
                                    f"{m1['type']} added param: {param}"
                                )
                            elif param not in m2["parameters"]:
                                param_diffs[param] = (
                                    f"{m1['type']} removed param: {param}"
                                )
                            elif m1["parameters"][param] != m2["parameters"][param]:
                                param_diffs[param] = (
                                    f"{m1['type']} changed {param}: {m1['parameters'][param]} → {m2['parameters'][param]}"
                                )

                    if param_diffs:
                        result["channel_processing"][channel] = (
                            f"changed parameters ({len(param_diffs)} differences)"
                        )
                    else:
                        result["channel_processing"][channel] = "unchanged"

    modules1_sigs = {create_module_signature(m): m for m in modules1}
    modules2_sigs = {create_module_signature(m): m for m in modules2}

    # Keep track of matched modules to identify additions later
    matched_modules2 = set()

    # Enhanced module matching with smart comparison
    for sig1, module1 in modules1_sigs.items():
        best_match = None
        best_score = 0

        for sig2, module2 in modules2_sigs.items():
            # Skip if already matched to prevent double-matching
            if sig2 in matched_modules2:
                continue

            if compare_modules(module1, module2):
                # Calculate a similarity score based on parameter overlap
                params1 = set(module1["parameters"].keys())
                params2 = set(module2["parameters"].keys())
                common_params = params1.intersection(params2)

                # Score is based on parameter similarity
                score = len(common_params) / max(len(params1), len(params2))

                # Boost score for exact type matches and channel matches
                if module1["type"] == module2["type"]:
                    score += 0.2  # Boost for same type

                channel1 = get_module_processing_channel(module1)
                channel2 = get_module_processing_channel(module2)
                if channel1 and channel2 and channel1 == channel2:
                    score += 0.3  # Boost for same channel

                if score > best_score:
                    best_score = score
                    best_match = (sig2, module2)

        # Threshold for considering a match - higher for channel-specific modules
        threshold = 0.6
        if module1["type"] in ["SaveImages", "CorrectIlluminationApply", "MaskImage"]:
            threshold = 0.7

        if best_match and best_score > threshold:
            # Mark this module as matched
            matched_sig, module2 = best_match
            matched_modules2.add(matched_sig)

            # Compare these modules as modifications
            param_diffs = {}
            for param in set(module1["parameters"].keys()) | set(
                module2["parameters"].keys()
            ):
                if param not in module1["parameters"]:
                    param_diffs[param] = {
                        "change": "added",
                        "value": module2["parameters"][param],
                    }
                elif param not in module2["parameters"]:
                    param_diffs[param] = {
                        "change": "removed",
                        "value": module1["parameters"][param],
                    }
                elif module1["parameters"][param] != module2["parameters"][param]:
                    # Check if this is a metadata-only change
                    metadata_diff = compare_metadata_patterns(
                        module1["parameters"][param], module2["parameters"][param]
                    )

                    param_diffs[param] = {
                        "change": "modified",
                        "from": module1["parameters"][param],
                        "to": module2["parameters"][param],
                        "metadata_change": metadata_diff
                        if metadata_diff["changed"]
                        else None,
                    }

                    # Track overall metadata changes
                    if metadata_diff["changed"] and not metadata_diff["base_changed"]:
                        result["metadata_changes"].append(
                            {
                                "module_type": module1["type"],
                                "module_num_1": module1["module_num"],
                                "module_num_2": module2["module_num"],
                                "parameter": param,
                                "diff": metadata_diff,
                            }
                        )

            if param_diffs:
                # Analyze parameter changes in detail
                param_analysis = analyze_parameter_changes(param_diffs)

                module_change = {
                    "type": module1["type"],
                    "from_module_num": module1["module_num"],
                    "to_module_num": module2["module_num"],
                    "channel": get_module_processing_channel(module1),
                    "parameter_diffs": param_diffs,
                    "parameter_analysis": param_analysis,
                    "version_change": (module1["revision"] != module2["revision"]),
                    "revision_from": module1["revision"],
                    "revision_to": module2["revision"],
                }

                result["module_changes"]["modified"].append(module_change)
        else:
            # This module was removed
            result["module_changes"]["removed"].append(
                {
                    "type": module1["type"],
                    "module_num": module1["module_num"],
                    "channel": get_module_processing_channel(module1),
                    "key_params": dict([p for p in sig1[-1]])
                    if isinstance(sig1[-1], frozenset)
                    else {},
                }
            )

    # Find added modules (those not matched in pipeline2)
    for sig2, module2 in modules2_sigs.items():
        if sig2 not in matched_modules2:
            result["module_changes"]["added"].append(
                {
                    "type": module2["type"],
                    "module_num": module2["module_num"],
                    "channel": get_module_processing_channel(module2),
                    "key_params": dict([p for p in sig2[-1]])
                    if isinstance(sig2[-1], frozenset)
                    else {},
                }
            )

    return result


def generate_report(diff_result, format="text"):
    """Generate a human-readable diff report"""
    if format == "text":
        report = []

        # Pipeline statistics
        report.append("=== PIPELINE STATISTICS ===")
        stats = diff_result["stats"]
        report.append(
            f"Pipeline 1: {stats['enabled_modules_1']} enabled modules, {stats['disabled_modules_1']} disabled modules"
        )
        report.append(
            f"Pipeline 2: {stats['enabled_modules_2']} enabled modules, {stats['disabled_modules_2']} disabled modules"
        )
        report.append(
            f"Module change: {stats['enabled_modules_1']} → {stats['enabled_modules_2']} ({stats['enabled_modules_2'] - stats['enabled_modules_1']})"
        )

        # Metadata changes summary
        if diff_result.get("metadata_changes"):
            report.append("\n=== METADATA REFERENCE CHANGES ===")
            report.append(
                "The following metadata reference pattern changes were found:"
            )
            for change in diff_result["metadata_changes"]:
                report.append(
                    f"* {change['module_type']} (Module {change['module_num_1']} → {change['module_num_2']}): {change['parameter']}"
                )
                report.append(f"  {change['diff']['description']}")

        # Refactoring detection
        if diff_result["refactoring"]:
            report.append("\n=== DETECTED REFACTORING PATTERNS ===")
            for pattern in diff_result["refactoring"]:
                report.append(f"* {pattern['description']}")

        # Channel summary
        report.append("\n=== CHANNEL SUMMARY ===")
        if diff_result["channels"]["added"]:
            report.append(
                f"Added channels: {', '.join(diff_result['channels']['added'])}"
            )
        if diff_result["channels"]["removed"]:
            report.append(
                f"Removed channels: {', '.join(diff_result['channels']['removed'])}"
            )
        report.append(
            f"Common channels: {', '.join(diff_result['channels']['common'])}"
        )

        # Channel processing differences
        report.append("\n=== CHANNEL PROCESSING CHANGES ===")
        for channel, status in sorted(diff_result["channel_processing"].items()):
            report.append(f"Channel {channel}: {status}")

        # Module changes
        if diff_result["module_changes"]["added"]:
            report.append("\n=== ADDED MODULES ===")
            for mod in diff_result["module_changes"]["added"]:
                report.append(
                    f"+ Module {mod['module_num']}: {mod['type']} (Channel: {mod['channel'] or 'unknown'})"
                )
                for k, v in mod["key_params"].items():
                    report.append(f"  {k}: {v}")

        if diff_result["module_changes"]["removed"]:
            report.append("\n=== REMOVED MODULES ===")
            for mod in diff_result["module_changes"]["removed"]:
                report.append(
                    f"- Module {mod['module_num']}: {mod['type']} (Channel: {mod['channel'] or 'unknown'})"
                )
                for k, v in mod["key_params"].items():
                    report.append(f"  {k}: {v}")

        if diff_result["module_changes"]["modified"]:
            report.append("\n=== MODIFIED MODULES ===")
            for mod in diff_result["module_changes"]["modified"]:
                channel_info = f"Channel: {mod['channel'] or 'unknown'}"
                version_info = ""
                if mod.get("version_change", False):
                    version_info = (
                        f", Revision: {mod['revision_from']} → {mod['revision_to']}"
                    )

                report.append(
                    f"* {mod['type']} (Module {mod['from_module_num']} → {mod['to_module_num']}, {channel_info}{version_info})"
                )

                # Show version migration patterns if detected
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["version_migrations"]
                ):
                    for migration in mod["parameter_analysis"]["version_migrations"]:
                        if migration["confidence"] > 0.5:
                            report.append(f"  [Version Change] {migration['pattern']}")

                # Show high impact changes
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["high_impact"]
                ):
                    report.append("  [High Impact Changes]")
                    for change in mod["parameter_analysis"]["high_impact"]:
                        report.append(
                            f"  ! {change['parameter']}: {change['from']} → {change['to']}"
                        )

                # Show list changes
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["list_changes"]
                ):
                    for param, changes in mod["parameter_analysis"][
                        "list_changes"
                    ].items():
                        if changes["added"]:
                            report.append(
                                f"  + Added to {param}: {', '.join(changes['added'])}"
                            )
                        if changes["removed"]:
                            report.append(
                                f"  - Removed from {param}: {', '.join(changes['removed'])}"
                            )

                # Show other parameter changes
                for param, diff in mod["parameter_diffs"].items():
                    # Skip parameters that were already reported in special sections
                    skip = False
                    if "parameter_analysis" in mod:
                        # Skip parameters in version migrations
                        for migration in mod["parameter_analysis"][
                            "version_migrations"
                        ]:
                            if (
                                param in migration["old_params"]
                                or param in migration["new_params"]
                            ):
                                skip = True
                                break

                        # Skip parameters in high impact section
                        if not skip:
                            for change in mod["parameter_analysis"]["high_impact"]:
                                if param == change["parameter"]:
                                    skip = True
                                    break

                        # Skip parameters in list changes
                        if (
                            not skip
                            and param in mod["parameter_analysis"]["list_changes"]
                        ):
                            skip = True

                    if not skip:
                        if diff["change"] == "added":
                            report.append(f"  + {param}: {diff['value']}")
                        elif diff["change"] == "removed":
                            report.append(f"  - {param}: {diff['value']}")
                        elif diff["change"] == "modified":
                            # Check if this is a metadata-only change
                            if "metadata_change" in diff and diff["metadata_change"]:
                                metadata_diff = diff["metadata_change"]
                                if not metadata_diff["base_changed"]:
                                    report.append(
                                        f"  * {param}: [Metadata References Only] {metadata_diff['description']}"
                                    )
                                else:
                                    report.append(
                                        f"  * {param}: {diff['from']} → {diff['to']} (includes metadata changes)"
                                    )
                            else:
                                report.append(
                                    f"  * {param}: {diff['from']} → {diff['to']}"
                                )

        return "\n".join(report)

    elif format == "html":
        # Generate HTML report with CSS styling
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".added { color: green; }",
            ".removed { color: red; }",
            ".modified { color: blue; }",
            ".note { background-color: #f8f8f8; padding: 10px; border-left: 5px solid #ccc; }",
            ".high-impact { background-color: #ffeeee; font-weight: bold; }",
            ".refactoring { background-color: #eeeeff; padding: 10px; margin-bottom: 10px; border-left: 5px solid #88f; }",
            ".version-change { background-color: #eeffee; padding: 5px; margin: 5px 0; border-left: 3px solid #8f8; }",
            ".metadata-change { background-color: #fff8e8; padding: 5px; margin: 5px 0; border-left: 3px solid #fc3; }",
            "table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
            "table, th, td { border: 1px solid #ddd; }",
            "th, td { padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "tr:nth-child(even) { background-color: #f9f9f9; }",
            "h2 { color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; }",
            "summary { cursor: pointer; font-weight: bold; padding: 5px; background-color: #f8f8f8; }",
            "details { margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }",
            "details[open] summary { background-color: #e8e8e8; }",
            "</style>",
            "<title>CellProfiler Pipeline Diff</title>",
            "</head>",
            "<body>",
            "<h1>CellProfiler Pipeline Diff Report</h1>",
        ]

        # Pipeline statistics
        html.append("<div class='note'>")
        stats = diff_result["stats"]
        html.append(
            f"<p><strong>Pipeline 1:</strong> {stats['enabled_modules_1']} enabled modules, {stats['disabled_modules_1']} disabled modules</p>"
        )
        html.append(
            f"<p><strong>Pipeline 2:</strong> {stats['enabled_modules_2']} enabled modules, {stats['disabled_modules_2']} disabled modules</p>"
        )
        net_change = stats["enabled_modules_2"] - stats["enabled_modules_1"]
        change_symbol = "+" if net_change > 0 else ""
        html.append(
            f"<p><strong>Module change:</strong> {stats['enabled_modules_1']} → {stats['enabled_modules_2']} ({change_symbol}{net_change})</p>"
        )
        html.append("</div>")

        # Metadata changes summary
        if diff_result.get("metadata_changes"):
            html.append("<h2>Metadata Reference Changes</h2>")
            html.append("<div class='metadata-change'>")
            html.append(
                "<p>The following metadata reference pattern changes were detected:</p>"
            )
            html.append("<ul>")
            for change in diff_result["metadata_changes"]:
                html.append(
                    f"<li><strong>{change['module_type']}</strong> (Module {change['module_num_1']} → {change['module_num_2']}): {change['parameter']}<br>"
                )
                html.append(f"{change['diff']['description']}</li>")
            html.append("</ul>")
            html.append("</div>")

        # Refactoring patterns
        if diff_result["refactoring"]:
            html.append("<h2>Detected Refactoring Patterns</h2>")
            for pattern in diff_result["refactoring"]:
                html.append(f"<div class='refactoring'>{pattern['description']}</div>")

        # Channel summary
        html.append("<h2>Channel Summary</h2>")
        if diff_result["channels"]["added"]:
            html.append(
                f"<p><span class='added'>Added channels:</span> {', '.join(diff_result['channels']['added'])}</p>"
            )
        if diff_result["channels"]["removed"]:
            html.append(
                f"<p><span class='removed'>Removed channels:</span> {', '.join(diff_result['channels']['removed'])}</p>"
            )
        html.append(
            f"<p>Common channels: {', '.join(diff_result['channels']['common'])}</p>"
        )

        # Channel processing table
        html.append("<h2>Channel Processing Changes</h2>")
        html.append("<table>")
        html.append("<tr><th>Channel</th><th>Status</th></tr>")
        for channel, status in sorted(diff_result["channel_processing"].items()):
            class_name = ""
            if "added" in status:
                class_name = "added"
            elif "removed" in status:
                class_name = "removed"
            elif "changed" in status:
                class_name = "modified"
            html.append(
                f"<tr><td>{channel}</td><td class='{class_name}'>{status}</td></tr>"
            )
        html.append("</table>")

        # Module changes
        if diff_result["module_changes"]["added"]:
            html.append("<h2>Added Modules</h2>")
            html.append("<table>")
            html.append(
                "<tr><th>Module #</th><th>Type</th><th>Channel</th><th>Parameters</th></tr>"
            )
            for mod in diff_result["module_changes"]["added"]:
                params = ", ".join([f"{k}: {v}" for k, v in mod["key_params"].items()])
                html.append(
                    f"<tr class='added'><td>{mod['module_num']}</td><td>{mod['type']}</td><td>{mod['channel'] or 'unknown'}</td><td>{params}</td></tr>"
                )
            html.append("</table>")

        if diff_result["module_changes"]["removed"]:
            html.append("<h2>Removed Modules</h2>")
            html.append("<table>")
            html.append(
                "<tr><th>Module #</th><th>Type</th><th>Channel</th><th>Parameters</th></tr>"
            )
            for mod in diff_result["module_changes"]["removed"]:
                params = ", ".join([f"{k}: {v}" for k, v in mod["key_params"].items()])
                html.append(
                    f"<tr class='removed'><td>{mod['module_num']}</td><td>{mod['type']}</td><td>{mod['channel'] or 'unknown'}</td><td>{params}</td></tr>"
                )
            html.append("</table>")

        if diff_result["module_changes"]["modified"]:
            html.append("<h2>Modified Modules</h2>")

            for mod in diff_result["module_changes"]["modified"]:
                channel_info = f"Channel: {mod['channel'] or 'unknown'}"
                version_info = ""
                if mod.get("version_change", False):
                    version_info = (
                        f", Revision: {mod['revision_from']} → {mod['revision_to']}"
                    )

                html.append("<details>")
                html.append(
                    f"<summary>{mod['type']} (Module {mod['from_module_num']} → {mod['to_module_num']}, {channel_info}{version_info})</summary>"
                )

                # Version migration patterns
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["version_migrations"]
                ):
                    for migration in mod["parameter_analysis"]["version_migrations"]:
                        if migration["confidence"] > 0.5:
                            html.append(
                                f"<div class='version-change'>{migration['pattern']}</div>"
                            )

                # Show list changes
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["list_changes"]
                ):
                    html.append("<div style='margin: 10px 0;'>")
                    for param, changes in mod["parameter_analysis"][
                        "list_changes"
                    ].items():
                        if changes["added"]:
                            html.append(
                                f"<p><span class='added'>+ Added to {param}:</span> {', '.join(changes['added'])}</p>"
                            )
                        if changes["removed"]:
                            html.append(
                                f"<p><span class='removed'>- Removed from {param}:</span> {', '.join(changes['removed'])}</p>"
                            )
                    html.append("</div>")

                # Parameter table
                html.append("<table>")
                html.append(
                    "<tr><th>Parameter</th><th>Change</th><th>From</th><th>To</th></tr>"
                )

                # First show high impact parameters
                if (
                    "parameter_analysis" in mod
                    and mod["parameter_analysis"]["high_impact"]
                ):
                    for change in mod["parameter_analysis"]["high_impact"]:
                        html.append(
                            f"<tr class='high-impact'><td>{change['parameter']}</td><td class='modified'>Modified</td><td>{change['from']}</td><td>{change['to']}</td></tr>"
                        )

                # Then show all other parameters
                for param, diff in mod["parameter_diffs"].items():
                    # Skip parameters shown in high impact section
                    skip = False
                    if "parameter_analysis" in mod:
                        for change in mod["parameter_analysis"]["high_impact"]:
                            if param == change["parameter"]:
                                skip = True
                                break

                        # Also skip parameters that are part of version migrations
                        if not skip:
                            for migration in mod["parameter_analysis"][
                                "version_migrations"
                            ]:
                                if (
                                    param in migration["old_params"]
                                    or param in migration["new_params"]
                                ):
                                    skip = True
                                    break

                        # Skip parameters in list changes
                        if not skip and param in mod["parameter_analysis"].get(
                            "list_changes", {}
                        ):
                            skip = True

                    if not skip:
                        if diff["change"] == "added":
                            html.append(
                                f"<tr><td>{param}</td><td class='added'>Added</td><td>-</td><td>{diff['value']}</td></tr>"
                            )
                        elif diff["change"] == "removed":
                            html.append(
                                f"<tr><td>{param}</td><td class='removed'>Removed</td><td>{diff['value']}</td><td>-</td></tr>"
                            )
                        elif diff["change"] == "modified":
                            # Check if this is a metadata-only change
                            if "metadata_change" in diff and diff["metadata_change"]:
                                metadata_diff = diff["metadata_change"]
                                if not metadata_diff["base_changed"]:
                                    html.append(
                                        f"<tr class='metadata-change'><td>{param}</td><td class='modified'>Metadata Only</td><td colspan='2'>{metadata_diff['description']}</td></tr>"
                                    )
                                else:
                                    html.append(
                                        f"<tr><td>{param}</td><td class='modified'>Modified*</td><td>{diff['from']}</td><td>{diff['to']}</td></tr>"
                                    )
                            else:
                                html.append(
                                    f"<tr><td>{param}</td><td class='modified'>Modified</td><td>{diff['from']}</td><td>{diff['to']}</td></tr>"
                                )
                html.append("</table>")
                html.append("</details>")

        html.append("</body></html>")
        return "\n".join(html)

    else:
        return json.dumps(diff_result, indent=2)


def compare_metadata_patterns(value1, value2):
    """Compare two strings containing metadata patterns and report differences"""
    # Extract metadata references
    pattern = r"\\g<([^>]+)>"
    refs1 = set(re.findall(pattern, str(value1)))
    refs2 = set(re.findall(pattern, str(value2)))

    added = refs2 - refs1
    removed = refs1 - refs2

    # Get the base content by removing metadata patterns
    base1 = re.sub(pattern, "", str(value1))
    base2 = re.sub(pattern, "", str(value2))

    result = {
        "changed": len(added) > 0 or len(removed) > 0,
        "base_changed": base1.strip() != base2.strip(),
        "added_refs": list(added),
        "removed_refs": list(removed),
        "description": "",
    }

    if result["changed"]:
        result["description"] = (
            f"Metadata references changed: -{', '.join(removed)} +{', '.join(added)}"
        )

    return result


def main():
    parser = argparse.ArgumentParser(description="Compare CellProfiler pipelines")
    parser.add_argument("pipeline1", help="Path to first pipeline")
    parser.add_argument("pipeline2", help="Path to second pipeline")
    parser.add_argument(
        "--format",
        choices=["text", "html", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    pipeline1 = parse_cppipe(args.pipeline1)
    pipeline2 = parse_cppipe(args.pipeline2)

    diff_result = compare_pipelines(pipeline1, pipeline2)
    report = generate_report(diff_result, format=args.format)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
    else:
        print(report)


if __name__ == "__main__":
    main()
