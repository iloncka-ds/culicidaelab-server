# Script to update image_url in species.py

# Read the original file
with open('species.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Replace the image_url for each species
updated_content = []
lines = content.split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    if '"id": ' in line and i + 2 < len(lines) and '"image_url":' in lines[i+2]:
        # Extract the species_id
        species_id = line.split('"id": "')[1].split('"')[0]
        # Add the updated image_url line
        updated_content.append(line)  # Add the id line
        updated_content.append(lines[i+1])  # Add the next line (scientific_name)
        updated_content.append(f'        "image_url": "static\\images\\species\\{species_id}",')
        i += 3  # Skip the next two lines (scientific_name and original image_url)
    else:
        updated_content.append(line)
        i += 1

# Write the updated content back to the file
with open('species.py', 'w', encoding='utf-8') as file:
    file.write('\n'.join(updated_content))

print("Species image URLs have been updated successfully!")
