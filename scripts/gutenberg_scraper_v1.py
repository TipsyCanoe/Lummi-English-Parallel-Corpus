import requests
import re
import pandas as pd
import os

# Paths
OUTPUT_PATH = '../raw_data/gutenberg_vocabulary_v1.csv'
os.makedirs('../raw_data', exist_ok=True)

# URL of the plain text version of the book
url = "https://www.gutenberg.org/files/22228/22228-0.txt"
response = requests.get(url)
text = response.text

print(f"Downloaded text, length: {len(text)} characters")

# Define the section with more flexible matching
start_marker = "VOCABULARY OF THE LUMMI"
# Try several potential end markers
end_markers = [
    "Local Nomenclature of the Lummi",
    "LOCAL NOMENCLATURE",
    "APPENDIX",
    "FOOTNOTES"
]

print(f"Looking for start marker: '{start_marker}'")
start_index = text.find(start_marker)

# Try case-insensitive search as backup for start marker
if start_index == -1:
    print("Trying case-insensitive search for start marker...")
    start_index = text.lower().find(start_marker.lower())

if start_index == -1:
    print("❌ Start marker not found in the document.")
    with open('../raw_data/text_sample.txt', 'w', encoding='utf-8') as f:
        f.write(text[:5000])
    print("Saved first 5000 chars to text_sample.txt for inspection")
    exit(1)

# Try to find the end marker
end_index = -1
for marker in end_markers:
    print(f"Looking for end marker: '{marker}'")
    end_index = text.find(marker, start_index + len(start_marker))
    if end_index != -1:
        print(f"Found end marker: '{marker}' at position {end_index}")
        break
    print(f"End marker '{marker}' not found, trying case-insensitive...")
    end_index = text.lower().find(marker.lower(), start_index + len(start_marker))
    if end_index != -1:
        print(f"Found end marker (case-insensitive): '{marker}' at position {end_index}")
        break

# If no end marker is found, use a fallback approach
if end_index == -1:
    print("No predefined end markers found. Searching for next major section...")
    # Save the text after start marker for manual inspection
    with open('../raw_data/text_after_start.txt', 'w', encoding='utf-8') as f:
        f.write(text[start_index:start_index+5000])
    
    # Look for a blank line followed by uppercase text (likely a new section)
    remainder = text[start_index + len(start_marker):]
    section_breaks = re.finditer(r'\n\s*\n\s*[A-Z][A-Z\s]+', remainder)
    
    for match in section_breaks:
        candidate_end = start_index + len(start_marker) + match.start()
        # Ensure we've captured a reasonable amount of text (at least 1000 chars)
        if candidate_end - start_index > 1000:
            end_index = candidate_end
            print(f"Found potential section break at position {end_index}")
            print(f"Section break text: '{match.group().strip()}'")
            break

# Final fallback: use a fixed amount of text if all else fails
if end_index == -1:
    print("No section breaks found. Using fixed length section...")
    end_index = start_index + 10000  # Capture a reasonable chunk of text
    print(f"Using fixed end position: {end_index}")

# Extract the section
lummi_section = text[start_index:end_index]
print("✅ Vocabulary section extracted.")
print(f"Section length: {len(lummi_section)} characters")

# Save section for debugging
with open('../raw_data/lummi_section_debug.txt', 'w', encoding='utf-8') as f:
    f.write(lummi_section)
print("✅ Saved extracted section to 'lummi_section_debug.txt' for inspection")

# Extract vocabulary with improved regex
vocabulary = []
line_count = 0
matched_count = 0

for line in lummi_section.splitlines():
    line = line.strip()
    if len(line) < 5:
        continue
    
    line_count += 1
    
    # Try multiple regex patterns to catch different formats
    match = re.match(r'^(.+?),\s+(.+?)\.$', line)
    if not match:
        match = re.match(r'^(.+?),\s+(.+?)$', line)  # Without period
    if not match:
        match = re.match(r'^(.+?)[-—–]\s*(.+?)$', line)  # With dash separator
    if not match:
        match = re.match(r'^([A-Za-z\s]+)[\.\s]+([A-Za-z\s]+)$', line)  # Simple format
        
    if match:
        matched_count += 1
        english = match.group(1).strip()
        lummi = match.group(2).strip()
        if lummi.endswith('.'):
            lummi = lummi[:-1]  # Remove trailing period if present
        vocabulary.append({'english': english, 'lummi': lummi})

# ✅ Debugging Information
print(f"Total lines processed: {line_count}")
print(f"Lines successfully matched: {matched_count}")
print(f"✅ Total Entries Found: {len(vocabulary)}")

if len(vocabulary) > 0:
    print("🔍 First 5 entries:")
    for entry in vocabulary[:5]:
        print(entry)
else:
    print("❌ No entries found. Check lummi_section_debug.txt for the extracted text.")
    
    # If no entries found, save some example lines to help diagnose regex issues
    with open('../raw_data/sample_lines.txt', 'w', encoding='utf-8') as f:
        f.write("SAMPLE LINES FROM SECTION:\n\n")
        count = 0
        for line in lummi_section.splitlines():
            if len(line.strip()) > 10:
                f.write(f"{line.strip()}\n")
                count += 1
                if count >= 20:
                    break
    print("Saved 20 sample lines to sample_lines.txt for regex debugging")

# Save to CSV
if vocabulary:
    df = pd.DataFrame(vocabulary)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"✅ Vocabulary scraped and saved to {OUTPUT_PATH}")
else:
    print("❌ No vocabulary saved as no entries were found.")