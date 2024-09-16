this_file = 'dictionary.py'
print(this_file,': loading imports.')
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
# import difflib # related function moved to matrix.py
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
import nltk
import spacy
import pickle

# Download NLTK components
print(this_file,': downloading NLTK components.')
nltk.download(['stopwords', 'punkt', 'wordnet'])

# Initialize Spacy and stopwords
print(this_file,': starting Spacy.')
nlp = spacy.load("fr_core_news_sm")
stop_words = stop_words = fr_stop | {"|", "||", "|-", "_", "-", "—", "–", "...", "}", "}}" , ")"}  # Add any other unwanted tokens here

print(this_file,': defining data structures.')
RELATIONS = defaultdict(int)
word_in_document_count = defaultdict(int)
# Define namespace for XML parsing
NS = {'mw': 'http://www.mediawiki.org/xml/export-0.10/'}
titles_texts = []

# Function to clean, lemmatize, and remove stopwords
def process_text(text, is_lemmatize=False, min_len = 2):
    doc = nlp(text.lower())
    return [token.text for token in doc if not token.is_stop and not token.is_punct and token.text not in stop_words]
    # ### we decided not to lemmatize. the following code has no purpose
    # if is_lemmatize:
    #     return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.text not in stop_words and len(token.text)>=min_len]
    # else:
    #     return [token.text for token in doc if not token.is_stop and not token.is_punct and token.text not in stop_words]

# def load_xml(filename):
#     with open(filename, 'r', encoding='utf-8') as file:
#         tree = ET.parse(file)
#     root = tree.getroot()
#     for page in root.findall('mw:page', NS):
#         title = page.find('mw:title', NS).text
#         text = page.find('mw:text', NS).text
#         id = int(page.find('mw:id', NS).text)
#         titles_texts.append((title, text))
#         RELATIONS[title.lower()] = id  # Populate RELATIONS

def clean_text(text):
    # Correct the pattern to match content within [[ ]]
    text = re.sub(r'\[\[([^\[\]]*)\]\]', r'\1', text)
    # Correct the pattern to remove *, ., and '
    text = re.sub(r'[\*]|\.', '', text)
    return text

def tokenize(text):
    text = clean_text(text)
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    return words
 
def load_xml(xml_file):
    pagetitle_to_pageid = None
    with open('pagetitle_to_pageid.pkl', 'rb') as file:
        pagetitle_to_pageid = pickle.load(file)

    mots_freq = Counter()
    for event, elem in ET.iterparse(xml_file, events=('start', 'end')):
            if event == 'start' and elem.tag.endswith('page'):
                # title = id = text = None
                title = text = None
            if event == 'end':
                if elem.tag.endswith('title'):
                    title = elem.text
                # elif elem.tag.endswith('id') and id is None:
                #     id = elem.text
                elif elem.tag.endswith('text'):
                    text = elem.text if elem.text else ""
                    mots = tokenize(text)
                    # print(mots)
                    mots_freq.update(mots)

                if title and id:
                    RELATIONS[title] = pagetitle_to_pageid[title]
                elem.clear()
    filtered_mots_freq = Counter({word: freq for word, freq in mots_freq.items() if word not in stop_words and len(word)>2})
    return filtered_mots_freq

# Compute IDF for words in texts
# def compute_idf(texts, freq):
#     D = len(texts)
#     for text in texts:
#         unique_words = set(text.split())
#         for word in unique_words and freq:
#             word_in_document_count[word] += 1
#     return {word: math.log10(D / freq) for word, freq in word_in_document_count.items()}



def compute_idf(file, words):
    ns = {'mw': 'http://www.mediawiki.org/xml/export-0.10/'}

    tree = ET.parse(file) 
    root = tree.getroot()

    documents = [elem.text.lower().split() for elem in root.findall('.//mw:text', ns)] 

    doc_freqs = defaultdict(int)
    for doc in documents:
        unique_words = set(doc)
        intersection = unique_words.intersection(words)  
        for word in intersection:
            doc_freqs[word] += 1

    N = len(documents)

    idf_scores = {word: math.log10(N / doc_freqs.get(word, 1)) for word in words} 

    return idf_scores

# Save data to disk
def save_to_disk(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}\n")


def main():
    #The hard part
    # for i in range(1, 17):  # 1 to 16
    #     xml_file = f'filtered/frwiki_{i}_filtered.xml'
    #     load_xml(xml_file)

    # titles, raw_texts = zip(*titles_texts)

    # processed_texts = [' '.join(process_text(text)) for text in raw_texts]
    # lemmatized_titles = [process_text(title) for title in titles]

    # word_count = Counter()
    # for text in processed_texts:
    #     word_count.update(text.split())

    # for title in lemmatized_titles:
    #     word_count.update(title)

    # final_word_set = set(word for word, _ in word_count.most_common(20000)).union(*lemmatized_titles)
    # final_word_list = sorted(final_word_set, key=lambda w: -word_count[w])

    file = 'py1-old/frwiki_1.xml' #put what you want
    num_most_common = 30000

    print(this_file,': calculating',num_most_common,'most common words.')
    mots = load_xml(file).most_common(num_most_common)
    mots_list = [word for word, _ in mots]

    print(this_file,': computing IDF for most common words.')
    idfs = compute_idf(file,mots_list)

    print(this_file,': saving all data.')
    with open('dict.pkl', 'wb') as outfile:
        pickle.dump(mots_list, outfile)

    # save_to_disk(mots_list, 'text.txt') just wanted to make sure

    with open('idfs.pkl', 'wb') as outfile:
        pickle.dump(idfs, outfile)

    with open('relations.pkl', 'wb') as outfile:
        pickle.dump(RELATIONS, outfile)
    print(this_file,'done.')

if __name__ == "__main__":
    main()