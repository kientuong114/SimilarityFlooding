import networkx as nx
from fuzzywuzzy import fuzz

def generate(G, H):
    #print(G.nodes)
    #print(H.nodes)

    # to exclude OIDs only checks if it starts with '&', will improve later
    # initialMap is generated with fuzzywuzzy for now, will find better alternatives later
    initial_map = []
    for g_node in G.nodes:
        if g_node[0] != '&':
            for h_node in H.nodes:
                if h_node[0] != '&':
                    val = fuzz.ratio(g_node.lower(), h_node.lower())
                    initial_map.append([g_node, h_node, val / 100])

    initial_map.sort(key=lambda x: x[2], reverse=True)      # sorting by val
    # print("printing initialMap generated with fuzzywuzzy")
    # for i in initial_map:
    #     print(i)

    return initial_map
