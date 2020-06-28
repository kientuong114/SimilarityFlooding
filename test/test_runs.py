import sys
sys.path.append('../')
from similarityflooding.parse.compressor import compress_graph
import similarityflooding.sf.ipg as ipg
import similarityflooding.filter.filter as f
import similarityflooding.utils.utils as utils
import networkx as nx
import sys


def test_on_sql_compressed(formula, outfile):
    import similarityflooding.parse.sql_parser as sql_parser
    G1 = compress_graph(sql_parser.sql_ddl2Graph(sql_parser.parse_sql('test_schemas/test_schema_from_paper1.sql')))
    G2 = compress_graph(sql_parser.sql_ddl2Graph(sql_parser.parse_sql('test_schemas/test_schema_from_paper2.sql')))
    sf = gen_sf(G1, G2, formula=formula)
    utils.schema_graph_draw(sf.IPG)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs, outfile)


def test_on_sql_uncompressed(formula, outfile=sys.stdout):
    import similarityflooding.parse.sql_parser as sql_parser
    G1 = sql_parser.sql_ddl2Graph(sql_parser.parse_sql('test_schemas/test_schema_from_paper1.sql'))
    G2 = sql_parser.sql_ddl2Graph(sql_parser.parse_sql('test_schemas/test_schema_from_paper2.sql'))
    sf = gen_sf(G1, G2, formula=formula)
    pairs = f.select_filter(sf)
    f.print_pairs(utils.combine_oid_to_name_pairs(G1, G2, pairs), outfile)


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
    import similarityflooding.parse.xml_parser as xml_parser

    G1 = compress_graph(xml_parser.schema_tree2Graph(xml_parser.parse_xml('test_schemas/test_schema.xml')))
    utils.schema_graph_print(G1)
    G2 = compress_graph(xml_parser.schema_tree2Graph(xml_parser.parse_xml('test_schemas/test_schema_2.xml')))
    sf = gen_sf(G1, G2)
    pairs = f.select_filter(sf)
    f.print_pairs(pairs)


def test_on_xdr(formula, outfile=sys.stdout):
    import similarityflooding.parse.xdr_parser as xdr_parser
    G1 = xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr('test_schemas/CIDXPOSCHEMA.xdr'))
    G2 = xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr('test_schemas/Apertum.xdr'))
    sf = gen_sf(G1, G2, formula=formula)
    pairs = f.select_filter(sf)
    f.print_pairs(utils.combine_oid_to_name_pairs(G1, G2, pairs), outfile)


def test_on_xdr_compressed(formula, outfile=sys.stdout):
    import similarityflooding.parse.xdr_parser as xdr_parser

    G1 = compress_graph(xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr('test_schemas/CIDXPOSCHEMA.xdr')))
    G2 = compress_graph(xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr('test_schemas/Apertum.xdr')))
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
    ipg.similarity_flooding(sf, max_steps=100, verbose=True, fixpoint_formula=formula, tqdm=True)
    return sf


if __name__ == "__main__":
    test_on_xml()
    """
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
    """
