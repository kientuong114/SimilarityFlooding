import sys
sys.path.append('../') #Include upper folder sources

from parse.sql_parser import parse_sql, sql_ddl2Graph
from parse.xml_parser import schema_tree2Graph, parse_xml
from parse.xdr_parser import *
from parse.schema_graph_compressor import compress_graph
from sf import induced_propagation_graph as ipg
import filter.filter as f
import networkx as nx


def test_on_sql_compressed(formula, outfile):
    G1 = compress_graph(sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql')))
    G2 = compress_graph(sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql')))
    sf = gen_sf(G1, G2, formula=formula)
    sgu.schema_graph_draw(sf.IPG)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs, outfile)

def test_on_sql_compressed():
    G1 = compress_graph(sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql')))
    G2 = compress_graph(sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql')))
    sgu.schema_graph_draw(G2)
    sf = gen_sf(G1, G2)
    sgu.schema_graph_print(sf.IPG)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs)


def test_on_sql_uncompressed(formula, outfile):
    G1 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql'))
    G2 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql'))
    sf = gen_sf(G1, G2, formula=formula)
    pairs = f.select_filter(sf)
    f.print_pairs(sgu.combine_oid_to_name_pairs(G1, G2, pairs), outfile)


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

def test_on_xdr(formula, outfile):
    G1 = schema_tree2Graph(parse_xdr('test_schemas/CIDXPOSCHEMA.xdr'))
    G2 = schema_tree2Graph(parse_xdr('test_schemas/Apertum.xdr'))
    #s1 = sgu.schema_graph_print(G1)
    #s2 = sgu.schema_graph_print(G2)
    sf = gen_sf(G1, G2, formula=formula)
    pairs = f.select_filter(sf)
    f.print_pairs(sgu.combine_oid_to_name_pairs(G1, G2, pairs), outfile)

def test_on_xdr_compressed(formula, outfile):
    Gtemp = schema_tree2Graph(parse_xdr('test_schemas/CIDXPOSCHEMA.xdr'))
    #print(nx.get_node_attributes(Gtemp, 'type'))
    G1 = compress_graph(Gtemp)
    #print(nx.get_node_attributes(G1, 'type'))
    G2 = compress_graph(schema_tree2Graph(parse_xdr('test_schemas/Apertum.xdr')))
    node_attributes_A = nx.get_node_attributes(G1, 'type')
    node_attributes_B = nx.get_node_attributes(G2, 'type')
    #print(node_attributes_A)
    #print(node_attributes_B)
    s1 = sgu.schema_graph_print(G1)
    s2 = sgu.schema_graph_print(G2)
    sf = gen_sf(G1, G2, formula=formula)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs, outfile)

def gen_sf(G1, G2, formula=ipg.fixpoint_incremental):
    sf = ipg.SFGraphs(G1, G2)
    #Choises for fixpoint formula:
    #  fixpoint_incremental
    #  fixpoint_A
    #  fixpoint_B
    #  fixpoint_C 
    ipg.similarityFlooding(sf, max_steps=100, verbose=True, fixpoint_formula=formula, tqdm=True)
    return sf


if __name__ == "__main__":
    #test_on_sql_compressed()
    FILE_BASE = 'results/xdr_no_sf/xdr_2'
    for formula in (('incr', ipg.fixpoint_incremental), ('A', ipg.fixpoint_A), ('B', ipg.fixpoint_B), ('C', ipg.fixpoint_C)):
        with open(FILE_BASE+'_comp_'+formula[0]+'.txt', 'w+') as out:
            print('xdr test', file=out)
            print('Compressed graphs', file=out)
            print('Fixpoint Formula: ' + formula[0], file=out)
            test_on_xdr_compressed(formula[1], out)
        with open(FILE_BASE+'_no_comp_'+formula[0]+'.txt', 'w+') as out:
            print('xdr test', file=out)
            print('Uncompressed graphs', file=out)
            print('Fixpoint Formula: ' + formula[0], file=out)
            test_on_xdr(formula[1], out)
