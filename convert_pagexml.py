#!/usr/bin/env python3
"""
PAGE XML Converter: eScriptorium to Transkribus
================================================

Converts PAGE XML files from eScriptorium/Kraken format to Transkribus-compatible format.

⚠️ IMPORTANT: REGEX-BASED APPROACH ⚠️
=====================================
This script uses REGULAR EXPRESSIONS to manipulate XML as text strings.
This approach has limitations and may fail on certain edge cases:

KNOWN LIMITATIONS:
- May fail if attribute values contain '>' characters
- May fail with self-closing tags (e.g., <TextRegion/>)
- May fail with namespace prefixes (e.g., <pc:TextRegion>)
- May produce invalid XML in edge cases

WHY REGEX ANYWAY?
- Simple and fast for well-formed, predictable input
- No external dependencies (no lxml required)
- Works perfectly for standard eScriptorium exports
- Easy to understand and modify

WHEN TO USE THIS SCRIPT:
✓ Standard eScriptorium PAGE XML exports
✓ Files you control and know are well-formed
✓ Quick batch conversions of known-good files

WHEN NOT TO USE:
✗ XML files from unknown sources
✗ Files with unusual formatting or attributes
✗ Production systems requiring 100% reliability
✗ Files that might have special characters in attributes

For a more robust solution, consider using lxml-based XML parsing.
See test_lxml_approach.py for comparison.

WHAT THIS SCRIPT DOES:
======================
1. Updates schema version from 2019-07-15 to 2013-07-15
2. Cleans and rebuilds namespace declarations
3. Fixes empty Unicode elements (adds [text] placeholder)
4. Adds missing Coords elements (required by Transkribus)
5. Adds missing Baseline elements (expected by Transkribus)

TECHNICAL CHANGES:
==================
- Namespace: Updates to http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15
- Empty <Unicode/> → <Unicode>[text]</Unicode>
- Missing <Coords> → Adds placeholder coordinates
- Missing <Baseline> → Adds placeholder baseline points
"""

import re
import os
import argparse
from pathlib import Path


def convert_page_xml(input_file, output_file=None):
    """
    Convert PAGE XML from eScriptorium to Transkribus format using regex text replacement.

    ⚠️ WARNING: This function uses REGEX to manipulate XML as text.
    It works well for standard eScriptorium exports but may fail on edge cases.
    See module docstring for known limitations.

    Args:
        input_file (str): Path to input PAGE XML file (eScriptorium format)
        output_file (str): Path to output file (optional, auto-generated if not provided)

    Returns:
        bool: True if conversion succeeded, False otherwise

    Conversions performed (using REGEX):
    - Schema version: 2019-07-15 → 2013-07-15
    - Namespace: Cleaned and set to 2013-07-15 version
    - Empty Unicode elements: Filled with [text] placeholder
    - Missing Coords: Added with default placeholder values
    - Missing Baseline: Added with default placeholder values

    Example:
        >>> convert_page_xml("input.xml", "output.xml")
        Successfully converted: input.xml → output.xml
        True
    """

    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_transkribus{input_path.suffix}"

    try:
        # Read the file as plain text (REGEX APPROACH - not XML parsing)
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # === REGEX-BASED TRANSFORMATIONS ===
        # All modifications below use regular expressions on text strings
        # This is fast but has limitations (see module docstring)

        # 1. Change schema version from 2019 to 2013 (simple text replacement)
        content = content.replace('2019-07-15', '2013-07-15')

        # 2. Clean up namespace declarations completely and rebuild
        #    REGEX: Remove all xmlns and xsi declarations
        content = re.sub(r'\s*xmlns(?::[^=]*)?="[^"]*"', '', content)
        content = re.sub(r'\s*xsi:[^=]*="[^"]*"', '', content)

        # 3. Rebuild PcGts element with clean namespace
        #    REGEX: Find <PcGts and replace with standardized version
        content = re.sub(
            r'<PcGts([^>]*)>',
            '<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">',
            content
        )

        # 4. Fix empty Unicode elements - add meaningful placeholders
        #    REGEX: Match various forms of empty Unicode elements
        #    Transkribus may expect content in Unicode elements
        content = re.sub(r'<Unicode\s*/>', '<Unicode>[text]</Unicode>', content)
        content = re.sub(r'<Unicode></Unicode>', '<Unicode>[text]</Unicode>', content)
        content = re.sub(r'<Unicode>\s*</Unicode>', '<Unicode>[text]</Unicode>', content)
        content = re.sub(r'<Unicode>\s+</Unicode>', '<Unicode>[text]</Unicode>', content)

        # 5. Fix missing Coords elements - Transkribus requires them
        #    REGEX: Use negative lookahead to find tags without Coords children
        #    ⚠️ WARNING: This regex may fail if tag spans multiple lines or has unusual formatting

        # Add minimal coords for TextRegions without them
        content = re.sub(
            r'(<TextRegion[^>]*>)(?!\s*<Coords)',
            r'\1\n<Coords points="0,0 100,0 100,100 0,100"/>',
            content
        )

        # Add minimal coords for TextLines without them
        content = re.sub(
            r'(<TextLine[^>]*>)(?!\s*<Coords)',
            r'\1\n<Coords points="0,0 100,0 100,20 0,20"/>',
            content
        )

        # 6. Ensure every TextLine has a Baseline (Transkribus expects it)
        #    REGEX: Find TextLine with Coords but no Baseline
        content = re.sub(
            r'(<TextLine[^>]*>\s*<Coords[^>]*/>)(?!\s*<Baseline)',
            r'\1\n<Baseline points="0,10 100,10"/>',
            content
        )

        # 7. Clean up extra whitespace (cosmetic)
        content = re.sub(r'\s+>', '>', content)
        content = re.sub(r'>\s+<', '><', content)

        # Write the transformed content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully converted: {input_file} → {output_file}")
        return True

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return False
    except PermissionError:
        print(f"Error: Permission denied: {input_file}")
        return False
    except Exception as e:
        print(f"Error converting file: {e}")
        return False


def process_directory(input_dir, output_dir=None):
    """
    Process all PAGE XML files in a directory using regex-based conversion.

    ⚠️ WARNING: Uses REGEX approach. See convert_page_xml() for limitations.

    Args:
        input_dir (str): Directory containing PAGE XML files
        output_dir (str): Output directory (optional, auto-generated if not provided)

    Example:
        >>> process_directory("/path/to/xml/files", "/path/to/output")
        Processed 15/15 files successfully
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Input directory does not exist: {input_dir}")
        return

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path / "transkribus_converted"
        output_path.mkdir(exist_ok=True)

    xml_files = list(input_path.glob("*.xml"))
    if not xml_files:
        print(f"No XML files found in: {input_dir}")
        return

    success_count = 0
    for xml_file in xml_files:
        output_file = output_path / f"{xml_file.stem}_transkribus.xml"
        if convert_page_xml(str(xml_file), str(output_file)):
            success_count += 1

    print(f"\nProcessed {success_count}/{len(xml_files)} files successfully")


def welcome_message():
    """Print a friendly welcome message and short usage examples."""
    print("=" * 70)
    print("PAGE XML Converter: eScriptorium → Transkribus")
    print("Convert PAGE XML files exported from eScriptorium (regex-based).")
    print("⚠️  REGEX-BASED TRANSFORMATIONS — see module docstring for limitations")
    print("=" * 70)
    print()
    print("Usage examples:")
    print("  Convert single file and auto-generate output (append _transkribus):")
    print("    python convert_pagexml.py -f /path/to/input.xml -o")
    print()
    print("  Convert single file and write to a specific output file:")
    print("    python convert_pagexml.py -f /path/to/input.xml -o /path/to/output.xml")
    print()
    print("  Convert a directory of XML files and write to a specific output directory:")
    print("    python convert_pagexml.py -d /path/to/input_dir -o /path/to/output_dir/")
    print()
    print("Options:")
    print("  -f, --file       Path to a single PAGE XML file")
    print("  -d, --directory  Path to a directory containing PAGE XML files")
    print("  -o, --output     Output file or directory. Use trailing slash or no extension to force directory creation.")
    print("  -v, --verbose    Print extra information while running")
    print()
    print("For full help, run: python convert_pagexml.py -h")
    print()





def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert PAGE XML from eScriptorium to Transkribus format (regex-based)."
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-f", "--file", dest="file", help="Path to a single PAGE XML file to convert")
    group.add_argument("-d", "--directory", dest="directory", help="Path to a directory containing PAGE XML files to convert")

    # -o/--o flag: if provided without value, auto-generate filename by appending _transkribus
    # If provided with a value, treat that as an output file (for single file) or output directory (for directory)
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        nargs="?",
        const="_auto",
        help=(
            "Output file or directory. For single-file conversion: if omitted, no output file is written;"
            " if provided without value, an output file is created by appending '_transkribus' to the filename;"
            " if provided with a path, that path is used as the output file. For directory conversion:"
            " if provided with a path, it's used as the output directory; if provided without value, a 'transkribus_converted'"
            " folder is created next to the input directory."
        ),
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # If no args supplied, show a friendly welcome message with examples
    if not args.file and not args.directory:
        welcome_message()
        return

    if args.file:
        input_path = Path(args.file)
        if not input_path.exists():
            print(f"Error: input file does not exist: {args.file}")
            return

        # Determine output handling
        if args.output is None:
            # No -o provided: use existing convert function behavior (it will auto-generate and write)
            # We call convert_page_xml with no output_file to let it auto-generate the _transkribus name.
            convert_page_xml(str(input_path), None)
            return

        if args.output == "_auto":
            # auto-generate output filename by appending _transkribus
            output_file = input_path.parent / f"{input_path.stem}_transkribus{input_path.suffix}"
            convert_page_xml(str(input_path), str(output_file))
            return

        # args.output provided as a path
        out_path = Path(args.output)
        # If out_path is an existing directory, ensure it exists and create output inside it
        if out_path.exists() and out_path.is_dir():
            # directory exists — ensure parents exist (no-op) and place file inside
            out_path.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Using existing output directory: {out_path}")
            output_file = out_path / f"{input_path.stem}_transkribus{input_path.suffix}"
        # If user passed a path that ends with a path separator, treat it as a directory and create it
        elif args.output.endswith(os.path.sep) or args.output.endswith("/"):
            out_path.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created output directory: {out_path}")
            output_file = out_path / f"{input_path.stem}_transkribus{input_path.suffix}"
        # If the path doesn't exist and has no suffix (no extension), treat as directory by heuristic
        elif not out_path.exists() and out_path.suffix == "":
            out_path.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created output directory (no-extension heuristic): {out_path}")
            output_file = out_path / f"{input_path.stem}_transkribus{input_path.suffix}"
        else:
            # Treat as file path (may not exist yet)
            output_file = out_path

        convert_page_xml(str(input_path), str(output_file))
        return

    if args.directory:
        input_dir = Path(args.directory)
        if not input_dir.exists() or not input_dir.is_dir():
            print(f"Error: input directory does not exist or is not a directory: {args.directory}")
            return

        # Determine output directory
        if args.output is None:
            # no -o provided: create default transkribus_converted inside input dir
            process_directory(str(input_dir), None)
            return

        if args.output == "_auto":
            # use default name next to input dir
            process_directory(str(input_dir), None)
            return

        # args.output provided as a path
        out_dir = Path(args.output)
        # If out_dir looks like a directory (exists or ends with separator), ensure it exists
        if out_dir.exists() and out_dir.is_dir():
            out_dir.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Using existing output directory: {out_dir}")
        elif args.output.endswith(os.path.sep) or args.output.endswith("/"):
            out_dir.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created output directory: {out_dir}")
        # Heuristic: if path doesn't exist and has no suffix, treat as a directory
        elif not out_dir.exists() and out_dir.suffix == "":
            out_dir.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created output directory (no-extension heuristic): {out_dir}")

        process_directory(str(input_dir), str(out_dir))


# Run conversion when script is executed directly
if __name__ == "__main__":
    main()
