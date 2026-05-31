import re
from datetime import date

SVG_FILE = "streak-card.svg"

today = date.today()
date_str = today.strftime("%b %-d")   # e.g. "May 31"

with open(SVG_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ── helper: find a number right before a label and increment it ──────────────

def increment_near_label(svg, label, group="LEFT"):
    """
    Finds the LAST standalone integer that appears before `label` in the SVG
    text and returns the svg with that number incremented by 1.
    """
    # Match something like:  17\n    <animate ...
    # inside a <text> block that precedes the label
    pattern = re.compile(
        r'(<text[^>]*>[^<]*?)(\b(\d+)\b)([^<]*<animate[^/]*/>\s*</text>)',
        re.DOTALL
    )
    matches = list(pattern.finditer(svg))
    return svg

# ── 1. CURRENT STREAK — the big number inside the ring ───────────────────────
#    Looks like:   <text ... font-size="36" ...>
#                    1
#                    <animate .../>
#                  </text>

def bump(svg, font_size):
    """Increment the integer inside a <text> block that has the given font-size."""
    pattern = re.compile(
        r'(font-size="' + str(font_size) + r'"[^>]*>)\s*(\d+)\s*(\n\s*<animate)',
        re.DOTALL
    )
    def replacer(m):
        new_val = int(m.group(2)) + 1
        return m.group(1) + f"\n    {new_val}" + m.group(3)
    return pattern.sub(replacer, svg)

# Current streak  → font-size="36"
content = bump(content, 36)

# Total contributions → font-size="52"  (left panel)
# We only want the LEFT one; both 52-px texts exist so we patch the first match
pattern52 = re.compile(
    r'(font-size="52"[^>]*>)\s*(\d+)\s*(\n\s*<animate)',
    re.DOTALL
)
matches52 = list(pattern52.finditer(content))
if matches52:
    m = matches52[0]          # first = total contributions
    new_val = int(m.group(2)) + 1
    replacement = m.group(1) + f"\n    {new_val}" + m.group(3)
    content = content[:m.start()] + replacement + content[m.end():]

# ── 2. Longest streak — only update when current streak exceeds it ────────────
# Extract current streak value after bump
cs_match = re.search(r'font-size="36"[^>]*>\s*(\d+)', content)
ls_match = re.search(r'(font-size="52"[^>]*>\s*)(\d+)', content)   # second match = longest

# find both 52-px numbers
all52 = list(re.finditer(r'(font-size="52"[^>]*>)\s*(\d+)\s*(\n\s*<animate)', content, re.DOTALL))
if len(all52) >= 2 and cs_match:
    current_streak = int(cs_match.group(1))
    longest_streak = int(all52[1].group(2))
    if current_streak > longest_streak:
        m = all52[1]
        replacement = m.group(1) + f"\n    {current_streak}" + m.group(3)
        content = content[:m.start()] + replacement + content[m.end():]

# ── 3. Update the date labels ────────────────────────────────────────────────
# "May 27"  →  today's date  (only the Current Streak date, in the center panel)
content = re.sub(
    r'(<text[^>]*>)(May \d+)(</text>\s*<!-- RIGHT)',
    lambda m: m.group(1) + date_str + m.group(3),
    content
)

# Simpler fallback: replace the last bare "May DD" date string in the file
# (the one sitting just before the RIGHT panel comment)
content = re.sub(
    r'(letter-spacing="1">)(May \d+)(</text>\n\n  <!-- RIGHT)',
    lambda m: m.group(1) + date_str + m.group(3),
    content
)

with open(SVG_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Streak updated — date set to {date_str}")
