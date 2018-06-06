import gensim
import networkx as nx
import matplotlib.pyplot as plt

m = 'ruscorpora_upos_skipgram_300_5_2018.vec.gz'

model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=False)


def word_list():
    with open('words.txt', 'r', encoding='UTF-8') as file:
        line = file.read()
    arr = line.split('\n')
    arr.remove('')
    return arr


def graph():
    graph = nx.Graph()
    words = word_list()
    graph.add_nodes_from(words)
    edges = []
    for word1 in words:
        for word2 in words:
            if word1 in model and word2 in model:
                cos = model.similarity(word1, word2)
                print(word1, word2, cos)
                if cos > 0.5:
                    edges.append((word1, word2))
            else:
                continue
    graph.add_edges_from(edges)
    plt.figure(figsize=(15, 15))
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, node_color='green', node_size=10)
    nx.draw_networkx_edges(graph, pos, edge_color='blue')
    nx.draw_networkx_labels(graph, pos, font_size=10)
    plt.axis('off')
    nx.write_gexf(graph, 'fields.gexf')
    deg = nx.degree_centrality(graph)
    components = [i for i in nx.connected_component_subgraphs(graph) if len(i.nodes()) > 1]
    for c in components:
        print('Центральное слово компоненты - ',
              str(sorted(nx.degree_centrality(c), key=lambda x: deg[x], reverse=True)[0]),
              ', радиус - ', str(nx.radius(c)),
              ', коэф. кластеризации - ', str(nx.average_clustering(c)))


graph()
