""" 

@auther : MANU C
Created : 27/01/18
Last Updated : 09/02/18

"""


from django.shortcuts import render
from nltk.tokenize import word_tokenize
import string

from py2neo import Graph, Node, Relationship, NodeSelector


# for testing purpose
import pdb
from py2neo import watch

# Main context Predictor Function
def predict_context(request):
    input_data = "Cat climbed the tree. Dog Climbed the other tree."
    #file = open("/home/manu154c/Downloads/phd-datasets/datasets/webkb-test-stemmed.txt","r")
    #input_data = file.read()
    cleaned_tocken = text_cleaning(input_data)
    #print(cleaned_tocken)
    dictinary_from_tokens = create_dictionary(cleaned_tocken)
    #insert_into_graph_db(dictinary_from_tokens)
    count_bigram_relatedness(cleaned_tocken, dictinary_from_tokens)
    #output = "Cat climbed the tree. Dog Climbed the tree."
    output = dictinary_from_tokens
    return render(request, 'Predict/post_list.html', {'output' : output})

# Word embedding require minimal document cleaning
# No need of stemming, stop words removal etc...
def text_cleaning(input_doc):
    tokens = word_tokenize(input_doc)
    # convert to lower case
    tokens_lower = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens_lower]
    stripped = filter(None, stripped)
    stripped = list(stripped)
    #print(stripped)
    return stripped

# Creates a dictionary from the input document.
def create_dictionary(input_token):
    # unique_values_list = list(set(input_token))
    output = {}
    # pdb.set_trace()
    for item in input_token:
        if item in output:
            output[item] = int(output[item]) + 1
        else:
            output[item] = 1
            
    # pdb.set_trace()

    return output


# training phase function
# 1. insert_into_graph_db


def insert_into_graph_db(dictionary_in):
    graph = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    neo4j_transaction = graph.begin()
    #print(dictionary_in)
    for key, value in dictionary_in.items():
        #node = Node(key, name=key, count=value)
        #print(key)
        #print(value)
        #assert(False)
        neo4j_transaction.append("CREATE (word:Word {value:{a}, count:{b}}) RETURN word;", a=key, b=value)
        #pdb.set_trace()
        #watch("neo4j.http")
        #neo4j_transaction.create(node)
    neo4j_transaction.commit()
    return 1


# it will count the number of relation exist between 2 nodes
# from input-token-list pick adjecent nodes
# check both nodes are present 
# if not create a CO_OCCURENCE relation after adding the node
#   do nothing
# else
#   call check_for_relation for check for a CO_OCCURENCE relation
def count_bigram_relatedness(cleaned_tocken, dictinary_from_tokens):
    list_position = len(cleaned_tocken)
    list_position = list_position-1
    print(cleaned_tocken)
    for i in range(list_position):
        node1 = cleaned_tocken[i]
        node2 = cleaned_tocken[i+1]
        check_for_relation(node1, node2)

    return 1


#   if CO_OCCURENCE 
#        increment the count
#   else 
#        create a new CO_OCCURENCE relation between those nodes
#        initialize the count to 1
def check_for_relation(node1, node2):
    g = Graph('http://localhost:7474/db/data', user='neo4j', password='root')

    d = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=node1)
    list_d = list(d)
    if len(list_d) > 0:
        d = list_d[0]['a']
    else:
        neo4j_transaction = g.begin()
        d = Node("Word",value=node1)
        neo4j_transaction.create(d)
        neo4j_transaction.commit()

    e = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=node2)
    list_e = list(e)
    if len(list_e) > 0:
        e = list_e[0]['a']
    else:
        neo4j_transaction = g.begin()
        e = Node("Word",value=node2)
        neo4j_transaction.create(e)
        neo4j_transaction.commit()


    relations = g.match(start_node=d, rel_type="CO_OCCURENCED", end_node=e)

    if len(list(relations)) == 0:
        print("No Relationship exists")
        neo4j_transaction = g.begin()
        ab = Relationship(d, "CO_OCCURENCED", e, bidirectional=True)
        neo4j_transaction.create(ab)
        neo4j_transaction.commit()
    else:
        print("Relationship already exist")

    return 1