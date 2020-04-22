from sql_parser import parse_sql
from sql_parser import sql_ddl2Graph
from xml_parser import schema_tree2Graph
from xml_parser import parse_xml
import induced_propagation_graph as ipg
import filter as f
import _schema_graph_utils as sgu
import networkx as nx


def test_on_sql():
    G1 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql'))
    G2 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql'))
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    print(sgu.combine_oid_to_name_pairs(G1, G2, pairs))


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
    G1 = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    G2 = schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml'))
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    print(sgu.combine_oid_to_name_pairs(G1, G2, pairs))


def gen_sf(G1, G2):
    sf = ipg.SFGraphs(G1, G2)
    ipg.similarityFlooding(sf, max_steps=1000, verbose=True, fixpoint_formula=ipg.fixpoint_incremental)
    return sf


if __name__ == "__main__":
    test_on_sql()
