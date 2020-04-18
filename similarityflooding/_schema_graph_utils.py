import networkx as nx
from collections import deque
import pylab


def OID_generator(char = 'a', start_num = 1):
    n = start_num
    while True:
        yield char + str(n)
        n += 1

def BFS(G, startNode=None):
    if not startNode:
        startNode = list(G.nodes())[0]

    q = deque((startNode,))
    visited = set()
    visiting = set((startNode,))

    while q:
        curr = q.popleft()
        visiting.remove(curr)
        yield curr
        visited.add(curr)
        for child in G.neighbors(curr):
            if child not in visited and child not in visiting:
                visiting.add(child)
                q.append(child)

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



def schema_graph_draw(G, title='title'):
    pos = nx.spring_layout(G, k=3)
    edge_labels = nx.get_edge_attributes(G, 'title')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    pylab.show()
