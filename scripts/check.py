import requests

# URL of the plain text version of the book
url = "https://www.gutenberg.org/files/22228/22228-0.txt"
response = requests.get(url)

# ✅ Check the response status
if response.status_code == 200:
    print("✅ Successfully connected to Project Gutenberg")
else:
    print("❌ Failed to connect. Status code:", response.status_code)
    exit(1)

text = response.text

# 🔍 Check for the markers
start_marker = "VOCABULARY OF THE LUMMI."
end_marker = "Local Nomenclature of the Lummi Tribe"
start_index = text.find(start_marker)
end_index = text.find(end_marker, start_index)

# ✅ Print out the markers for debugging
print(f"Start Index: {start_index}")
print(f"End Index: {end_index}")

# If found, print the text around it
if start_index != -1 and end_index != -1:
    print("\n🔎 Marker Found! Here is a sample of the content:")
    print(text[start_index:start_index + 500])
else:
    print("❌ Markers not found.")
