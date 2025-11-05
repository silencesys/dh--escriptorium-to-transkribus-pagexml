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

No installation needed — this is a small Python script. Requires Python 3.6+.

```bash
# Clone the repository
git clone https://github.com/Aidee1996/escriptorium-to-transkribus-pagexml.git
cd escriptorium-to-transkribus-pagexml

# Show help
python convert_pagexml.py -h
```

## Usage (CLI)

The script is now a command-line tool. Use either `-f/--file` to convert a single PAGE XML file or
`-d/--directory` to convert all `.xml` files in a folder. Use `-o/--output` to control output paths.

Flags
- `-f, --file` — Path to a single PAGE XML file to convert.
- `-d, --directory` — Path to a directory containing PAGE XML files to convert.
- `-o, --output` — Optional output file or directory. Behavior:
	- For single-file conversion:
		- `-o` (no value) or `-o _auto` — auto-generate an output file by appending `_transkribus` to the input filename (same folder).
		- `-o /path/to/outdir/` or `-o outdir` — treat as output directory (created if needed) and write `<stem>_transkribus.xml` inside it.
		- `-o /path/to/output.xml` — treat as explicit output file path.
	- For directory conversion:
		- `-o` (no value) — create a `transkribus_converted` folder next to the input directory and write outputs there.
		- `-o /path/to/output_dir/` — use that output directory (created if needed).
- `-v, --verbose` — Print extra information (for example, when the output directory is created).

Notes about `-o` heuristics
- If `-o` is a path that does not exist and has no file extension, the script treats it as a directory and creates it.
- If you want to force an output file without extension, provide a trailing slash to make your intention explicit.

Examples

Single file, auto-generate output (append `_transkribus`):
```bash
python convert_pagexml.py -f /path/to/input.xml
```

Single file, explicit output file:
```bash
python convert_pagexml.py -f /path/to/input.xml -o /path/to/output.xml
```

Single file, output into a directory (created if needed):
```bash
python convert_pagexml.py -f /path/to/input.xml -o /path/to/output_dir/
```

Batch convert a directory into a specific output folder:
```bash
python convert_pagexml.py -d /path/to/input_dir -o /path/to/output_dir/
```

For full help and all options, run:

```bash
python convert_pagexml.py -h
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