import networkx as nx # type: ignore
from collections import deque
import pylab # type: ignore


def OID_generator(char:str='a', start_num:int=1):
    n = start_num
    while True:
        yield char + str(n)
        n += 1


def is_OID(elem:str):
    if elem[0] == '&' and len(elem) > 1:
        # for char in elem[1:]:         This condition is not used to facilitate testing on test_base
        #     if not char.isdigit():
        #         return False
        return True
    return False


def get_names(G):
    oid_name = {}
    for elem in G.edges().data():
        if elem[2]["title"] == "name":
            oid_name[elem[0]] = elem[1]
    return oid_name


def combine_oid_to_name_pairs(G1, G2, pairs):
    namesG1 = get_names(G1)
    namesG2 = get_names(G2)

    final = []
    for pair in pairs:
        if pair[0] is not None and pair[1] is not None:
            final.append((namesG1[pair[0]], namesG2[pair[1]]))
        else:
            if pair[0] is None:
                final.append((None, namesG2[pair[1]]))
            else:
                final.append((namesG1[pair[0]], None))

    return final


def DFS(G, startNode=None):
    if not startNode:
        startNode = list(G.nodes())[0]

    q = deque((startNode,))
    visited = set()
    visiting = set((startNode,))

    while q:
        curr = q.pop()
        visiting.remove(curr)
        yield curr
        visited.add(curr)
        for child in G.neighbors(curr):
            if child not in visited and child not in visiting:
                visiting.add(child)
                q.append(child)


def schema_graph_print(G, data_rep:bool=True):
    for edge in G.edges(data=True):
        print(edge)
    print()


def schema_graph_draw(G, title:str='title'):
    pos = nx.spring_layout(G, k=3)
    edge_labels = nx.get_edge_attributes(G, 'title')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    pylab.show()
