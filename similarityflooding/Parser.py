import re
import pprint
import pylab


def parse_sql(file_path):

    with open(file_path, 'r') as file_object:
        query = file_object.read().replace('\n', ' ').replace('\t', '')

    queries = re.sub(' +', ' ', query).strip(' ').split(';')[:-1]

    return queries


def sql_ddl2graph(data, G):
    import networkx as nx

    # todo: index nodes for now are connected to each other only for 'column' and 'SQLType' relations, so
    #   have to add connections between nodes that have destination nodes with the same characteristics
    # todo: add weights
    # todo: apply other libraries or external software for more beautiful graph drawings

    G.add_node('Table')
    G.add_node('Column')
    G.add_node('ColumnType')

    index = 1

    query_elements = []
    for table in data:
        temp = table.split(',')
        temp[-1] = temp[-1][:-2]    # Fixing open parenthesis of last element
        query_elements.append(temp)

    creation_table = re.compile(r'\s*(CREATE TABLE )(?P<tableName>\w*)\s*(\()\s(?P<nameColumn>\w*)\s(?P<SQLType>\S+)\s*(?P<other>.*)')
    creation_column = re.compile(r'\s*(?P<nameColumn>\w*)\s(?P<SQLType>\S+)\s*(?P<other>.*)')

    for tables in query_elements:
        for elements in tables:
            match = creation_table.match(elements)
            if match is not None:
                # Adding tableName and its components
                table_name = match.group('tableName')
                name_elem = '&' + str(index)
                index += 1
                G.add_edge(name_elem, table_name, title='name')
                G.add_edge(name_elem, 'Table', title='type')
            else:
                match = creation_column.match(elements)

            # Adding the column with its SQLType
            new_column = '&' + str(index)
            index += 1
            name_column = match.group('nameColumn')
            G.add_edge(new_column, 'Column', title='type')
            G.add_edge(new_column, name_column, title='name')
            G.add_edge(name_elem, new_column, title='column')

            new_SQLType = '&' + str(index)
            index += 1
            name_SQLType = match.group('SQLType')
            G.add_edge(new_column, new_SQLType, title='SQLType')
            G.add_edge(new_SQLType, 'ColumnType', title='type')
            G.add_edge(new_SQLType, name_SQLType, title='name')

    # Displaying the graph
    pos = nx.spring_layout(G, k=3)
    edge_labels = nx.get_edge_attributes(G, 'title')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    pylab.show()


def main():
    import networkx as nx

    print("Please insert the file path of the SQL DLL file")
    file_path = input()
    data = parse_sql(file_path)
    G = nx.DiGraph()
    sql_ddl2graph(data, G)


if __name__ == '__main__':
    main()
