import pickle
import xml.etree.ElementTree as ET
import glob

this_file = 'custom_pageid.py'

# -------------------------------------------------------------------

def process_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    custom_id = 0 # local custom id
    page_titles = {}

    for page in root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'):
        title = page.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
        page_titles[custom_id] = title
        custom_id += 1

    return page_titles

def process_all_xml_files(directory_path):
    # glob is used to find all files in the given directory
    xml_files = glob.glob(f"{directory_path}/*.xml")
    
    all_titles = {}
    custom_id = 0 # global custom id

    for file_path in xml_files:
        print(this_file, ': opening file',file_path) # to show the progress
        page_titles = process_xml_file(file_path)
        
        # update the global dictionary with the new titles, adjusting the custom ID
        for title in page_titles.values():
            all_titles[custom_id] = title
            custom_id += 1
    
    return all_titles

# -------------------------------------------------------------------

if __name__ == "__main__":
    directory_path = 'py1'  # change to the actual path
    all_titles = process_all_xml_files(directory_path)
    # print(all_titles)

    output_file = 'pageid_to_pagetitle.pkl'
    print(this_file, ': done, saving result to',output_file)
    
    with open(output_file, 'wb') as file:
        pickle.dump(all_titles, file)

    output_file = 'pagetitle_to_pageid.pkl'
    print(this_file, ': done, saving reverse result to',output_file)

    reversed_all_titles = {value: key for key, value in all_titles.items()}

    with open(output_file, 'wb') as file:
        pickle.dump(reversed_all_titles, file)