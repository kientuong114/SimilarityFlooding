import sys
sys.path.append('../') #Include upper folder sources

import schema_graph_utils as sgu
from sql_parser import parse_sql, sql_ddl2Graph
from xml_parser import schema_tree2Graph, parse_xml
from xdr_parser import *
from schema_graph_compressor import compress_graph
import induced_propagation_graph as ipg
import filter as f
import networkx as nx

def test_on_sql():
    Gtemp = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql'))
    print(nx.get_node_attributes(Gtemp, 'type'))
    sgu.schema_graph_print(Gtemp)
    G1 = compress_graph(Gtemp)
    print(nx.get_node_attributes(G1, 'type'))
    sgu.schema_graph_print(G1)
    G2 = compress_graph(sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql')))
    node_attributes_A = nx.get_node_attributes(G1, 'type')
    node_attributes_B = nx.get_node_attributes(G2, 'type')
    print(node_attributes_A)
    print(node_attributes_B)
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs)


def test_base():
    G1 = nx.DiGraph()
    G1.add_edge("&a", "&a1", title='l1')
    G1.add_edge("&a", "&a2", title='l1')
    G1.add_edge("&a1", "&a2", title='l2')
    G2 = nx.DiGraph()
    G2.add_edge("&b", "&b1", title='l1')
    G2.add_edge("&b", "&b2", title='l2')
    G2.add_edge("&b2", "&b1", title='l2')

    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf, verbose=False)
    print(pairs)


def test_on_xml():
    Gtemp = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    print(nx.get_node_attributes(Gtemp, 'type'))
    sgu.schema_graph_print(Gtemp)
    G1 = compress_graph(Gtemp)
    print(nx.get_node_attributes(G1, 'type'))
    sgu.schema_graph_print(G1)
    G2 = compress_graph(schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml')))
    node_attributes_A = nx.get_node_attributes(G1, 'type')
    node_attributes_B = nx.get_node_attributes(G2, 'type')
    print(node_attributes_A)
    print(node_attributes_B)
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs)

def test_on_xdr():
    G1 = schema_tree2Graph(parse_xdr('test_schemas/Apertum.xdr'))
    G2 = schema_tree2Graph(parse_xdr('test_schemas/CIDXPOSCHEMA.xdr'))
    s1 = sgu.schema_graph_print(G1)
    input("Press any key to continue")
    s2 = sgu.schema_graph_print(G2)
    input("Press any key to continue")
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    print(sgu.combine_oid_to_name_pairs(G1, G2, pairs))

def test_on_xdr_compressed():
    Gtemp = schema_tree2Graph(parse_xdr('test_schemas/Apertum.xdr'))
    print(nx.get_node_attributes(Gtemp, 'type'))
    G1 = compress_graph(Gtemp)
    print(nx.get_node_attributes(G1, 'type'))
    G2 = compress_graph(schema_tree2Graph(parse_xdr('test_schemas/CIDXPOSCHEMA.xdr')))
    node_attributes_A = nx.get_node_attributes(G1, 'type')
    node_attributes_B = nx.get_node_attributes(G2, 'type')
    print(node_attributes_A)
    print(node_attributes_B)
    s1 = sgu.schema_graph_print(G1)
    input("Press any key to continue")
    s2 = sgu.schema_graph_print(G2)
    input("Press any key to continue")
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs)

def gen_sf(G1, G2):
    sf = ipg.SFGraphs(G1, G2)
    ipg.similarityFlooding(sf, max_steps=1000, verbose=True, fixpoint_formula=ipg.fixpoint_incremental)
    return sf


if __name__ == "__main__":
    test_on_sql()
