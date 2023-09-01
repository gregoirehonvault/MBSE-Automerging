import nltk

#nltk.download('punkt')
#nltk.download('wordnet')

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def preprocess_word(word):
    # Tokenize the word
    tokens = word_tokenize(word.lower())

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Return the preprocessed word
    return " ".join(tokens)


def calculate_similarity(word1, word2):
    word1 = preprocess_word(word1)
    word2 = preprocess_word(word2)

    synsets1 = wordnet.synsets(word1)
    synsets2 = wordnet.synsets(word2)

    max_similarity = 0.0


# SYNSET BIEN POUR COMPARER 1 MOT (ON SORT LES SYNONYMES) il faut trouver autre chose pour les phrases ??? ou combiner ce que j'ai trouvé avant
    for synset1 in synsets1:
        for synset2 in synsets2:
            similarity = synset1.wup_similarity(synset2)
            if similarity is not None and similarity > max_similarity:
                max_similarity = similarity

    print(f"The semantic similarity between '{word1}' and '{word2}' is:\n{max_similarity}")
    return max_similarity


word1 = "car"
word2 = "bus"
word3 = "vehicle"
word4 = "automobile"
similarity = calculate_similarity(word1, word2)
similarity = calculate_similarity(word1, word3)
similarity = calculate_similarity(word1, word4)