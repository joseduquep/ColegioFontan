"""
Fix the encoding of data_export.json by re-encoding it as UTF-8.
Reads with latin-1 (which can decode any byte), then writes as UTF-8.
"""
# Read with latin-1 (accepts any byte sequence)
with open('data_export.json', 'r', encoding='latin-1') as f:
    data = f.read()

# Write back as proper UTF-8
with open('data_export.json', 'w', encoding='utf-8') as f:
    f.write(data)

print(f"Fixed encoding. File size: {len(data)} characters")
print("Done!")
