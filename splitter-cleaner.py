import xml.etree.ElementTree as ET
import re
import os

# -------------------- individual cleaning functions --------------------

def remove_sub_titles(text):
    """
    Removes all sub-titles, replaces them with empty line.

    ----------Input----------
    = Lorem =
    Ipsum
    == dolor ==
    sit
    === amet ===
    ----------Output----------
    = Lorem =
    Ipsum
    
    sit
      
    """

    return re.sub("==.*?[^=].*?={2,}\n", '', text, re.UNICODE)

def remove_units(text):
    """
    Removes all ({{}}), replaces them with empty line.

    ----------Input----------
    Lorem ipsum (sit {{amet|consectetur}} adipiscing)
    ----------Output----------
    Lorem ipsum
    """
    return re.sub("\({{[^}]*}}[^)]*\)", '', text, re.UNICODE)

def remove_refs(text):
    """
    Removes all <ref> tags, replaces them with empty line.

    ----------Input----------
    Lorem ipsum &lt;ref&gt(sit {{amet|consectetur}} adipiscing)
    ----------Output----------
    Lorem ipsum
    """
    return re.sub('&lt;ref.*?(/&gt;|&lt;/ref&gt;)', '', text, re.UNICODE)
    
def remove_html_comments(text):
    """
    Removes all html comments, replaces them with empty line.

    ----------Input----------
    <body>
      <!-- This is a comment -->
      <p>This is some text.</p>
      <!-- Another comment -->
    </body>
    ----------Output----------
    <body>
    
      <p>This is some text.</p>
    
    </body>
    """
    return re.sub("<!--.*?-->", '', text, re.UNICODE)

def remove_whitespace(text):
    """
    Removes whitespaces, replaces them with a single space.

    ----------Input----------
    Lorem ipsum  dolor   sit    amet     .
    ----------Output----------
    Lorem ipsum dolor sit amet .
    """
    return re.sub(" {2,}", ' ', text)

def remove_blank_lines(text):
    """
    Removes blank lines, replaces them with a single space.

    ----------Input----------
    Lorem ipsum,

    dolor sit amet,


    consectetur adipiscing elit.
    ----------Output----------
    Lorem ipsum, dolor sit amet, consectetur adipiscing elit.
    
    """
    return re.sub("\n{2,}", ' ', text)

def remove_fileblocks(text):
    """
    Removes all metadata about files, only keeps the title as it is on the Wikipedia page.

    ----------Input----------
    [[Fichier:Nine Glories of Paris.webm|vignette|thumbtime=5|start=4|end=31|L'Arc de Triomphe en 1921.]]
    ----------Output----------
    L'Arc de Triomphe en 1921.
    """
    # separated pattern and re.sub because this regex is god awful
    pattern = r'\[\[Fichier:[^\]]*\|([^\|]+)\]\]'
    result_string = re.sub(pattern, r'\1', text)
    return result_string.strip()

def remove_lt_gt(text):
    """
    Removes the &lt and &gt as well as their content.

    ----------Input----------
    Soient &lt;math&gt;F&lt;/math&gt; et &lt;math&gt;G&lt;/math&gt; deux sous-espace vectoriels.
    ----------Output----------
    Soient F et G deux sous-espace vectoriels. 
    """
    return re.sub(r'&lt;.*?&gt;', '', text)

def remove_spec_characters(text):
    """
    Removes a bunch of useless special characters.

    ----------Input----------
    L'orem "ipsum" <math>dolor*</math> & sit = amet
    ----------Output----------
    L orem  ipsum   math dolor  /math   sit   amet
    """
    # & deliberately replaced by "" and not a space " " because & is only found in URLs
    return text.replace("'", " ").replace("\"", " ").replace("’"," ").replace("&#039;"," ").replace("*", " ").replace("="," ").replace("&","").replace("<", " ").replace(">", " ")

def remove_ref_tags(text):
    """
    Removes the very frequent <ref> tags, and their attributes, but not their content.

    ----------Input----------
    Lorem <ref>{{Ouvrage|langue=fr|prénom1=Antoine (1866-1936) Auteur du texte|nom1=Meillet|titre=Esquisse d'une grammaire comparée de l'arménien classique}}</ref> Ipsum
    Dolor <ref name="hdr2021-22">{{HDR|2022}}</ref> Amet
    ----------Output----------
    Lorem  {{Ouvrage|langue=fr|prénom1=Antoine (1866-1936) Auteur du texte|nom1=Meillet|titre=Esquisse d'une grammaire comparée de l'arménien classique}}  Ipsum
    Dolor  {{HDR|2022}}  Amet
    """
    text = re.sub(r'<ref.*?>', ' ', text)
    return text.replace('</ref>',' ')

def remove_genealogy_tree(text):
    """
    Removes all lines of a genealogy tree.
    Note : we wanted to keep the internal links, but it proved to be too slow for very little gain.
           genealogy trees are rare and not in our selected corpus anyway.

    ----------Input----------
    Lorem
    {{Arbre généalogique/début|style=font-size:85%;line-height:100%;}}
    {{Arbre généalogique| | | | | | | | | | | | | | | | | | | | | | | | | }}
    Ipsum
    ----------Output----------
    Lorem
    Ipsum
    """
    lines = text.splitlines()
    filtered_lines = [line for line in lines if not line.startswith("{{Arbre généalogique")]
    return '\n'.join(filtered_lines)

def remove_categories(text):
    """
    Remove all but the X of every "[[Catégorie:X]]".

    ----------Input----------
    [[Catégorie:Lorem Ipsum]]
    [[Catégorie:Dolor amet]]
    ----------Output----------
    Lorem Ipsum
    Dolor amet
    """
    return re.sub(r'\[\[Catégorie:(.*?)\]\]', r'\1', text)   

### This function turned out to be way too slow, so we abandoned the idea.
# def remove_meta_words(text):
#     meta_words = ['auteur', 'titre', 'sous-titre', 'éditeur', 'date', 'année', 'édition', 'langue', 'écrit', 'coauteur', 'article', 'chapitre', 'ouvrage']
#     # pattern = re.compile(r'(?i)(\b(?:' + '|'.join(re.escape(word) for word in meta_words) + r')\b)', flags=re.IGNORECASE)
#     # # pattern = re.compile(r'(?i)\b(?:' + '|'.join(re.escape(word) for word in meta_words) + r')\b', flags=re.IGNORECASE)
#     # return pattern.sub(' ', text)

#     ### to avoid hardcoding (but needs a OS call...) :
#     # meta_words_file = 'meta_words.txt'
#     # with open(meta_words_file, 'r') as file:
#     #     meta_words = file.read().splitlines()
        
#     ### this regex turned out to be super slow, abandoned idea
#     pattern = r'(?i)(?:{})'.format('|'.join(re.escape(word) for word in meta_words))
#     return re.sub(pattern, ' ', text)

# -------------------- put all cleaing functions together --------------------

def REMOVE(text):
    # ---------- clean stuff : ----------
    text = remove_units(text)
    text = remove_refs(text)
    text = remove_html_comments(text)
    text = remove_categories(text)
    text = remove_genealogy_tree(text)
    text = remove_sub_titles(text) # maybe put it at the very last so we can use it
    text = remove_fileblocks(text)
    text = remove_lt_gt(text)
    text = remove_ref_tags(text)
    text = remove_spec_characters(text) # do it last, other functions need spec characters
    # text = remove_meta_words(text) # TOO SLOW !!!
    # ---------- remove leftovers : ----------
    text = remove_whitespace(text)
    text = remove_blank_lines(text)
    return text

# ------------------------------ splitter ------------------------------

def split_xml_into_files(input_xml_path, output_directory, max_file_size=1e7):
    output_file = None      # to open output streams
    is_first_file = True    # to know if wwe need to add <mediawiki> or not
    current_file_size = 0   # to know when we exceed max_file_size
    output_file_counter = 1 # to name output files correctly

    # parse through each event and element in the XML file
    for event, element in ET.iterparse(input_xml_path, events=('start', 'end')):
        # ------------------------- <event> -------------------------
        if event == 'start':
            if element.tag.endswith('mediawiki') and is_first_file:
                is_first_file = False
                continue
            if element.tag.endswith('page'):
                page_title = page_id = page_text = None

        # ------------------------- </event> -------------------------
        if event == 'end':
            if element.tag.endswith('page'):
                # Check if a new file should be started
                if output_file is None or current_file_size >= max_file_size:
                    if output_file is not None:
                        output_file.write('</mediawiki>')
                        output_file.close()
                        # return  # stops after creating one file, for testing
                    file_name = os.path.join(output_directory, f'frwiki_{output_file_counter}.xml')
                    output_file = open(file_name, 'w', encoding='utf-8')
                    output_file.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="fr">\n')
                    output_file_counter += 1
                    current_file_size = len('<mediawiki>')

                page_title = remove_spec_characters(page_title if page_title else "")
                page_text = REMOVE(page_text if page_text else "")

                page_content = f"<page>\n<title>{page_title}</title>\n<id>{page_id}</id>\n<text>{page_text}</text>\n</page>\n"
                output_file.write(page_content)
                current_file_size += len(page_content.encode('utf-8'))

            elif element.tag.endswith('title'):
                page_title = element.text
            elif element.tag.endswith('id') and page_id is None:
                page_id = element.text
            elif element.tag.endswith('text'):
                page_text = element.text

            # clear the element from memory to keep memory usage low
            element.clear()

    # the last file needs to be properly closed manually
    if output_file is not None:
        output_file.write('</mediawiki>')
        output_file.close()

# ------------------------------ main ------------------------------

if __name__ == '__main__':
    XML_FILE = 'frwiki.xml'
    OUTPUT_DIR = 'splitted-cleaned' 
    os.makedirs(OUTPUT_DIR, exist_ok=True) # will create directory if it doesn't exist
    split_xml_into_files(XML_FILE, OUTPUT_DIR)