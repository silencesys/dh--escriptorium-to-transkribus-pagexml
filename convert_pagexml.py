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


# =============================================================================
# SIMPLE USAGE - Only change these paths:
# =============================================================================

# Option 1: Convert single file
input_file = r"C:\Users\annam\Dropbox\escriptorium-to-transkribus-pagexml\prepisy-z-escriptoria\20230620_151509.xml"  # Change to your path
output_file = r"C:\Users\annam\Dropbox\escriptorium-to-transkribus-pagexml\prepisy-z-escriptoria\20230620_151509_transkribus.xml"

# Option 2: Convert entire folder
input_folder = r"C:\path\to\xml\files"  # Change to your path
output_folder = r"C:\path\to\output\folder"

# =============================================================================


def easy_convert():
    """
    Simple conversion function - just configure paths above and run!

    This is a convenience wrapper that checks for files/folders and runs conversion.
    For programmatic use, call convert_page_xml() or process_directory() directly.
    """

    print("=" * 70)
    print("PAGE XML Converter: eScriptorium → Transkribus")
    print("⚠️  REGEX-BASED APPROACH - See script header for limitations")
    print("=" * 70)
    print()

    # Try to convert single file first
    if os.path.exists(input_file):
        print(f"Converting file: {input_file}")
        if convert_page_xml(input_file, output_file):
            print("✅ File conversion completed!")
        else:
            print("❌ Error during file conversion")
        return

    # If file doesn't exist, try folder
    if os.path.exists(input_folder):
        print(f"Converting folder: {input_folder}")
        process_directory(input_folder, output_folder)
        print("✅ Folder conversion completed!")
        return

    # If neither exists, show instructions
    print("❌ File or folder does not exist!")
    print()
    print("📝 INSTRUCTIONS:")
    print("1. Find the lines above marked 'input_file' and 'input_folder'")
    print("2. Change the paths to your actual files/folders")
    print("3. Run again: python convert_pagexml.py")
    print()
    print("💡 Example path: r'C:\\Users\\Name\\Desktop\\my_file.xml'")


# Run conversion when script is executed directly
if __name__ == "__main__":
    easy_convert()
