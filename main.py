import similarityflooding.parse.xdr_parser as xdr_parser
import similarityflooding.sf.ipg as ipg
import similarityflooding.filter.filter as f
import similarityflooding.utils.utils as utils
from similarityflooding.parse.compressor import compress_graph
import networkx as nx
import os
import sys

TEST_SCHEMA_PATH = 'test/test_schemas'


def xdr_compressed():
    cidxposchema = os.path.join(TEST_SCHEMA_PATH, 'CIDXPOSCHEMA.xdr')
    apertum = os.path.join(TEST_SCHEMA_PATH, 'Apertum.xdr')

    G1 = compress_graph(xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr(cidxposchema)))
    G2 = compress_graph(xdr_parser.schema_tree2Graph(xdr_parser.parse_xdr(apertum)))

    print('Example of run with CIDXPOSCHEMA.xdr + Apertum.xdr, compressed and fixpoint_incremental')
    print('Printing first schema: ')
    s1 = utils.schema_graph_print(G1)
    input('Press any key to continue...')
    print('Printing second schema: ')
    s2 = utils.schema_graph_print(G2)
    input('Press any key to continue...')

    sf = ipg.SFGraphs(G1, G2)

    print('Executing similarity flooding algorithm:')
    ipg.similarity_flooding(sf, max_steps=500, verbose=False, fixpoint_formula=ipg.fixpoint_incremental, tqdm=True)

    print('Executing filter algorithm')
    pairs = f.select_filter(sf)
    print('Printing results of filter selection: ')
    f.print_pairs(pairs)


if __name__ == "__main__":
    xdr_compressed()
