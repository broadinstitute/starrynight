import argparse
import json
import re
from collections import defaultdict


def parse_cppipe(filepath):
    """Parse a CellProfiler pipeline into structured data"""
    with open(filepath, "r") as f:
        content = f.read()

    # Parse header
    header_match = re.search(
        r"(CellProfiler Pipeline.*?)ModuleCount:", content, re.DOTALL
    )
    header = header_match.group(1) if header_match else ""

    # Extract modules
    modules = []
    module_blocks = re.findall(
        r"(\w+):\[module_num:(\d+)\|.*?enabled:(True|False).*?\](.*?)(?=\w+:\[module_num|\Z)",
        content,
        re.DOTALL,
    )

    for module_type, module_num, enabled, params in module_blocks:
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
                "enabled": enabled == "True",
                "parameters": parameters,
            }
        )

    return {"header": header, "modules": modules}


def extract_channels(pipeline):
    """Identify channels used in the pipeline"""
    channels = set()

    # Look for channel patterns in image names
    for module in pipeline["modules"]:
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


def compare_pipelines(pipeline1, pipeline2, enabled_only=True):
    """Compare two parsed pipelines and return structured differences"""
    result = {
        "header_changes": {},
        "module_count_diff": pipeline2["module_count"] - pipeline1["module_count"]
        if "module_count" in pipeline1 and "module_count" in pipeline2
        else None,
        "channels": {"added": [], "removed": [], "common": []},
        "module_changes": {"added": [], "removed": [], "modified": []},
        "channel_processing": {},
    }

    # Extract channels
    channels1 = extract_channels(pipeline1)
    channels2 = extract_channels(pipeline2)

    result["channels"]["added"] = list(channels2 - channels1)
    result["channels"]["removed"] = list(channels1 - channels2)
    result["channels"]["common"] = list(channels1 & channels2)

    # Filter enabled modules if requested
    modules1 = [m for m in pipeline1["modules"] if not enabled_only or m["enabled"]]
    modules2 = [m for m in pipeline2["modules"] if not enabled_only or m["enabled"]]

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
                    param_diffs = []
                    for m1, m2 in zip(mods1, mods2):
                        for param in set(m1["parameters"].keys()) | set(
                            m2["parameters"].keys()
                        ):
                            if param not in m1["parameters"]:
                                param_diffs.append(f"{m1['type']} added param: {param}")
                            elif param not in m2["parameters"]:
                                param_diffs.append(
                                    f"{m1['type']} removed param: {param}"
                                )
                            elif m1["parameters"][param] != m2["parameters"][param]:
                                param_diffs.append(
                                    f"{m1['type']} changed {param}: {m1['parameters'][param]} → {m2['parameters'][param]}"
                                )

                    if param_diffs:
                        result["channel_processing"][channel] = (
                            f"changed parameters ({len(param_diffs)} differences)"
                        )
                    else:
                        result["channel_processing"][channel] = "unchanged"

    # Create module signatures for better comparison
    def create_module_signature(module):
        key_params = {
            k: v
            for k, v in module["parameters"].items()
            if k in ["Select the input image", "Name the output image"]
        }
        return (module["type"], frozenset(key_params.items()))

    modules1_sigs = {create_module_signature(m): m for m in modules1}
    modules2_sigs = {create_module_signature(m): m for m in modules2}

    # Find added and removed modules
    for sig, module in modules2_sigs.items():
        if sig not in modules1_sigs:
            result["module_changes"]["added"].append(
                {
                    "type": module["type"],
                    "module_num": module["module_num"],
                    "channel": get_module_processing_channel(module),
                    "key_params": dict([p for p in sig[1]]),
                }
            )

    for sig, module in modules1_sigs.items():
        if sig not in modules2_sigs:
            result["module_changes"]["removed"].append(
                {
                    "type": module["type"],
                    "module_num": module["module_num"],
                    "channel": get_module_processing_channel(module),
                    "key_params": dict([p for p in sig[1]]),
                }
            )

    # Compare common modules
    for sig in set(modules1_sigs.keys()) & set(modules2_sigs.keys()):
        m1 = modules1_sigs[sig]
        m2 = modules2_sigs[sig]

        # Compare all parameters
        param_diffs = {}
        for param in set(m1["parameters"].keys()) | set(m2["parameters"].keys()):
            if param not in m1["parameters"]:
                param_diffs[param] = {
                    "change": "added",
                    "value": m2["parameters"][param],
                }
            elif param not in m2["parameters"]:
                param_diffs[param] = {
                    "change": "removed",
                    "value": m1["parameters"][param],
                }
            elif m1["parameters"][param] != m2["parameters"][param]:
                param_diffs[param] = {
                    "change": "modified",
                    "from": m1["parameters"][param],
                    "to": m2["parameters"][param],
                }

        if param_diffs:
            result["module_changes"]["modified"].append(
                {
                    "type": m1["type"],
                    "from_module_num": m1["module_num"],
                    "to_module_num": m2["module_num"],
                    "channel": get_module_processing_channel(m1),
                    "parameter_diffs": param_diffs,
                }
            )

    return result


def generate_report(diff_result, format="text"):
    """Generate a human-readable diff report"""
    if format == "text":
        report = []

        # Channel summary
        report.append("=== CHANNEL SUMMARY ===")
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
                report.append(
                    f"* {mod['type']} (Module {mod['from_module_num']} → {mod['to_module_num']}, Channel: {mod['channel'] or 'unknown'})"
                )
                for param, diff in mod["parameter_diffs"].items():
                    if diff["change"] == "added":
                        report.append(f"  + {param}: {diff['value']}")
                    elif diff["change"] == "removed":
                        report.append(f"  - {param}: {diff['value']}")
                    else:
                        report.append(f"  * {param}: {diff['from']} → {diff['to']}")

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
            "table { border-collapse: collapse; width: 100%; }",
            "table, th, td { border: 1px solid #ddd; }",
            "th, td { padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "tr:nth-child(even) { background-color: #f9f9f9; }",
            "h2 { color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; }",
            "</style>",
            "<title>CellProfiler Pipeline Diff</title>",
            "</head>",
            "<body>",
            "<h1>CellProfiler Pipeline Diff Report</h1>",
        ]

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
            html.append(f"<tr><td>{channel}</td><td>{status}</td></tr>")
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
                    f"<tr><td>{mod['module_num']}</td><td>{mod['type']}</td><td>{mod['channel'] or 'unknown'}</td><td>{params}</td></tr>"
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
                    f"<tr><td>{mod['module_num']}</td><td>{mod['type']}</td><td>{mod['channel'] or 'unknown'}</td><td>{params}</td></tr>"
                )
            html.append("</table>")

        if diff_result["module_changes"]["modified"]:
            html.append("<h2>Modified Modules</h2>")
            for mod in diff_result["module_changes"]["modified"]:
                html.append(
                    f"<h3>{mod['type']} (Module {mod['from_module_num']} → {mod['to_module_num']}, Channel: {mod['channel'] or 'unknown'})</h3>"
                )
                html.append("<table>")
                html.append(
                    "<tr><th>Parameter</th><th>Change</th><th>From</th><th>To</th></tr>"
                )
                for param, diff in mod["parameter_diffs"].items():
                    if diff["change"] == "added":
                        html.append(
                            f"<tr><td>{param}</td><td class='added'>Added</td><td>-</td><td>{diff['value']}</td></tr>"
                        )
                    elif diff["change"] == "removed":
                        html.append(
                            f"<tr><td>{param}</td><td class='removed'>Removed</td><td>{diff['value']}</td><td>-</td></tr>"
                        )
                    else:
                        html.append(
                            f"<tr><td>{param}</td><td class='modified'>Modified</td><td>{diff['from']}</td><td>{diff['to']}</td></tr>"
                        )
                html.append("</table>")

        html.append("</body></html>")
        return "\n".join(html)

    else:
        return json.dumps(diff_result, indent=2)


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
    parser.add_argument(
        "--enabled-only", action="store_true", help="Only compare enabled modules"
    )
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    pipeline1 = parse_cppipe(args.pipeline1)
    pipeline2 = parse_cppipe(args.pipeline2)

    diff_result = compare_pipelines(
        pipeline1, pipeline2, enabled_only=args.enabled_only
    )
    report = generate_report(diff_result, format=args.format)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
    else:
        print(report)


if __name__ == "__main__":
    main()
