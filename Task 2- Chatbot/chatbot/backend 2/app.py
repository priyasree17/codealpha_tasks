from flask import Flask, request, render_template
import json
import random
import nltk
import string
import os  # For getting PORT environment variable
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('stopwords')

app = Flask(__name__)

# Load intents
with open("intents.json") as file:
    intents = json.load(file)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
tokenizer = TreebankWordTokenizer()

def preprocess(text):
    tokens = tokenizer.tokenize(text.lower())
    words = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return ' '.join(words)

# Build corpus from patterns
corpus = []
tags = []
for intent in intents['intents']:
    for pattern in intent['patterns']:
        corpus.append(preprocess(pattern))
        tags.append(intent['tag'])

# Vectorize patterns using TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

def get_response(user_input):
    input_processed = preprocess(user_input)
    input_vector = vectorizer.transform([input_processed])

    similarities = cosine_similarity(input_vector, X).flatten()
    best_match_index = np.argmax(similarities)
    best_score = similarities[best_match_index]

    print("\nSimilarity Scores:")
    for i, score in enumerate(similarities):
        print(f"[{i}] Tag: {tags[i]}, Pattern: '{corpus[i]}', Score: {score:.4f}")

    if best_score > 0.3:
        tag = tags[best_match_index]
        for intent in intents['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    else:
        return "I'm sorry, I didn't understand that. Can you try again?"

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        user_input = request.form["message"]
        response = get_response(user_input)
    return render_template("index.html", response=response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
