this_file='matrix2.py'
print(this_file,': loading imports.')
# import difflib
import math
import xml.etree.ElementTree as ET
import re
from collections import defaultdict, Counter
import spacy
import pickle
# import os # unused
# from dictionary import find_closest_word # moved here

print(this_file,': starting spacy.')
nlp = spacy.load("fr_core_news_sm", disable=["parser", "ner"])

print(this_file,': opening our files.')
# Les 25000 mots, reste à charger
with open('dict.pkl','rb') as file:
    valid_words = pickle.load(file) # CHANGED TO A SET !!!

with open('idfs.pkl','rb') as file:
    IDF = pickle.load(file)

with open('relations.pkl','rb') as file:
    RELATIONS =  pickle.load(file)

print(this_file,': defining our data structures.')
# Data structures
valid_words = set(valid_words)
word_page_relation = defaultdict(lambda: defaultdict(int))
adjacency_list = defaultdict(set)

# Find closest word using difflib
# def find_closest_word(misspelled_word, word_list):
#     closest_matches = difflib.get_close_matches(misspelled_word, word_list)
#     return closest_matches[0] if closest_matches else None

def find_internal_links(text):
    pattern = r'\[\[([^\[\]|]+)(?:\|[^\[\]]+)?\]\]'
    links = re.findall(pattern, text)
    return links

# def update_word_page_relation(page_id, text, word_page_relation, valid_words):
#     print('a',end='')
#     doc = nlp(text)
#     page_word_count = defaultdict(int)

#     print('b',end='')
#     for token in doc:
#         if not token.is_stop and not token.is_punct:
#             root = token.lemma_
#             # corrected_word = find_closest_word(root, valid_words)
#             if root in valid_words:
#                 page_word_count[root] += 1
#     print('c',end='')
#     for word, count in page_word_count.items():
#         word_page_relation[word][page_id] += count
#     print('d',end='')

def update_word_page_relations_batch(root, ns, word_page_relation, valid_words_set, pagetitle_to_pageid):
    print(this_file,': uwpr-step1.')
    # Step 1: Collect texts and page IDs
    texts_and_ids = [(page.find('.//mw:title', ns).text + " " + page.find('.//mw:text', ns).text, pagetitle_to_pageid[page.find('.//mw:title',ns).text])
                     for page in root.findall('.//mw:page', ns)]
    
    print(this_file,': uwpr-step2.')
    # Step 2: Process with nlp.pipe
    # Note: texts_and_ids is a list of tuples (text, page_id), we need to unpack them
    texts, page_ids = zip(*texts_and_ids)  # This separates texts and their corresponding page IDs
    docs = list(nlp.pipe(texts))  # Process all texts at once
    
    print(this_file,': uwpr-step3.')
    # Step 3: Update relations for each processed document
    for doc, page_id in zip(docs, page_ids):
        # print(page_id, end=' ')
        page_word_count = defaultdict(int)
        for token in doc:
            if not token.is_stop and not token.is_punct and token.lemma_ in valid_words_set:
                page_word_count[token.lemma_] += 1
        
        for word, count in page_word_count.items():
            word_page_relation[word][page_id] += count

def process_xml_file(xml_data, valid_words=valid_words):
    # root = ET.fromstring(xml_data)  # Parse the XML data
    ns = {'mw': 'http://www.mediawiki.org/xml/export-0.10/'}

    tree = ET.parse(xml_data) 
    root = tree.getroot()
    # Initialize CSR representation components for the adjacency matrix
    C, I, L = [], [], [0]

    DEBUG_COUNTER = 0

    pagetitle_to_pageid = None
    with open('pagetitle_to_pageid.pkl', 'rb') as file:
        pagetitle_to_pageid = pickle.load(file)

    print(this_file,': starting word-page relation.')
    update_word_page_relations_batch(root, ns, word_page_relation, valid_words, pagetitle_to_pageid)
    
    print(this_file,': starting internal link search.')
    # Process each page in the XML data
    for page in root.findall('.//mw:page',ns):
        # # if DEBUG_COUNTER%25==0 :
        # print(DEBUG_COUNTER, end=' ')
        # DEBUG_COUNTER+=1
        page_title = page.find('.//mw:title',ns).text
        page_text = page.find('.//mw:text',ns).text
        page_id = pagetitle_to_pageid[page_title]
        
        # Find and process internal links in the current page
        links = find_internal_links(page_text)
        for link in links:
            link_id = RELATIONS[link.lower()]

            # Ensure the page_id key exists in adjacency_list as a set
            if page_id not in adjacency_list:
                adjacency_list[page_id] = set()
            adjacency_list[page_id].add(link_id)

    print(this_file,': building CSR representation.')
    # Build the CSR representation as we go
    for page_id in range(1, max(adjacency_list.keys()) + 1):

        links = adjacency_list.get(page_id, [])
        L.append(len(C))  # Start index for this node's adjacency list in C

        if links:
            weight = 1 / len(links)
            for link_id in links:
                C.append(weight)
                I.append(link_id)  # Adjust for 0-based indexing

    L.append(len(C))  # End index for the last node's adjacency list

    # Save results to disk
    save_to_disk(word_page_relation, "word_page_relation.xml")
    save_to_disk(adjacency_list, "graph.xml")

    # Also return CSR representation for further use
    return C, I, L


def compute_tf(word_page_relation = word_page_relation):
    tf_dict = {}
    for word, occ in word_page_relation.items():
        tf_page = {}
        for page, val in occ.items():
            tf_page[page] = 1 + math.log10(val)
        tf_dict[word] = tf_page
    return tf_dict

def compute_nd(word_page_relation = word_page_relation):
    tfs = compute_tf(word_page_relation)
    Nd = defaultdict(float)

    for word, pages in tfs.items():
        for page, tf_value in pages.items():
            Nd[page] += tf_value**2  # Sum of squares of TFs for each page

    # Take the square root of the sum for each page to get Nd
    for page in Nd:
        Nd[page] = math.sqrt(Nd[page])

    return Nd

def compute_normalized_tf(word_page_relation = word_page_relation):
    # Calculate term frequencies and norms
    tfs = compute_tf(word_page_relation)
    nd_per_page = compute_nd(word_page_relation)
    
    normalized_tf = defaultdict(dict)

    for word, pages in tfs.items():
        for page, tf_value in pages.items():
            # Calculate normalized TF only if Nd is not 0 to avoid division by zero
            if nd_per_page[page] != 0:
                normalized_tf[word][page] = tf_value / nd_per_page[page]
            else:
                normalized_tf[word][page] = 0

    return normalized_tf

def filter_weak_word_page_associations(word_page_relation = word_page_relation):
    idf_scores = IDF
    tf_scores = compute_tf(word_page_relation)
    nd_scores = compute_nd(word_page_relation)
    
    filtered_word_page_relations = defaultdict(dict)
    
    for word, pages in tf_scores.items():
        for page, tf_score in pages.items():
            normalized_tf = tf_score / nd_scores[page] if nd_scores[page] > 0 else 0
            score = idf_scores[word] * normalized_tf
            
            threshold = 0.01  # This is an example value; need to determine the appropriate value through testing
            
            if score > threshold:
                filtered_word_page_relations[word][page] = score
    
    return filtered_word_page_relations

def save_to_disk(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for key, value in data.items():
            file.write(f"{key}: {value}\n")

# xml_data = """
# <root>
# <page>
# <title>Algèbre linéaire</title>
# <id>7</id>
# <text>Le texte de la page sur l'algèbre linéaire le Le texte de la page sur l'[[algèbre linéaire]] le... ....</text>
# </page>
# <page>
# <title>Calcul différentiel</title>
# <id>12</id>
# <text>Le texte de la page sur le calcul différentiel [[Calcul différentiel|calcul différentiel]] [[algèbre linéaire]]...</text>
# </page>
# </root>
# """

# # Your adjacency list
# adjacency_list_test = {
#     1: {2, 3, 4},
#     2: set(),
#     3: {1, 4},
#     4: {1}
# }

#print(create_matrix(adjacency_list_test))
def main():
# Parse and process the XML data
    print(this_file,': starting main.')

    file = 'py1-old/frwiki_1.xml' # put what you want
    C, I, L = process_xml_file(file)
    print("C:", C[:20])
    print("I:", I[:20])
    print("L:", L[:20])

    tf = compute_tf()
    nd = compute_nd()

    # Save if needed
    with open('C_matrix.pkl','wb') as file:
        pickle.dump(C,file)

    with open('I_matrix.pkl','wb') as file:
        pickle.dump(I,file)

    with open('L_matrix.pkl','wb') as file:
        pickle.dump(L,file)

    with open('TF.pkl','wb') as file:
        pickle.dump(tf,file)
    
    with open('ND.pkl','wb') as file:
        pickle.dump(nd,file)

if __name__=="__main__":
    main()
