#!pip install pulp
# nltk, pandas
import numpy as np
from pulp import *

# Sentence semantics
import torch
import os
from transformers import AutoTokenizer, AutoModel #for embeddings
from sklearn.metrics.pairwise import cosine_similarity #for similarity
#download pretrained model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased",)
model = AutoModel.from_pretrained("bert-base-uncased",output_hidden_states=True)

#nltk.download('punkt')
#nltk.download('wordnet')

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import gui

# CONSTANTS
EQ_THRESHOLD = 0.7
VER_LENGTH = 3
os.environ['TOKENIZERS_PARALLELISM'] = "false"
unique_id = 0  

from abc import ABC, abstractclassmethod


# Match equivalent nodes in 2 given lists
def match(nodes1, nodes2, match_name = False, verbose=True):

    prob = LpProblem("Matching_Nodes", LpMaximize)

    # Useful setup
    n1 = len(nodes1)
    n2 = len(nodes2)
    nodes1_idx = range(n1)
    nodes2_idx = range(n2)

    # Matching preferences matrix
    c = np.zeros((n1, n2))
    for i in nodes1_idx:
        for j in nodes2_idx:
            rate = nodes1[i].eq_rate(nodes2[j], match_name)
            c[i][j] = rate

    # All possible combinations of nodes1 and nodes2 elements
    y = LpVariable.dicts("pair", [(i,j) for i in nodes1_idx for j in nodes2_idx], cat='Binary')

    # Maximise the sum over i of sum over j of c[i][j]*y[i][j]
    prob += lpSum([(c[i][j]) * y[(i,j)] for i in nodes1_idx for j in nodes2_idx])

    # But an element i can match with at most 1 element j
    # and the other way around
    for i in nodes1_idx:
        prob += lpSum(y[(i,j)] for j in nodes2_idx) <= 1
    for i in nodes2_idx:
        prob += lpSum(y[(j,i)] for j in nodes1_idx) <= 1

    # Applying a number of pairs to find
    prob += lpSum(y[(i,j)] for i in nodes1_idx for j in nodes2_idx) == np.min([n1, n2])
    # Calling solver
    prob.solve()

    # TO DO Possible enhancement with this dictionary to have a "translation" common point for nodes
    # for now, merging places overwrites names and labels for coherence between the 2 models
    matches = {} 
    diffs = []
    for j in nodes2_idx:
        # In cas it is not matched, it will be added to the other nodes list
        # as part of the "diffs" list
        unaffected = True
        for i in nodes1_idx:
            if y[(i,j)].varValue == 1 and c[i][j] > EQ_THRESHOLD:
                matches[nodes1[i]] = nodes2[j]
                if verbose:
                    print(f"Matched {nodes1[i]} and {nodes2[j]} with similarity score {c[i][j]}.")
                unaffected = False
        if unaffected:
            diffs.append(nodes2[j])

    # Worth noting that the solver does not always output the same matches if there are equalities
    if verbose:
        if len(diffs) != 0:
            print("Found diffs:")
            for diff in diffs:
                print(diff)
        else:
            print("Found no diffs")
        #print("Similarity matrix:")
        #print(c)
        

    return matches, diffs


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


# Compare semantic similarity for 2 words (used for elements' names), 
# but these names must be part of natural language (any other match would work because it is the exact same name)
def word_similarity(word1, word2):

    word_similarity = 0.0
    # Same word so we return upper_bound for this matching
    if word1 == '' or word2 == '':
        return 0
    elif word1 == word2:
        print(f"\t\tSame words '{word1}' and '{word2}'")
        return 1
    else:
        # Eliminating words containing less information 
        # TO DO comprendre plus exactement ce process
        word1 = preprocess_word(word1)
        word2 = preprocess_word(word2)

        # Searching for synonyms
        synsets1 = wordnet.synsets(word1)
        synsets2 = wordnet.synsets(word2)

        for synset1 in synsets1:
            for synset2 in synsets2:
                similarity = synset1.wup_similarity(synset2)
                if similarity is not None and similarity > word_similarity:
                    word_similarity = similarity
        """
        synset1.wup_similarity(synset2): 
            Wu-Palmer Similarity: 
            Return a score denoting how similar two word senses are, based on the depth of the two senses in the taxonomy 
            and that of their Least Common Subsumer (most specific ancestor node). 
            Note that at this time the scores given do not always agree with those given by Pedersen’s Perl implementation of Wordnet Similarity.
        """
    print(f"\t\tSimilarity between words '{word1}' and '{word2}' is {word_similarity}")
    return word_similarity


#create embeddings
def create_embeddings(text,token_length):
  tokens=tokenizer(text,max_length=token_length,padding='max_length',truncation=True)
  output=model(torch.tensor(tokens.input_ids).unsqueeze(0),
               attention_mask=torch.tensor(tokens.attention_mask).unsqueeze(0)).hidden_states[-1]
  return torch.mean(output,axis=1).detach().numpy()


# TO DO test out token lengths
# since we have to test every combinatin, some work is already done !
# we should process each outs, and then only process cosine_similarity
# when comparing
def desc_similarity(note1, note2, token_length=20):

    label1 = note1.get_label()
    label2 = note2.get_label()

    if len(label1) == 0 or len(label2) == 0:
        print("Undefined labels")
        return 0
    elif label1 == label2:
        print("Same description")
        return 1

    # L'intérêt est de ne faire l'embedding qu'au moment de l'évaluation des équivalences, et pas à l'initialisation
    # pour éviter le travail inutile (peut être que l'équivalence peut s'arrêter avant d'arriver à process d'embedding à cause d'une égalité parfaite entre les 2 phrases?)
    if not note1.is_embedded():
        note1.embeddings = create_embeddings(label1, token_length=token_length)
        print(f"No embeddings for {note1.get_name()}, creating one...")

    if not note2.is_embedded():
        note2.embeddings = create_embeddings(label2, token_length=token_length)
        print(f"No embeddings for {note2.get_name()}, creating one...")

    sim = cosine_similarity(note1.embeddings, note2.embeddings)[0][0]
    print(f"Similarity {sim} between descriptions:\n >>{note1}\n >>{note2}")
    return sim


# Calculates semantic similarity between name and description of 2 elements
def similarity(element1, element2, match_name=False):
    print(f"Calculating similarity of {element1.get_name()}, {element2.get_name()}")

    # Used for optimization after places names have been unified
    # We want same places to be matched (i.e places with exact same name)
    # any difference in the name implies different places
    if match_name:
        if element1.get_name() == element2.get_name():
            print("Same name ,elements matched")
            return 1
        else:
            print("Different names, elements can't be matched")
            return 0
    if word_similarity(element1.get_label(), element2.get_label()) == 1:
        print(f"Same label")
        return 1
    else:
        print("Different labels, seeking description match...")
        return desc_similarity(element1.get_desc(), element2.get_desc())



def merge_nodes(nodes1, nodes2):
        # Fetching solver answer for matching places
        matches, diffs = match(nodes1, nodes2)
        # Now we merge the matching nodes that passed the threshold
        clash_collector = []
        k = 0
        for match_node in matches.items():
            node1, node2  = match_node[0], match_node[1]
            # Node will have unique id, if merge fails, we just have to apply unique id to the other node
            try:
                node1.merge(node2)
            except ClashError as e:
                clash_collector.append(e)

        """
        # Those that did not match (diffs) are added to the list as new nodes
        for diff_node in diffs:
            # TO DO Probleme ne va pas apparaitre dans la vue si fait comme ca... préférer add_element ou quoi, mais alors faire un try except dans le add_element
            nodes1.append(diff_node)
        """

        if clash_collector == []:
            print(f"[NODES MERGE] Completed without error")
            print("~"* 40)
        else:
            print(f"[NODES MERGE] Found errors")
            print("> Starting clash resolve <")
            for clash in clash_collector:
                refused = clash.resolve()
                if bool(refused):
                    # TO DO Probleme ne va pas apparaitre dans la vue si fait comme ca... préférer add_element ou quoi, mais alors faire un try except dans le add_element
                    diffs.append(refused)
            print(f"[NODES MERGE] All merges completed")
            print(nodes1, nodes2)
            print("~"* 40)

        return diffs

# Give unique ids to all passed elements
def make_unique(marker):
    global unique_id
    unique_id += 1
    return marker + str(unique_id)
    

class ClashError(Exception, ABC):
    """
    default1
    default2
    ...
    type_format
    cl
    refused
    """
    def __init__(self, element1, element2):
        print("Conflictual values found, storing error for now...")
        self.element1, self.element2 = element1, element2
        self.init_message()
        self.init_format()
        self.store_default()
        self.refused = None
        
    def __str__(self):
        if bool(self.element1): 
            return f"Error while merging {self.element1.get_name()} and {self.element2.get_name()}, Clashing values for {self.message}"
        else:
            return "Error while merging"

    def resolve(self):
        self.cl = gui.Clashview(self, self.element1.model.clash_frame)
        self.cl.print(f"{self}.\nEnter value: (empty to cancel)")
        self.refused = ""
        self.try_merge()
        return self.refused

    def try_merge(self):
        while self.refused == "":
            # Fetch value input from the user
            self.cl.validate.wait_variable(self.cl.user_input)
            value = str(self.cl.user_input.get())
            try:
                self.cl.print(f"chosen value: {value}")
                # Overwriting values in the clashed elements
                # Any issue over format will be raised here
                self.write_value(value)

                # Trying to merge
                self.element1.merge(self.element2)
                self.refused = None

            except ValueError:
                if value == "":
                    self.cl.print(f"Merge canceled, defaulting to values {self.element1} | {self.element2} and adding {self.element2} to diffs")
                    self.reset_value()
                    self.refused = self.element2
                else:
                    self.cl.print(f"Wrong format, should be of type {self.type_format}.")
        self.cl.destroy()
    
    @abstractclassmethod
    def init_message(self):
        pass
    
    @abstractclassmethod
    def init_format(self):
        pass
    
    @abstractclassmethod
    def store_default(self):
        pass

    @abstractclassmethod
    def write_value(self, value):
        pass
    
    @abstractclassmethod
    def reset_value(self):
        pass



class TimeClashError(ClashError):
            
        # Override
    def init_message(self):
        self.message = f"time stamps : {self.element1.get_time()} | {self.element2.get_time()}"
    
    # Override
    def init_format(self):
        self.type_format = "str(bracket) int , int str(bracket)"
    
    # Override
    def store_default(self):
        self.default1 = self.element1.get_time()
        self.default2 = self.element2.get_time()

    # Override
    def write_value(self, value):
        self.element1.set_time(value)
        self.element2.set_time(value)

    # Override
    def reset_value(self):
        self.element1.set_time(self.default1)
        self.element2.set_time(self.default2)


class KindClashError(ClashError):

    # Override
    def init_message(self):
        self.message = f"arc kind : {self.element1.get_kind()} | {self.element2.get_kind()}"
    
    # Override
    def init_format(self):
        self.type_format = "str"
    
    # Override
    def store_default(self):
        self.default1 = self.element1.get_kind()
        self.default2 = self.element2.get_kind()

    # Override
    def write_value(self, value):
        self.element1.set_kind(value)
        self.element2.set_kind(value)

    # Override
    def reset_value(self):
        self.element1.set_kind(self.default1)
        self.element2.set_kind(self.default2)


class WeightClashError(ClashError):

    # Override
    def init_message(self):
        self.message = f"arc weight : {self.element1.get_weight()} | {self.element2.get_weight()}"
    
    # Override
    def init_format(self):
        self.type_format = "int"
    
    # Override
    def store_default(self):
        self.default1 = self.element1.get_weight()
        self.default2 = self.element2.get_weight()

    # Override
    def write_value(self, value):
        self.element1.set_weight(value)
        self.element2.set_weight(value)

    # Override
    def reset_value(self):
        self.element1.set_weight(self.default1)
        self.element2.set_weight(self.default2)


class MarkingClashError(ClashError):
        
    # Override
    def init_message(self):
        self.message = f"place marking : {self.element1.get_marking()} | {self.element2.get_marking()}"
    
    # Override
    def init_format(self):
        self.type_format = "int"
    
    # Override
    def store_default(self):
        self.default1 = self.element1.get_marking()
        self.default2 = self.element2.get_marking()
    
    # Override
    def write_value(self, value):
        self.element1.set_marking(value)
        self.element2.set_marking(value)

    # Override
    def reset_value(self):
        self.element1.set_marking(self.default1)
        self.element2.set_marking(self.default2)


    