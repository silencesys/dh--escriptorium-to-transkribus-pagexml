#!/usr/bin/env python3
"""
Test to demonstrate REAL breaking cases for regex
"""
import re

def regex_approach(content):
    content = re.sub(r'(<TextRegion[^>]*>)(?!\s*<Coords)', r'\1\n<Coords points="0,0 100,0 100,100 0,100"/>', content)
    return content

# Critical breaking cases
test_cases = {
    "greater_than_in_attribute": """<TextRegion id="region_1" custom="value>with>greaterthan">
  <TextLine>text</TextLine>
</TextRegion>""",

    "self_closing_textregion": """<TextRegion id="region_1"/>""",

    "textregion_in_string": """<SomeElement>
  <Description>This text mentions &lt;TextRegion&gt; as an example</Description>
  <TextRegion id="region_1">
    <TextLine>text</TextLine>
  </TextRegion>
</SomeElement>""",

    "regex_special_chars": """<TextRegion id="region_1" pattern=".*test[0-9]+">
  <TextLine>text</TextLine>
</TextRegion>""",

    "namespace_prefix": """<pc:TextRegion xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15" id="region_1">
  <pc:TextLine>text</pc:TextLine>
</pc:TextRegion>""",
}

print("=" * 80)
print("CRITICAL BREAKING CASES")
print("=" * 80)

for name, xml in test_cases.items():
    print(f"\n{'='*80}")
    print(f"Test case: {name}")
    print(f"{'='*80}")
    print("INPUT:")
    print(xml)
    print("\nOUTPUT:")
    try:
        result = regex_approach(xml)
        print(result)

        # Try to parse as XML to see if it's still valid
        from xml.etree import ElementTree as ET
        try:
            ET.fromstring(result)
            print("\n✓ Valid XML")
        except ET.ParseError as e:
            print(f"\n✗ INVALID XML: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
