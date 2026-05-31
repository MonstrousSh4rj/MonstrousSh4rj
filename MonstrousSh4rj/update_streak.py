import re
from datetime import date

SVG_FILE = "streak-card.svg"

today = date.today()
# Use strftime without %-d for cross-platform compatibility
day = str(today.day)  # no leading zero
month = today.strftime("%b")
date_str = f"{month} {day}"   # e.g. "May 31"

with open(SVG_FILE, "r", encoding="utf-8") as f:
    content = f.read()

def bump(svg, font_size):
    pattern = re.compile(
        r'(font-size="' + str(font_size) + r'"[^>]*>)\s*(\d+)\s*(\n\s*<animate)',
        re.DOTALL
    )
    def replacer(m):
        new_val = int(m.group(2)) + 1
        return m.group(1) + f"\n    {new_val}" + m.group(3)
    return pattern.sub(replacer, svg)

# Bump current streak (font-size 36)
content = bump(content, 36)

# Bump total contributions (first font-size 52)
pattern52 = re.compile(
    r'(font-size="52"[^>]*>)\s*(\d+)\s*(\n\s*<animate)',
    re.DOTALL
)
matches52 = list(pattern52.finditer(content))
if matches52:
    m = matches52[0]
    new_val = int(m.group(2)) + 1
    replacement = m.group(1) + f"\n    {new_val}" + m.group(3)
    content = content[:m.start()] + replacement + content[m.end():]

# Update longest streak if current streak exceeds it
cs_match = re.search(r'font-size="36"[^>]*>\s*(\d+)', content)
all52 = list(re.finditer(r'(font-size="52"[^>]*>)\s*(\d+)\s*(\n\s*<animate)', content, re.DOTALL))
if len(all52) >= 2 and cs_match:
    current_streak = int(cs_match.group(1))
    longest_streak = int(all52[1].group(2))
    if current_streak > longest_streak:
        m = all52[1]
        replacement = m.group(1) + f"\n    {current_streak}" + m.group(3)
        content = content[:m.start()] + replacement + content[m.end():]

# Update the date label near current streak
content = re.sub(
    r'(letter-spacing="1">)(May \d+|Jun \d+|Jul \d+|Aug \d+|Sep \d+|Oct \d+|Nov \d+|Dec \d+|Jan \d+|Feb \d+|Mar \d+|Apr \d+)(</text>)',
    lambda m: m.group(1) + date_str + m.group(3),
    content
)

with open(SVG_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Streak updated — date set to {date_str}")
