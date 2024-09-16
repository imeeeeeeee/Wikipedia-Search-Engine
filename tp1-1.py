import sys
import re

# ---------- notes ----------

"""
stuff to remove :
- files format (".jpg")
- xml bullshit ("&lt", "&gt") DONE
- the "=" denoting sections ("==== Villes et villages ====") DONE
- white space 
- markdown things (""italique"", \"""gras\""")
- liens externes (balises ref) DONE
- liens internes commençant par [[Mot_clé:titre...]]
- sections "notes et références" "voir aussi" "bibliographie" "articles connexes" "liens externes"
- tout en minuscule, supprimer symboles spéciaux, comme :
- PONCTUATION

- pages dont le contenu (dans <text>) contient moins de 600 mots après nettoyage

stuff to take advantage of :
- <title>, <page>
- <id> maybe (cf consignes TP1: garder title, page, ptet id, et virer le reste)
- [[Article]], [[Article|texte]]
"""

# ---------- fonctions ----------

def remove_sub_titles(text):
    """
    Removes all sub-titles, replaces them with empty line.

    ----------Input:
    = Lorem =
    Ipsum
    == dolor ==
    sit
    === amet ===
    ----------Output :
    = Lorem =
    Ipsum
    
    sit
      
    """
    # TODO : fix, doesn't seem to always work. try titles with spaces in them

    return re.sub("==.*?[^=].*?={2,}\n", '', text, re.UNICODE)

def remove_units(text):
    """
    Removes all ({{}}), replaces them with empty line.

    ----------Input:
    Lorem ipsum (sit {{amet|consectetur}} adipiscing)
    ----------Output :
    Lorem ipsum
    """
    return re.sub("\({{[^}]*}}[^)]*\)", '', text, re.UNICODE)

def remove_refs(text):
    """
    Removes all <ref> tags, replaces them with empty line.

    ----------Input:
    Lorem ipsum &lt;ref&gt(sit {{amet|consectetur}} adipiscing)
    ----------Output :
    Lorem ipsum
    """
    return re.sub('&lt;ref.*?(/&gt;|&lt;/ref&gt;)', '', text, re.UNICODE)
    
def remove_html_comments(text):
    """
    Removes all html comments, replaces them with empty line.

    ----------Input:
    <body>
      <!-- This is a comment -->
      <p>This is some text.</p>
      <!-- Another comment -->
    </body>
    ----------Output :
    <body>
    
      <p>This is some text.</p>
    
    </body>
    """
    return re.sub("<!--.*?-->", '', text, re.UNICODE)

def remove_whitespace(text):
    """
    Removes whitespaces, replaces them with a single space.

    ----------Input:
    Lorem ipsum  dolor   sit    amet     .
    ----------Output :
    Lorem ipsum dolor sit amet .
    """
    return re.sub(" {2,}", ' ', text)

def remove_blank_lines(text):
    """
    Removes blank lines, replaces them with a single space.

    ----------Input:
    Lorem ipsum,

    dolor sit amet,


    consectetur adipiscing elit.
    ----------Output :
    Lorem ipsum, dolor sit amet, consectetur adipiscing elit.
    
    """
    return re.sub("\n{2,}", ' ', text)

def remove_last_lines(text):
    """ 
    Removes the last few lines 
    """
    split = text.split("\n")
    lines = []
    last_lines = re.compile("==.*?(Voir aussi|Annexes|Notes et références|Liens externes).*?==")

    for line in split:
        if not last_lines.match(line) is None: break
        lines.append(line)
    return "\n".join(lines)

def remove_fileblocks(text):
    """
    Removes all metadata about files, only keeps the title as it is on the Wikipedia page.

    ----------Input:
    [[Fichier:Nine Glories of Paris.webm|vignette|thumbtime=5|start=4|end=31|L'Arc de Triomphe en 1921.]]
    ----------Output:
    L'Arc de Triomphe en 1921.
    """
    # separated pattern and re.sub because this regex is god awful
    pattern = r'\[\[Fichier:[^\]]*\|([^\|]+)\]\]'
    result_string = re.sub(pattern, r'\1', text)
    return result_string.strip()

# ---------- tests ----------

def REMOVE(text):
    text = remove_sub_titles(text)
    text = remove_units(text)
    text = remove_refs(text)
    text = remove_html_comments(text)
    text = remove_whitespace(text)
    text = remove_blank_lines(text)
    # text = remove_last_lines(text) doesn't work for now
    text = remove_fileblocks(text)
    return text

mystr = """Lorem ipsum [[Fichier:x|y|z]] dolor amet"""
print(remove_fileblocks(mystr))

mystr = """Stuff text [[Fichier:aaa|bbb|ccc|ddd|eee|fff]] around"""
print(remove_fileblocks(mystr))

# ---------- final ----------

# il faudra choisir entre : 
# - faire bcp de fonctions (code clair, mais moins efficace)
# - faire peu de fonctions (code moins lisible, mais + rapide car moins de passages)


if __name__ == "__main__":
    print("[START TP1-1-NETTOYAGE]")

    if len(sys.argv) == 3:
        xml_file = ""

        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            xml_file = file.read()
            xml_file = REMOVE(xml_file)
        print('(XML file cleaned)')

        with open(sys.argv[2], 'w', encoding='utf-8') as file:
            file.write(xml_file)
        print('(new XML file saved)')

    else:
        print("[ERROR TP1-1 NETTOYAGE]")
        print("    Usage attendu: ")
        print("python3 nettoyage.py in.xml out.xml")

    print("[END TP1-1-NETTOYAGE]")