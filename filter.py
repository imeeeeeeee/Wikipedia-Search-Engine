import xml.etree.ElementTree as ET
from math import ceil
import os

def filter_pages_by_keywords(xml_file, keywords):
    # Define the namespace
    ns = {'mw': 'http://www.mediawiki.org/xml/export-0.10/'}
    # Register the namespace
    ET.register_namespace('', ns['mw'])
    
    # Load and parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # List to hold pages to be removed (to avoid modifying the tree while iterating)
    pages_to_remove = []

    # Iterate through each <page> element using the namespace
    for page in root.findall('mw:page', ns):
        # Find the <text> element using the namespace and get its text content
        text_element = page.find('mw:text', ns)
        if text_element is not None:
            text_content = text_element.text.lower() if text_element.text else ""

            # Count how many of the specified keywords appear in the text
            keyword_count = sum(keyword.lower() in text_content for keyword in keywords)

            # If fewer than two keywords are found, mark the page for removal
            if keyword_count < 4 or len(text_content.split()) < 600:
                pages_to_remove.append(page)

    # Remove the marked pages from the tree
    for page in pages_to_remove:
        root.remove(page)

    tmp_file_path = 'tmp.xml'
    tree.write(tmp_file_path, encoding='utf-8')
    return tmp_file_path

def main():
    keywords = ['nature',
                'vert',
                'plante',
                'feuille',
                'racine',
                'tige',
                'fleur',
                'graine',
                'croissance',
                'sol',
                'eau',
                'lumière solaire',
                'biodiversité',
                'forêt',
                'jardin',
                'écologie',
                'conservation',
                'espèce',
                'habitat',
                'climat']

    # Create the filtered directory if it doesn't exist
    if not os.path.exists('filtered'):
        os.makedirs('filtered')

    # Iterate over the files and apply the filtering
    for i in range(1, 17):  # 1 to 16
        xml_file = f'py1/frwiki_{i}.xml'
        filtered_file = filter_pages_by_keywords(xml_file, keywords)
        
        # Move and rename the temporary filtered file to the 'filtered' directory
        os.rename(filtered_file, f'filtered/frwiki_{i}_filtered.xml')

    # filter_pages_by_keywords('frwiki_1.xml',keywords)

if __name__ == "__main__":
    main()