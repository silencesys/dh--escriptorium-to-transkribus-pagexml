#!/usr/bin/env python3
"""
Demonstration of lxml approach handling edge cases correctly
"""
from lxml import etree

def lxml_approach(xml_string):
    """Parse and modify XML properly"""
    # Parse the XML
    root = etree.fromstring(xml_string.encode('utf-8'))

    # Find all TextRegion elements (namespace-aware)
    # This works with any namespace prefix
    for elem in root.iter():
        if elem.tag.endswith('TextRegion'):
            # Check if Coords already exists
            has_coords = False
            for child in elem:
                if child.tag.endswith('Coords'):
                    has_coords = True
                    break

            # Add Coords if missing
            if not has_coords:
                # Create new element with same namespace as parent
                ns = elem.tag.split('}')[0] + '}' if '}' in elem.tag else ''
                coords = etree.Element(f"{ns}Coords")
                coords.set('points', '0,0 100,0 100,100 0,100')
                # Insert as first child
                elem.insert(0, coords)

    # Return formatted XML
    return etree.tostring(root, pretty_print=True, encoding='unicode')

# Test on the breaking cases
test_cases = {
    "greater_than_in_attribute": """<TextRegion id="region_1" custom="value&gt;with&gt;greaterthan">
  <TextLine>text</TextLine>
</TextRegion>""",

    "self_closing_textregion": """<root><TextRegion id="region_1"/></root>""",

    "namespace_prefix": """<pc:TextRegion xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15" id="region_1">
  <pc:TextLine>text</pc:TextLine>
</pc:TextRegion>""",
}

print("=" * 80)
print("LXML APPROACH - HANDLES EDGE CASES CORRECTLY")
print("=" * 80)

for name, xml in test_cases.items():
    print(f"\n{'='*80}")
    print(f"Test case: {name}")
    print(f"{'='*80}")
    print("INPUT:")
    print(xml)
    print("\nOUTPUT:")
    try:
        result = lxml_approach(xml)
        print(result)

        # Verify it's valid XML
        etree.fromstring(result.encode('utf-8'))
        print("✓ Valid XML")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    print()
