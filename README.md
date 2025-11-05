# escriptorium-to-transkribus-pagexml

Convert PAGE XML files from eScriptorium/Kraken format to Transkribus-compatible format.

## ⚠️ Important: REGEX-Based Approach

**This tool uses REGULAR EXPRESSIONS to manipulate XML as text strings.**

### Why Regex?
- ✅ Simple and fast for standard eScriptorium exports
- ✅ No external dependencies (no lxml required)
- ✅ Easy to understand and modify
- ✅ Works perfectly for well-formed, predictable input

### Known Limitations
- ⚠️ May fail if attribute values contain `>` characters
- ⚠️ May fail with self-closing tags (e.g., `<TextRegion/>`)
- ⚠️ May fail with namespace prefixes (e.g., `<pc:TextRegion>`)
- ⚠️ May produce invalid XML in rare edge cases

### When to Use This Tool
- ✓ Standard eScriptorium PAGE XML exports
- ✓ Files you control and know are well-formed
- ✓ Quick batch conversions of known-good files

### When NOT to Use
- ✗ XML files from unknown sources
- ✗ Files with unusual formatting or special characters in attributes
- ✗ Production systems requiring 100% reliability

For comparison with a more robust lxml-based approach, see `test_lxml_approach.py`.

## What It Does

This script converts PAGE XML files by making the following changes:

1. **Schema Version**: Updates from `2019-07-15` to `2013-07-15`
2. **Namespace**: Sets to `http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15`
3. **Unicode Elements**: Fills empty `<Unicode/>` with `[text]` placeholder
4. **Coords Elements**: Adds placeholder coordinates where missing (Transkribus requirement)
5. **Baseline Elements**: Adds placeholder baselines where missing (Transkribus expectation)

## Installation

No installation needed! Just Python 3.6+

```bash
# Clone the repository
git clone https://github.com/Aidee1996/escriptorium-to-transkribus-pagexml.git
cd escriptorium-to-transkribus-pagexml

# Run the script
python convert_pagexml.py
```

## Usage

### Simple Usage (Recommended)

1. Open `convert_pagexml.py` in a text editor
2. Find these lines near the bottom:

```python
# Option 1: Convert single file
input_file = r"C:\path\to\your\file.xml"
output_file = r"C:\path\to\output\file.xml"

# Option 2: Convert entire folder
input_folder = r"C:\path\to\xml\files"
output_folder = r"C:\path\to\output\folder"
```

3. Change the paths to your files/folders
4. Run: `python convert_pagexml.py`

### Programmatic Usage

```python
from convert_pagexml import convert_page_xml, process_directory

# Convert single file
convert_page_xml("input.xml", "output.xml")

# Convert entire directory
process_directory("input_folder", "output_folder")
```

## Examples

### Single File Conversion
```bash
$ python convert_pagexml.py
Converting file: my_manuscript.xml
Successfully converted: my_manuscript.xml → my_manuscript_transkribus.xml
✅ File conversion completed!
```

### Batch Directory Conversion
```bash
$ python convert_pagexml.py
Converting folder: /path/to/manuscripts
Successfully converted: page_001.xml → page_001_transkribus.xml
Successfully converted: page_002.xml → page_002_transkribus.xml
...
Processed 50/50 files successfully
✅ Folder conversion completed!
```

## Testing

Run the included test files to see how the regex approach handles edge cases:

```bash
# See where regex works well
python test_regex_edge_cases.py

# See critical cases where regex can fail
python test_regex_real_breaks.py

# Compare with lxml approach
python test_lxml_approach.py
```

## Format Differences

### eScriptorium (2019-07-15 schema)
- May use newer schema version
- May have empty `<Unicode/>` elements
- May have missing `<Coords>` or `<Baseline>` elements
- May have different namespace declarations

### Transkribus (2013-07-15 schema)
- Requires 2013-07-15 schema version
- Expects content in Unicode elements
- Requires Coords elements for regions
- Expects Baseline elements for text lines

## Troubleshooting

### "Invalid XML" errors
If you get XML parsing errors in Transkribus:
1. Check if your input file has special characters in attributes
2. Try the lxml-based approach (see `test_lxml_approach.py`)
3. Manually validate the output XML

### Missing or incorrect coordinates
The script adds placeholder coordinates (e.g., `0,0 100,0 100,100 0,100`) when they're missing. You may need to:
1. Export from eScriptorium with proper coordinates
2. Manually adjust coordinates in Transkribus
3. Re-segment in Transkribus if needed

## Contributing

Contributions welcome! Please note that this project intentionally uses a regex-based approach for simplicity. If proposing changes:
- Keep the regex approach for the main script
- Add edge case handling where possible
- Document any new limitations discovered

## License

MIT License - see LICENSE file for details

## References

- [PAGE XML Format](https://github.com/PRImA-Research-Lab/PAGE-XML)
- [eScriptorium](https://escriptorium.readthedocs.io/)
- [Transkribus](https://readcoop.eu/transkribus/)

---

**Note**: This is a pragmatic tool designed for specific use cases. For production systems or untrusted input, consider using proper XML parsing libraries like lxml