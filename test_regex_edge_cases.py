#!/usr/bin/env python3
"""
Test to demonstrate where regex approach fails
"""
import re

# Your current regex approach
def regex_approach(content):
    content = re.sub(r'(<TextRegion[^>]*>)(?!\s*<Coords)', r'\1\n<Coords points="0,0 100,0 100,100 0,100"/>', content)
    return content

# Test cases
test_cases = {
    "simple": """<TextRegion id="region_1">
  <TextLine>text</TextLine>
</TextRegion>""",

    "multiline_tag": """<TextRegion
    id="region_1"
    type="paragraph">
  <TextLine>text</TextLine>
</TextRegion>""",

    "comment": """<TextRegion id="region_1">
  <!-- This is a comment -->
  <TextLine>text</TextLine>
</TextRegion>""",

    "already_has_coords": """<TextRegion id="region_1">
  <Coords points="10,10 20,20"/>
  <TextLine>text</TextLine>
</TextRegion>""",

    "nested": """<TextRegion id="outer">
  <TextRegion id="inner">
    <TextLine>text</TextLine>
  </TextRegion>
</TextRegion>""",
}

print("=" * 80)
print("TESTING REGEX APPROACH ON EDGE CASES")
print("=" * 80)

for name, xml in test_cases.items():
    print(f"\n{'='*80}")
    print(f"Test case: {name}")
    print(f"{'='*80}")
    print("INPUT:")
    print(xml)
    print("\nOUTPUT:")
    result = regex_approach(xml)
    print(result)
    print()
