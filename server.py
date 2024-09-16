import pickle
import dill
from collections import defaultdict
from flask import Flask, request, render_template_string
import requests
# import spacy

# --------------------- QUERY PRE-PROCESSING ---------------------

# nlp = spacy.load("fr_core_news_lg")

# def clarify_request(req):
#     doc = nlp(req)    
#     res = []
    
#     for token in doc:
#         if not token.is_stop and not token.is_punct:
#             res.append(token.lemma_)

#     return ' '.join(res)

# def clarify_request(req):
#     req = ''.join(request)
#     req = request.split(' ')

#     return [word for word in req]

# ------------------ TEMPORARY REQUEST HANDLING ------------------
# (this will be done properly in another file soon)

def dumb_request_process(request):
    # Process the request (you can replace this with your own logic)
    req = ''.join(request)
    req = request.split(' ')

    return [word for word in req]

# ------------------ REQUEST HANDLING ------------------

# We need to import all of the data
with open('idfs.pkl','rb') as file:
    IDF = pickle.load(file)

with open('TF.pkl','rb') as file:
    TF = pickle.load(file)

with open('ND.pkl','rb') as file:
    ND = pickle.load(file)

def find_pages_with_all_query_words(word_pages, query):
    num_words = len(query)  # Number of words in the query
    current_indices = [0] * num_words  # Current index for each word in the query
    matching_pages = []  # List to store pages that contain all query words
    
    # Continue as long as there's at least one more page for each query word
    while all(current_indices[i] < len(word_pages[query[i]]) for i in range(num_words)):
        # Find the maximum page number among the current pages of all query words
        eee = query[0]
        eee = current_indices[0]
        eee = word_pages[query[0]][current_indices[0]]
        eee = word_pages[query[0]][current_indices[0]][0]
        max_page = max(word_pages[query[i]][current_indices[i]][0] for i in range(num_words)
                       if current_indices[i] < len(word_pages[query[i]]))
        
        # Counter for the number of query words found in the max_page
        count_match = 0
        for i in range(num_words):
            # Advance the index for each word until it reaches or surpasses the max_page
            while current_indices[i] < len(word_pages[query[i]]) and word_pages[query[i]][current_indices[i]][0] < max_page:
                current_indices[i] += 1
            
            # If the word is found in the max_page, increment the counter
            if current_indices[i] < len(word_pages[query[i]]) and word_pages[query[i]][current_indices[i]][0] == max_page:
                count_match += 1
        
        # If all query words are found in max_page, add it to the result list
        if count_match == num_words:
            matching_pages.append(max_page)
            # Move to the next page for each word
            for i in range(num_words):
                current_indices[i] += 1
    
    return matching_pages

def common_pages(query, tf=TF):
    common_pages = None
    for word in query:
        pages = tf.get(word, {})
        if common_pages is None:
            common_pages = set(pages.keys())
        else:
            common_pages &= set(pages.keys())
    return common_pages

def calculate_score(pages, tf, idf, nd, pagerank, alpha, beta, gamma):
    scores = {}
    for page in pages:
        f_d_r = sum(idf[word] * tf[word].get(page, 0) for word in tf if word in idf) / nd[page]
        p_d = pagerank[page] ** gamma
        scores[page] = [pagerank[page], f_d_r, alpha * f_d_r + beta * p_d]
    return sorted(scores.items(), key=lambda item: item[1][2], reverse=True)
    # return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def get_wikipedia_urls_by_pageids(page_ids):
    # Conversion de la liste d'IDs en une chaîne séparée par des '|'
    ids_string = '|'.join(str(id) for id in page_ids)
    
    # URL de base de l'API de Wikipédia pour obtenir des informations sur des pages
    api_url = "https://fr.wikipedia.org/w/api.php"
    
    # Paramètres de la requête à l'API
    params = {
        'action': 'query',
        'format': 'json',
        'pageids': ids_string,
        'prop': 'info',
        'inprop': 'url'
    }
    
    # Exécution de la requête HTTP GET
    response = requests.get(api_url, params=params)
    
    # Initialisation de la liste des URLs
    urls = []
    
    # Vérification que la requête a réussi
    if response.status_code == 200:
        data = response.json()
        pages = data['query']['pages']
        
        for page_id in pages:
            # Vérifie si 'fullurl' est présent avant d'accéder à la valeur
            if 'fullurl' in pages[page_id]:
                urls.append(pages[page_id]['fullurl'])
            else:
                # Vous pouvez choisir de retourner une valeur par défaut ou d'ignorer cette page
                urls.append(f"URL non trouvée pour l'ID {page_id}")
            
        return urls
    else:
        return ["Erreur lors de la requête à l'API de Wikipédia."]

def final_display(result):
    result = result[:20]

    ids = [int(pageid_to_realid[r[0]]) for r in result]
    urls = get_wikipedia_urls_by_pageids(ids)

    final_res = []
    for i in range(len(urls)):
        print(result[i])
        cur_res = []
        cur_res.append(urls[i])
        cur_res.append(f"PageRank : {result[i][1][0]:.6f}")
        cur_res.append(f"Relevance : {result[i][1][1]:.6f}")
        cur_res.append(f"Total : {result[i][1][2]:.6f}")
        final_res.append(cur_res)
        
    return final_res

# ---------------------------- SERVER ----------------------------

app = Flask(__name__)

# HTML template for the main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Query Processor</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding: 20px; }
        .result-item { margin-bottom: 10px; }
        .result-link { word-break: break-all; } /* Ensures URLs don't overflow */
    </style>
</head>
<body>
    <div class="container">
        <h2>MAAIN : Recherche Wikipédia</h2>
        <form method="post" class="mb-3">
            <div class="form-group">
                <input type="text" class="form-control" name="query" placeholder="Entrez votre requête" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        {% if results %}
            <h3>Résultats:</h3>
            <div>
            {% for sublist in results %}
                <div class="result-item">
                    <a href="{{ sublist[0] }}" class="result-link" target="_blank">{{ sublist[0] }}</a>
                    {% if sublist|length > 1 %}
                        <p>
                        {% for item in sublist[1:] %}
                            {{ item }}
                            {% if not loop.last %}, {% endif %}
                        {% endfor %}
                        </p>
                    {% endif %}
                </div>
            {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

WRD = None
TF = None
IDF = None
ND = None
pageid_to_realid = None
pagerank = None

with open('WPR.pkl', 'rb') as f:
    WRD = dill.load(f)
# with open('WPR.pkl','rb') as file:
#     WRD = pickle.load(file)
with open('TF.pkl','rb') as file:
    TF = pickle.load(file)
with open('idfs.pkl','rb') as file:
    IDF = pickle.load(file)
with open('ND.pkl','rb') as file:
    ND = pickle.load(file)
with open('pageid_to_realid.pkl','rb') as file:
    pageid_to_realid = pickle.load(file)
with open('pagerank.pkl','rb') as file:
    pagerank = pickle.load(file)

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    # ---------- QUERY HANDLER ----------
    if request.method == 'POST':
        query = request.form['query']
        # clarified_query = clarify_request(query)
        clarified_query = query.split(' ')
        # relevant_pages = find_pages_with_all_query_words(WRD,clarified_query)
        relevant_pages = common_pages(clarified_query, TF)

        if len(relevant_pages)>0:
            filtered_tf = {word: TF[word] for word in clarified_query if word in TF}
            results = calculate_score(relevant_pages,filtered_tf,IDF,ND,pagerank,1.0,0.3,0.5)
            results = final_display(results)
        else:
            results = [['','Aucune page ne correspond à votre recherche.']]
        # if the clarified query removed all words, use the raw query
        # if len(clarified_query)>0:
        #     results = dumb_request_process(clarified_query)
        # else : 
        #     results = dumb_request_process(query)
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(port=8888)