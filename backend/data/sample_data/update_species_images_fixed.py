import json

# Read the original file
with open('species.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Extract the species_list using a more reliable method
start = content.find('species_list = ') + len('species_list = ')
end = content.rfind(']') + 1
species_data = content[start:end]

# Parse the list of dictionaries
species_list = eval(species_data)

# Update the image_url for each species
for species in species_list:
    if 'id' in species and 'image_url' in species:
        species['image_url'] = f"static\\images\\species\\{species['id']}"

# Reconstruct the file content
new_content = 'species_list = ' + json.dumps(species_list, indent=4, ensure_ascii=False, sort_keys=False)
new_content = new_content.replace('"', '"')  # Ensure proper quote escaping
new_content = new_content.replace('\"', '"')  # Fix escaped quotes

# Write the updated content back to the file
with open('species.py', 'w', encoding='utf-8') as file:
    file.write(new_content)

print("Species image URLs have been updated successfully!")
