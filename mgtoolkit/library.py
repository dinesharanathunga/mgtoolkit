from properties import resources
from exception import MetagraphException
from numpy import matrix
import copy
import math


def singleton(cls):
    """A helper function to ease implementing singletons.
    This should be used as a decorator to the
    class that should be a singleton.
    :param cls: class that should be a singleton
    :return: singleton instance of the class
    """
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance


class Triple(object):
    """ Captures a set of co-inputs, co-outputs and edges between two metagraph elements.
    """

    def __init__(self, coinputs, cooutputs, edges):
        if edges is None:
            raise MetagraphException('edges', resources['value_null'])

        self.coinputs = coinputs
        self.cooutputs = cooutputs
        self.edges = edges

    def coinputs(self):
        """ The co-inputs of the Triple object
        :return: set
        """
        return self.coinputs

    def cooutputs(self):
        """ The co-outputs of the Triple object
        :return: set
        """
        return self.cooutputs

    def edges(self):
        """ The edges of the Triple object
        :return: set
        """
        return self.edges

    def __repr__(self):
        if isinstance(self.edges, list):
            edge_desc = [repr(edge) for edge in self.edges]
        else:
            edge_desc = [repr(self.edges)]
        full_desc = ''
        for desc in edge_desc:
            if full_desc == '':
                full_desc = desc
            else:
                full_desc += ', ' + desc
        return 'Triple(%s, %s, %s)' % (self.coinputs, self.cooutputs, full_desc)


class Node(object):
    """ Represents a metagraph node.
    """

    def __init__(self, element_set):
        if element_set is None or len(element_set) == 0:
            raise MetagraphException('element_set', resources['value_null'])
        if not isinstance(element_set, set):
            raise MetagraphException('element_set', resources['format_invalid'])

        self.element_set = element_set

    def get_element_set(self):
        """ Returns the node elements
        :return: set
        """
        return self.element_set

    def __repr__(self):
        return 'Node(%s)' % self.element_set


class Edge(object):
    """ Represents a metagraph edge.
    """

    def __init__(self, invertex, outvertex, attributes=None, label=None):
        if invertex is None or len(invertex) == 0:
            raise MetagraphException('invertex', resources['value_null'])
        if outvertex is None or len(outvertex) == 0:
            raise MetagraphException('outvertex', resources['value_null'])
        if not isinstance(invertex, set):
            raise MetagraphException('invertex', resources['format_invalid'])
        if not isinstance(outvertex, set):
            raise MetagraphException('outvertex', resources['format_invalid'])

        self.invertex = invertex
        self.outvertex = outvertex
        self.attributes = attributes
        self.label = label

        # include attributes as part if invertex
        if attributes is not None:
            invertex = list(self.invertex)
            for attribute in attributes:
                if attribute not in invertex:
                    invertex.append(attribute)
            self.invertex = set(invertex)

    def __repr__(self):
        return 'Edge(%s, %s)' % (self.invertex, self.outvertex)

    def invertex(self):
        """ Returns the invertex of the edge.
        :return: set
        """
        return self.invertex

    def outvertex(self):
        """ Returns the outvertex of the edge.
        :return: set
        """
        return self.outvertex

    def label(self):
        """ Returns the label of the edge.
        :return: string
        """
        return self.label


class Metapath(object):
    """ Represents a metapath between a source and a target node in a metagraph.
    """

    def __init__(self, source, target, edge_list):
        if source is None or len(source) == 0:
            raise MetagraphException('source', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('target', resources['value_null'])

        self.source = source
        self.target = target
        self.edge_list = edge_list

    def source(self):
        """ Returns the source of the metapath.
        :return: set
        """
        return self.source

    def target(self):
        """ Returns the target of the metapath.
        :return: set
        """
        return self.target

    def edge_list(self):
        """ Returns the list of edges of the metapath.
        :return: set
        """
        return self.edge_list

    def __repr__(self):
        edge_desc = [repr(edge) for edge in self.edge_list]
        full_desc = 'source: %s, target: %s' % (self.source, self.target)
        for desc in edge_desc:
            if full_desc == '':
                full_desc = desc
            else:
                full_desc += ", " + desc
        return 'Metapath({ %s })' % full_desc

    def dominates(self, metapath):
        """Checks whether current metapath dominates that provided.
        :param metapath: Metapath object
        :return: boolean
        """
        if metapath is None:
            raise MetagraphException('metapath', resources['value_null'])

        input1 = self.source
        input2 = metapath.source

        output1 = self.target
        output2 = metapath.target

        if input1.issubset(input2) and output2.issubset(output1):
            return True

        return False


class Metagraph(object):
    """ Represents a metagraph.
    """

    def __init__(self, generator_set):
        if generator_set is None or len(generator_set) == 0:
            raise MetagraphException('generator_set', resources['value_null'])
        if not isinstance(generator_set, set):
            raise MetagraphException('generator_set', resources['format_invalid'])

        self.nodes = []
        self.edges = []
        self.generating_set = generator_set
        self.a_star = None

    def add_node(self, node):
        """ Adds a node to the metagraph.
        :param node: Node object
        :return: None
        """
        if not isinstance(node, Node):
            raise MetagraphException('node', resources['format_invalid'])

        # nodes cant be null or empty
        if node is None:
            raise MetagraphException('node', resources['value_null'])

        # each element in node must be in the generating set
        not_found = [element not in self.generating_set for element in node.element_set]
        if True in not_found:
            raise MetagraphException('node', resources['range_invalid'])

        if not MetagraphHelper().is_node_in_list(node, self.nodes):
            self.nodes.append(node)

    def remove_node(self, node):
        """ Removes a specified node from the metagraph.
        :param node: Node object
        :return: None
        """

        if not isinstance(node, Node):
            raise MetagraphException('node', resources['format_invalid'])

        # nodes cant be null or empty
        if node is None:
            raise MetagraphException('node', resources['value_null'])

        if not MetagraphHelper().is_node_in_list(node, self.nodes):
            raise MetagraphException('node', resources['value_not_found'])

        self.nodes.remove(node)

    def add_nodes_from(self, nodes_list):
        """ Adds nodes from the given list to the metagraph.
        :param nodes_list: list of Node objects
        :return: None
        """

        if nodes_list is None or len(nodes_list) == 0:
            raise MetagraphException('nodes_list', resources['value_null'])

        for node in nodes_list:
            if not isinstance(node, Node):
                raise MetagraphException('nodes_list', resources['format_invalid'])

        for node in nodes_list:
            if not MetagraphHelper().is_node_in_list(node, self.nodes):
                self.nodes.append(node)

    def remove_nodes_from(self, nodes_list):
        """ Removes nodes from the given list from the metagraph.
        :param nodes_list: list of Node objects
        :return: None
        """

        if nodes_list is None or len(nodes_list) == 0:
                raise MetagraphException('nodes_list', resources['value_null'])

        for node in nodes_list:
            if not isinstance(node, set):
                raise MetagraphException('nodes_list', resources['format_invalid'])
            if not MetagraphHelper().is_node_in_list(node, self.nodes):
                raise MetagraphException('nodes_list', resources['value_not_found'])

        for node in nodes_list:
            self.nodes.remove(node)

    def add_edge(self, edge):
        """ Adds the given edge to the metagraph.
        :param edge: Edge object
        :return: None
        """

        if not isinstance(edge, Edge):
            raise MetagraphException('edge', resources['format_invalid'])

        # add to list of nodes first
        node1 = Node(edge.invertex)
        node2 = Node(edge.outvertex)
        if not MetagraphHelper().is_node_in_list(node1, self.nodes):
            self.nodes.append(node1)
        if not MetagraphHelper().is_node_in_list(node2, self.nodes):
            self.nodes.append(node2)

        #..then edges
        if not MetagraphHelper().is_edge_in_list(edge, self.edges):
            self.edges.append(edge)

    def remove_edge(self, edge):
        """ Removes the given edge from the metagraph.
        :param edge: Edge object
        :return:None
        """

        if not isinstance(edge, Edge):
            raise MetagraphException('edge', resources['format_invalid'])

        # remove edge
        if edge in self.edges:
            self.edges.remove(edge)

    def add_edges_from(self, edge_list):
        """ Adds the given list of edges to the metagraph.
        :param edge_list: list of Edge objects
        :return: None
        """

        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        for edge in edge_list:
            if not isinstance(edge, Edge):
                raise MetagraphException('edge', resources['format_invalid'])

        for edge in edge_list:
            node1 = Node(edge.invertex)
            node2 = Node(edge.outvertex)
            if not MetagraphHelper().is_node_in_list(node1, self.nodes):
                self.nodes.append(node1)
            if not MetagraphHelper().is_node_in_list(node2, self.nodes):
                self.nodes.append(node2)
            if edge not in self.edges:
                self.edges.append(edge)

    def remove_edges_from(self, edge_list):
        """ Removes edges from the given list from the metagraph.
        :param edge_list: list of Edge objects
        :return: None
        """

        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        for edge in edge_list:
            if not isinstance(edge, Edge):
                raise MetagraphException('edge', resources['format_invalid'])

        for edge in edge_list:
            if MetagraphHelper().is_edge_in_list(edge, self.edges):
                self.edges.remove(edge)

    def nodes(self):
        """ Returns a list of metagraph nodes.
        :return: list of Node objects
        """
        return self.nodes

    def edges(self):
        """ Returns a list of metagraph edges.
        :return: list of Edge objects.
        """
        return self.edges

    def get_edges(self, invertex, outvertex):
        """ Retrieves all edges between a given invertex and outvertex.
        :param invertex: set
        :param outvertex: set
        :return: list of Edge objects.
        """

        if invertex is None:
            raise MetagraphException('invertex', resources['value_null'])
        if outvertex is None:
            raise MetagraphException('outvertex', resources['value_null'])

        result = []
        if len(self.edges) > 0:
            for edge in self.edges:
                if (invertex in edge.invertex) and (outvertex in edge.outvertex) and (edge not in result):
                    result.append(edge)

        return result

    @staticmethod
    def get_coinputs(edge, x_i):
        """ Returns the set of co-inputs for element x_i in the given edge.
        :param edge: Edge object
        :param x_i: invertex element
        :return: set
        """

        coinputs = None
        all_inputs = edge.invertex
        if x_i in list(all_inputs):
            coinputs = list(all_inputs)
            coinputs.remove(x_i)
        if coinputs is not None and len(coinputs) > 0:
            return set(coinputs)
        return None

    @staticmethod
    def get_cooutputs(edge, x_j):
        """ Returns the set of co-outputs for element x_j in the given edge.
        :param edge: Edge object
        :param x_j: outvertex element
        :return: set
        """

        cooutputs = None
        all_outputs = edge.outvertex
        if x_j in list(all_outputs):
            cooutputs = list(all_outputs)
            cooutputs.remove(x_j)
        if cooutputs is not None and len(cooutputs) > 0:
            return set(cooutputs)
        return None

    def adjacency_matrix(self):
        """ Returns the adjacency matrix of the metagraph.
        :return: numpy.matrix
        """

        # get matrix size
        size = len(self.generating_set)
        adj_matrix = MetagraphHelper().get_null_matrix(size, size)

        # one triple for each edge e connecting x_i to x_j
        for i in range(size):
            for j in range(size):
                x_i = list(self.generating_set)[i]
                x_j = list(self.generating_set)[j]
                # multiple edges may exist between x_i and x_j
                edges = self.get_edges(x_i, x_j)
                if len(edges) > 0:
                    triples_list = []
                    for edge in edges:
                        coinputs = self.get_coinputs(edge, x_i)
                        cooutputs = self.get_cooutputs(edge, x_j)
                        triple = Triple(coinputs, cooutputs, edge)
                        if triple not in triples_list:
                            triples_list.append(triple)

                    adj_matrix[i][j] = triples_list

        # return adj_matrix
        # noinspection PyCallingNonCallable
        return matrix(adj_matrix)

    def equivalent(self, metagraph2):
        """Checks if current metagraph is equivalent to the metagraph provided.
        :param metagraph2: Metagraph object
        :return: boolean
        """

        if metagraph2 is None:
            raise MetagraphException('metagraph2', resources['value_null'])

        if self.dominates(metagraph2) and metagraph2.dominates(self):
            return True

        return False

    def add_metagraph(self, metagraph2):
        """ Adds the given metagraph to current and returns the composed result.
        :param metagraph2: Metagraph object
        :return: Metagraph object
        """

        if metagraph2 is None:
            raise MetagraphException('metagraph2', resources['value_null'])

        generating_set1 = self.generating_set
        generating_set2 = metagraph2.generating_set

        if generating_set2 is None or len(generating_set2) == 0:
            raise MetagraphException('metagraph2.generating_set', resources['value_null'])

        # check if the generating sets of the matrices overlap (otherwise no sense in combining metagraphs)
        #intersection=generating_set1.intersection(generating_set2)
        #if intersection==None:
        #    raise MetagraphException('generating_sets', resources['no_overlap'])

        if len(generating_set1.difference(generating_set2)) == 0 and \
           len(generating_set2.difference(generating_set1)) == 0:
            # generating sets are identical..simply add edges
            # size = len(generating_set1)
            for edge in metagraph2.edges:
                if edge not in self.edges:
                    self.add_edge(edge)
        else:
            # generating sets overlap but are different...combine generating sets and then add edges
            # combined_generating_set = generating_set1.union(generating_set2)
            for edge in metagraph2.edges:
                if edge not in self.edges:
                    self.add_edge(edge)

        return self

    def multiply_metagraph(self, metagraph2):
        """ Multiplies the metagraph with that provided and returns the result.
        :param metagraph2: Metagraph object
        :return: Metagraph object
        """

        if metagraph2 is None:
            raise MetagraphException('metagraph2', resources['value_null'])

        generating_set1 = self.generating_set
        generating_set2 = metagraph2.generating_set

        if generating_set2 is None or len(generating_set2) == 0:
            raise MetagraphException('metagraph2.generator_set', resources['value_null'])

        # check generating sets are identical
        if not(len(generating_set1.difference(generating_set2)) == 0 and
           len(generating_set2.difference(generating_set1)) == 0):
            raise MetagraphException('generator_sets', resources['not_identical'])

        adjacency_matrix1 = self.adjacency_matrix().tolist()
        adjacency_matrix2 = metagraph2.adjacency_matrix().tolist()
        size = len(generating_set1)
        resultant_adjacency_matrix = MetagraphHelper().get_null_matrix(size, size)

        for i in range(size):
            for j in range(size):
                resultant_adjacency_matrix[i][j] = MetagraphHelper().multiply_components(
                    adjacency_matrix1, adjacency_matrix2, generating_set1, i, j, size)

        # extract new edge list
        new_edge_list = MetagraphHelper().get_edges_in_matrix(resultant_adjacency_matrix, self.generating_set)
        # clear current edge list and append new
        self.edges = []
        if len(new_edge_list) > 0:
            self.add_edges_from(new_edge_list)

        return self

    def get_closure(self):
        """ Returns the closure matrix (i.e., A*) of the metagraph.
        :return: numpy.matrix
        """

        adjacency_matrix = self.adjacency_matrix().tolist()

        i = 0
        size = len(self.generating_set)
        a = dict()
        a[i] = adjacency_matrix
        a_star = adjacency_matrix

        for i in range(size):
            #print(' iteration %s --------------'%i)
            a[i+1] = MetagraphHelper().multiply_adjacency_matrices(a[i],
                                                                   self.generating_set,
                                                                   adjacency_matrix,
                                                                   self.generating_set)
            #print('multiply_adjacency_matrices complete')
            a_star = MetagraphHelper().add_adjacency_matrices(a_star,
                                                              self.generating_set,
                                                              a[i+1],
                                                              self.generating_set)
            #print('add_adjacency_matrices complete')
            if a[i+1] == a[i]:
                break

        # noinspection PyCallingNonCallable
        return matrix(a_star)

    def get_all_metapaths_from(self, source, target):
        """ Retrieves all metapaths between given source and target in the metagraph.
        :param source: set
        :param target: set
        :return: list of Metapath objects
        """

        if source is None or len(source) == 0:
            raise MetagraphException('source', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('target', resources['value_null'])

        # check subset
        if not source.intersection(self.generating_set) == source:
            raise MetagraphException('source', resources['not_a_subset'])
        if not target.intersection(self.generating_set) == target:
            raise MetagraphException('target', resources['not_a_subset'])

        # compute A* first
        if self.a_star is None:
            #print('computing closure..')
            self.a_star = self.get_closure().tolist()
            #print('closure computation- %s'%(time.time()- start))

        metapaths = []
        all_applicable_input_rows = []
        for x_i in source:
            index = list(self.generating_set).index(x_i)
            if index not in all_applicable_input_rows:
                all_applicable_input_rows.append(index)

        for i in all_applicable_input_rows:
            metapath_exist = False
            cumulative_output = []
            cumulative_edges = []
            for x_j in target:
                j = list(self.generating_set).index(x_j)
                if self.a_star[i][j] is not None:
                    metapath_exist = True
                    # x_j is already an output
                    cumulative_output.append(x_j)
                    triples = MetagraphHelper().get_triples(self.a_star[i][j])
                    for triple in triples:
                        # retain cooutputs
                        output = triple.cooutputs
                        if output is not None and output not in cumulative_output:
                            cumulative_output.append(output)
                        #... and edges
                        if isinstance(triple.edges, Edge):
                            edges = MetagraphHelper().get_edge_list([triple.edges])
                        else:
                            edges = MetagraphHelper().get_edge_list(triple.edges)

                        for edge in edges:
                            if edge not in cumulative_edges:
                                cumulative_edges.append(edge)

            if not metapath_exist:
                return None

            is_subset = True
            for elt in list(target):
                if elt not in cumulative_output:
                    is_subset = False
                    break
            if is_subset:
                for edge in cumulative_edges:
                    if edge not in metapaths:
                        metapaths.append(edge)

        valid_metapaths = []
        from itertools import combinations
        all_subsets = sum(map(lambda r: list(combinations(metapaths, r)), range(1, len(metapaths)+1)), [])
        for path in all_subsets:
            if len(path) <= len(metapaths):
                mp = Metapath(source, target, list(path))
                if self.is_metapath(mp):
                    valid_metapaths.append(mp)

        #print('valid metapath computation- %s'%(time.time()- start))
        return valid_metapaths

    def is_metapath(self, metapath_candidate):
        """ Checks if the given candidate is a metapath.
        :param metapath_candidate: Metapath object
        :return: boolean
        """

        if metapath_candidate is None:
            raise MetagraphException('metapath_candidate', resources['value_null'])

        a_star = self.get_closure().tolist()
        all_applicable_input_rows = []
        for x_i in metapath_candidate.source:
            index = list(self.generating_set).index(x_i)
            if index not in all_applicable_input_rows:
                all_applicable_input_rows.append(index)

        all_applicable_output_cols = []
        for x_j in metapath_candidate.target:
            index = list(self.generating_set).index(x_j)
            if index not in all_applicable_output_cols:
                all_applicable_output_cols.append(index)

        validated_edges = []
        all_inputs = []
        all_outputs = []
        for i in all_applicable_input_rows:
            for j in all_applicable_output_cols:
                if a_star[i][j] is not None:
                    # check simple paths
                    for edge in metapath_candidate.edge_list:
                        for triple in a_star[i][j]:
                            edges1 = MetagraphHelper().get_edges_from_triple_list(triple)
                            if (MetagraphHelper().is_edge_in_list(edge, edges1)) and (edge not in validated_edges):
                                validated_edges.append(edge)

                        for input_elt in list(edge.invertex):
                            if input_elt not in all_inputs:
                                all_inputs.append(input_elt)

                        for output_elt in list(edge.outvertex):
                            if output_elt not in all_outputs:
                                all_outputs.append(output_elt)

        for edge in metapath_candidate.edge_list:
            if edge not in validated_edges:
                return False

        # now check input and output sets
        # check which (subset1.issubset(set(all_inputs).difference(set(all_outputs)))) ?
        if (set(all_inputs).difference(set(all_outputs)).issubset(metapath_candidate.source)) and \
           set(metapath_candidate.target).issubset(all_outputs):
            return True

        return False

    def is_edge_dominant_metapath(self, metapath):
        """ Checks if the given metapath is an edge-dominant metapath.
        :param metapath: Metapath object
        :return: boolean
        """

        if metapath is None:
            raise MetagraphException('metapath', resources['value_null'])

        from itertools import combinations
        # check input metapath is valid
        if not self.is_metapath(metapath):
            return False

        all_subsets = sum(map(lambda r: list(combinations(metapath.edge_list, r)),
                              range(1, len(metapath.edge_list)+1)), [])
        # if one proper subset is a metapath then not edge dominant
        for path in all_subsets:
            # must be a proper subset
            if len(path) < len(metapath.edge_list):
                mp = Metapath(metapath.source, metapath.target, list(path))
                if self.is_metapath(mp):
                    return False

        return True

    def is_input_dominant_metapath(self, metapath):
        """ Checks if the given metapath is an input-dominant metapath.
        :param metapath: Metapath object
        :return: boolean
        """

        if metapath is None:
            raise MetagraphException('metapath', resources['value_null'])

        from itertools import combinations
        # check input metapath is valid
        if not self.is_metapath(metapath):
            return False

        # get all proper subsets of subset1
        all_subsets = sum(map(lambda r: list(combinations(metapath.source, r)), range(1, len(metapath.source)+1)), [])
        # if one proper subset has a metapath to subset2 then not input dominant
        for subset in all_subsets:
            # must be proper subset
            if len(subset) < len(metapath.source):
                if isinstance(subset, tuple):
                    subset = set(list(subset))
                metapath1 = self.get_all_metapaths_from(subset, metapath.target)
                if len(metapath1) > 0:
                    #print('source: %s, target: %s'%(subset, metapath.target))
                    return False
        return True

    def is_dominant_metapath(self, metapath):
        """ Checks if the given metapath is a dominant metapath.
        :param metapath: Metapath object
        :return: boolean
        """

        if metapath is None:
            raise MetagraphException('metapath', resources['value_null'])

        # check input metapath is valid
        if not self.is_metapath(metapath):
            return False

        if (self.is_edge_dominant_metapath(metapath) and
           self.is_input_dominant_metapath(metapath)):
            return True

        return False

    def is_redundant_edge(self, edge, metapath, source, target):
        """ Checks if the given edge is redundant for the given metapath.
        :param edge: Edge object
        :param metapath: Metapath object
        :param source: set
        :param target: set
        :return: boolean
        """

        if edge is None:
            raise MetagraphException('edge', resources['value_null'])
        if metapath is None:
            raise MetagraphException('metapath', resources['value_null'])
        if source is None:
            raise MetagraphException('source', resources['value_null'])
        if target is None:
            raise MetagraphException('target', resources['value_null'])

        # check input metapath is valid
        if not self.is_metapath(metapath):
            raise MetagraphException('metapath', resources['arguments_invalid'])

        from itertools import combinations
        all_subsets = sum(map(lambda r: list(combinations(target, r)), range(1, len(target)+1)), [])
        # get all metapaths from subset1 to proper subsets of subset2
        for subset in all_subsets:
            if len(subset) < len(target):
                metapaths = self.get_all_metapaths_from(source, target)
                # check if edges is in every metapath found
                if metapaths is not None and len(metapaths) > 0:
                    for mp in metapaths:
                        if not MetagraphHelper().is_edge_in_list(edge, mp.edge_list):
                            # redundant
                            return True

                    # non redundant
                    return False
        return False

    def is_cutset(self, edge_list, source, target):
        """ Checks if an edge list is a cutset between a given source and target.
        :param edge_list: list of Edge objects
        :param source: set
        :param target: set
        :return: boolean
        """

        if edge_list is None:
            raise MetagraphException('edges', resources['value_null'])
        if source is None:
            raise MetagraphException('source', resources['value_null'])
        if target is None:
            raise MetagraphException('target', resources['value_null'])

        # remove input edge list from original list
        original_edges = self.edges
        modified_edge_list = []
        for edge1 in original_edges:
            included = False
            for edge2 in edge_list:
                if edge1.invertex == edge2.invertex and edge1.outvertex == edge2.outvertex:
                    included = True
                    break
            if not included:
                modified_edge_list.append(edge1)

        mg = Metagraph(self.generating_set)
        mg.add_edges_from(modified_edge_list)
        #adjacency_matrix = mg.adjacency_matrix().tolist()

        metapaths = mg.get_all_metapaths_from(source, target)

        if metapaths is not None and len(metapaths) > 0:
            return False

        return True

    def get_minimal_cutset(self, source, target):
        """ Retrieves the minimal cutset between a given source and target.
        :param source: set
        :param target: set
        :return: list of Edge objects
        """

        if source is None:
            raise MetagraphException('source', resources['value_null'])
        if target is None:
            raise MetagraphException('target', resources['value_null'])

        metapaths = self.get_all_metapaths_from(source, target)
        if metapaths is None or len(metapaths) == 0:
            return None

        cutsets = []
        from itertools import combinations
        # noinspection PyTypeChecker
        for metapath in metapaths:
            all_combinations = sum(map(lambda r: list(combinations(metapath.edge_list, r)),
                                   range(1, len(metapath.edge_list)+1)), [])
            for combination in all_combinations:
                if self.is_cutset(list(combination), source, target) and list(combination) not in cutsets:
                    cutsets.append(list(combination))

        # return smallest cutset
        if len(cutsets) > 0:
            smallest = cutsets[0]
            for cutset in cutsets:
                if len(cutset) < len(smallest):
                    smallest = cutset
            return smallest

        return None

    def is_bridge(self, edge_list, source, target):
        """ Checks if a given edge list forms a bridge between a source and a target.
        :param edge_list: list of Edge objects
        :param source: set
        :param target: set
        :return: boolean
        """

        if edge_list is None:
            raise MetagraphException('edge_list', resources['value_null'])
        if source is None:
            raise MetagraphException('source', resources['value_null'])
        if target is None:
            raise MetagraphException('target', resources['value_null'])

        if not isinstance(edge_list, list):
            raise MetagraphException('edge_list', resources['arguments_invalid'])

        return self.is_cutset(edge_list, source, target)

    def get_projection(self, generator_subset):
        """ Gets the metagraph projection for a subset of the generating set.
        :param generator_subset: set
        :return: Metagraph object
        """

        if generator_subset is None:
            raise MetagraphException('generator_subset', resources['value_null'])

        # step1. reduce A* by removing unwanted rows, cols
        applicable_rows_and_cols = []
        for x_i in generator_subset:
            index = list(self.generating_set).index(x_i)
            if index not in applicable_rows_and_cols:
                applicable_rows_and_cols.append(index)

        a_star = self.get_closure().tolist()

        # sort list
        applicable_rows_and_cols = sorted(applicable_rows_and_cols)

        size = len(generator_subset)
        a_star_new = MetagraphHelper().get_null_matrix(size, size)

        m = 0
        for i in applicable_rows_and_cols:
            n = 0
            for j in applicable_rows_and_cols:
                a_star_new[m][n] = a_star[i][j]
                n += 1
            m += 1

        # step2. create list L from edges in E (not E') s.t. V_e is a subset of X'
        edge_list1 = []
        all_triples = []
        k = len(applicable_rows_and_cols)
        for i in range(k):
            for j in range(k):
                if a_star_new[i][j] is not None:
                    triples = MetagraphHelper().get_triples(a_star_new[i][j])
                    for triple in triples:
                        if isinstance(triple.edges, Edge):
                            new_triple = Triple(triple.coinputs, triple.cooutputs, [triple.edges])
                            if new_triple not in all_triples:
                                all_triples.append(new_triple)
                            edges = MetagraphHelper().extract_edge_list([triple.edges])
                        else:
                            if triple not in all_triples:
                                all_triples.append(triple)
                            edges = MetagraphHelper().extract_edge_list(triple.edges)

                        # select edges with invertices in generator_subset
                        for edge in edges:
                            if edge.invertex.issubset(set(generator_subset)) and ([edge] not in edge_list1):
                                edge_list1.append([edge])

        # step3. find combinations of triples s.t. union(CI_t_i)\ union(CO_t_i) is a subset of generator_subset
        from itertools import combinations
        all_combinations = sum(map(lambda r: list(combinations(all_triples, r)), range(1, len(all_triples)+1)), [])
        for combination in all_combinations:
            coinput = MetagraphHelper().get_coinputs_from_triples(combination)
            cooutput = MetagraphHelper().get_cooutputs_from_triples(combination)
            diff = set(coinput).difference(set(cooutput))
            if diff.issubset(set(generator_subset)):
                # add edges in combination to L
                edges2 = MetagraphHelper().get_edges_from_triple_list(list(combination))
                included = MetagraphHelper().is_edge_list_included(edges2, edge_list1)
                if not included:
                    edge_list1.append(edges2)

        # step4. construct L0 from L
        triples_list_l0 = []
        for element in edge_list1:
            all_inputs = MetagraphHelper().get_netinputs(element)
            all_outputs = MetagraphHelper().get_netoutputs(element)
            net_inputs = list(set(all_inputs).difference(all_outputs))
            net_outputs = all_outputs
            new_triple = Triple(set(net_inputs), set(net_outputs), element)
            if new_triple not in triples_list_l0:
                triples_list_l0.append(new_triple)

        # step5. reduce L0
        to_eliminate = []
        for i in triples_list_l0:
            for j in triples_list_l0:
                if i != j:
                    # check if i is subsumed by j
                    edges_i = MetagraphHelper().get_edge_list(i.edges)
                    edges_j = MetagraphHelper().get_edge_list(j.edges)
                    outputs_i = i.cooutputs
                    outputs_j = j.coinputs

                    # check j's edges are a subset of i's edges
                    subset = True
                    for edge in edges_j:
                        if edge not in edges_i:
                            subset = False
                            break

                    inclusive = True
                    if subset:
                        # edges form a subset..check outputs are inclusive
                        outputs_j_in_x = []
                        for output in outputs_j:
                            if (output in generator_subset) and (output not in outputs_j_in_x):
                                outputs_j_in_x.append(output)

                        outputs_i_in_x = []
                        for output in outputs_i:
                            if (output in generator_subset) and (output not in outputs_i_in_x):
                                outputs_i_in_x.append(output)

                        for output in outputs_i_in_x:
                            if output not in outputs_j_in_x:
                                inclusive = False
                                break

                        if inclusive and (i not in to_eliminate):
                            to_eliminate.append(i)
                            break

        for elt in to_eliminate:
            triples_list_l0.remove(elt)

        to_drop = []

        for i in triples_list_l0:
            for j in triples_list_l0:
                if i != j:
                    inputs_i = i.coinputs
                    inputs_j = j.coinputs
                    outputs_i = i.cooutputs
                    outputs_j = j.cooutputs

                    # check if input and output of j are a subset of i
                    input_subset = True
                    for input_elt in inputs_j:
                        if input_elt not in inputs_i:
                            input_subset = False
                            break

                    if input_subset:
                        output_subset = True
                        for output in outputs_j:
                            if output not in outputs_i:
                                output_subset = False
                                break

                        if output_subset:
                            for elt in j.cooutputs:
                                i.cooutputs.remove(elt)
                            if (i.cooutputs is None or len(i.cooutputs) == 0) and (i not in to_drop):
                                to_drop.append(i)

        for item in to_drop:
            triples_list_l0.remove(item)

        #step6. merge triples based on identical inputs and outputs
        triples_to_merge = dict()
        index = 0
        for triple1 in triples_list_l0:
            for triple2 in triples_list_l0:
                if triple1 != triple2:
                    # merge if same input and output
                    if triple1.coinputs == triple2.coinputs and triple1.cooutputs == triple2.cooutputs:
                        if index not in triples_to_merge:
                            triples_to_merge[index] = []
                        if triple2 not in triples_to_merge[index]:
                            triples_to_merge[index].append(triple2)
            index += 1

        post_merge_triples = dict()
        for index, triples_list in triples_to_merge.iteritems():
            triple1 = triples_to_merge[index]
            if triple1 in triples_list_l0:
                triples_list_l0.remove(triple1)
                for triple2 in triples_list:
                    if triple2 in triples_list_l0:
                        triples_list_l0.remove(triple2)
                    if index not in post_merge_triples:
                        post_merge_triples[index] = Triple(triple1.coinputs, triple1.cooutputs,
                                                           [triple1.edges, triple2.edges])
                    else:
                        post_merge_triples[index].edges.append(triple2.edges)
                triples_list_l0.append(post_merge_triples[index])

        #step7. and triples with identical inputs only
        triples_to_merge = dict()
        index = 0
        for triple1 in triples_list_l0:
            for triple2 in triples_list_l0:
                if triple1 != triple2:
                    # merge if same input
                    if triple1.coinputs == triple2.coinputs:
                        if index not in triples_to_merge:
                            triples_to_merge[index] = []
                        if triple2 not in triples_to_merge[index]:
                            triples_to_merge[index].append(triple2)
            index += 1

        triple_list_l0_copy = copy.copy(triples_list_l0)

        post_merge_triples = dict()
        for index, triples_list in triples_to_merge.iteritems():
            triple1 = triple_list_l0_copy[index]
            if triple1 in triples_list_l0:
                triples_list_l0.remove(triple1)
                for triple2 in triples_list:
                    if triple2 in triples_list_l0:
                        triples_list_l0.remove(triple2)
                    if index not in post_merge_triples:
                        edges_to_merge = list(triple1.edges)
                        for elt in list(triple2.edges):
                            if elt not in edges_to_merge:
                                edges_to_merge.append(elt)
                        post_merge_triples[index] = Triple(triple1.coinputs, triple1.cooutputs.union(triple2.cooutputs),
                                                           edges_to_merge)
                    else:
                        edges_to_merge = list(post_merge_triples[index].edges)
                        for elt in list(triple2.edges):
                            if elt not in edges_to_merge:
                                edges_to_merge.append(elt)
                        post_merge_triples[index] = Triple(post_merge_triples[index].coinputs,
                                                           post_merge_triples[index].cooutputs.union(triple2.cooutputs),
                                                           edges_to_merge)  # triple1
                triples_list_l0.append(post_merge_triples[index])

        temp_list = []
        for triple in triples_list_l0:
            # remove all inputs and outputs that are not in generator_subset
            valid_inputs = triple.coinputs.intersection(set(generator_subset))
            valid_outputs = triple.cooutputs.intersection(set(generator_subset))
            new_triple = Triple(valid_inputs, valid_outputs, triple.edges)
            if new_triple not in temp_list:
                temp_list.append(new_triple)

        # remove any tuples with zero input or output
        final_triples_list = []
        for triple in temp_list:
            if triple.coinputs is not None and triple.cooutputs is not None and \
               len(triple.coinputs) > 0 and len(triple.cooutputs) > 0 and \
               (triple not in final_triples_list):
                final_triples_list.append(triple)

        edge_list = []
        for triple in final_triples_list:
            edge = Edge(triple.coinputs, triple.cooutputs, None, repr(triple.edges))
            if edge not in edge_list:
                edge_list.append(edge)

        if edge_list is None or len(edge_list) == 0:
            return None

        mg = Metagraph(set(generator_subset))
        mg.add_edges_from(edge_list)

        return mg

    def incidence_matrix(self):
        """ Gets the metagraph projection for a subset of the generating set.
        :return: numpy.matrix
        """

        rows = len(self.generating_set)
        cols = len(self.edges)

        incidence_matrix = MetagraphHelper().get_null_matrix(rows, cols)

        for i in range(rows):
            x_i = list(self.generating_set)[i]
            for j in range(cols):
                e_j = self.edges[j]
                if x_i in e_j.invertex:
                    incidence_matrix[i][j] = -1
                elif x_i in e_j.outvertex:
                    incidence_matrix[i][j] = 1
                else:
                    incidence_matrix[i][j] = None

        # noinspection PyCallingNonCallable
        return matrix(incidence_matrix)

    def get_inverse(self):
        """ Gets the inverse metagraph.
        :return: Metagraph object
        """

        incidence_m = self.incidence_matrix().tolist()

        edge_list = []
        # step1: extract indices
        col_index = 0
        for i in range(len(incidence_m[0])):
            negative_item_indices = []
            positive_item_indices = []
            column = [row[col_index] for row in incidence_m]
            row_index = 0
            for item1 in column:
                if item1 == -1:
                   # get all elements with +1 across the row
                    row = incidence_m[row_index]
                    eligible = []
                    local_index = 0
                    for item2 in row:
                        if item2 == 1 and local_index not in eligible:
                            eligible.append(local_index)
                        local_index += 1

                    if len(eligible) == 0:
                        row_index += 1  # debug dr check this
                        continue

                    # TODO: how do we handle multiple occurrences of +1?
                    # keep a track of -1 and + 1 indices
                    if (row_index, col_index) not in negative_item_indices:
                        negative_item_indices.append((row_index, col_index))

                    for local_index in eligible:
                        if (row_index, local_index) not in positive_item_indices:
                            positive_item_indices.append((row_index, local_index))

                row_index += 1

            # construct edges from indices
            invertex = []
            outvertex = []
            edge_label = None
            for negative_item_index in negative_item_indices:
                if repr(self.edges[negative_item_index[1]]) not in outvertex:
                    outvertex.append(repr(self.edges[negative_item_index[1]]))

            for positive_item_index in positive_item_indices:
                if repr(self.edges[positive_item_index[1]]) not in invertex:
                    invertex.append(repr(self.edges[positive_item_index[1]]))

                # generate label
                if edge_label is None:
                    edge_label = '<%s,%s>' % (list(self.generating_set)[positive_item_index[0]],
                                              repr(self.edges[positive_item_index[1]]))
                else:
                    edge_label += ', <%s,%s>' % (list(self.generating_set)[positive_item_index[0]],
                                                 repr(self.edges[positive_item_index[1]]))

            if invertex is not None and outvertex is not None and len(invertex) > 0 and len(outvertex) > 0:
                edge = Edge(set(invertex), set(outvertex), None, edge_label)
                if edge not in edge_list:
                    edge_list.append(edge)
            col_index += 1

        # compress the edges
        compressed_edges = []
        for edge1 in edge_list:
            compressed = False
            for edge2 in edge_list:
                if edge1 != edge2:
                    if edge1.invertex == edge2.invertex and edge1.label == edge2.label:
                        new_edge = Edge(edge1.invertex, edge1.outvertex.union(edge2.outvertex), None, edge1.label)
                        if not MetagraphHelper().is_edge_in_list(new_edge, compressed_edges):
                            compressed_edges.append(new_edge)
                        compressed = True
            if not compressed and (not MetagraphHelper().is_edge_in_list(edge1, compressed_edges)):
                compressed_edges.append(edge1)

        # add links to alpha and beta
        row_index = 0
        occurrences = lambda s, lst: (y for y, e in enumerate(lst) if e == s)
        for row in incidence_m:
            if row.__contains__(-1) and (not row.__contains__(1)):
                col_indices = list(occurrences(-1, row))
                for col_index in col_indices:
                    label = '<%s, alpha>' % (list(self.generating_set)[row_index])
                    new_edge = Edge({'alpha'}, {repr(self.edges[col_index])}, None, label)
                    if not MetagraphHelper().is_edge_in_list(new_edge, compressed_edges):
                        compressed_edges.append(new_edge)

            elif row.__contains__(1) and (not row.__contains__(-1)):
                col_indices = list(occurrences(1, row))
                for col_index in col_indices:
                    label = '<%s, %s>' % (list(self.generating_set)[row_index], repr(self.edges[col_index]))
                    new_edge = Edge({repr(self.edges[col_index])}, {'beta'}, None, label)
                    if not MetagraphHelper().is_edge_in_list(new_edge, compressed_edges):
                        compressed_edges.append(new_edge)
            row_index += 1

        mg = Metagraph(MetagraphHelper().get_generating_set(compressed_edges))
        mg.add_edges_from(compressed_edges)
        return mg

    def get_efm(self, generator_subset):
        """ Gets the element-flow metagraph.
        :param generator_subset: set
        :return: Metagraph object
        """

        if generator_subset is None or len(generator_subset) == 0:
            raise MetagraphException('generator_subset', resources['value_null'])

        incidence_m = self.incidence_matrix().tolist()
        excluded = self.generating_set.difference(generator_subset)

        # compute G1 and G2
        applicable_rows = []
        for x_i in generator_subset:
            index = list(self.generating_set).index(x_i)
            if index not in applicable_rows:
                applicable_rows.append(index)

        # sort list
        applicable_rows = sorted(applicable_rows)
        inapplicable_rows = sorted(set(range(len(self.generating_set))).difference(applicable_rows))

        rows1 = len(generator_subset)
        cols1 = len(incidence_m[0])
        rows2 = len(excluded)
        g1 = MetagraphHelper().get_null_matrix(rows1, cols1)
        g2 = MetagraphHelper().get_null_matrix(rows2, cols1)

        m = 0
        for i in applicable_rows:
            n = 0
            for j in range(cols1):
                g1[m][n] = incidence_m[i][j]
                n += 1
            m += 1

        m = 0
        for i in inapplicable_rows:
            n = 0
            for j in range(cols1):
                g2[m][n] = incidence_m[i][j]
                n += 1
            m += 1

        g1_t = MetagraphHelper().transpose_matrix(g1)
        mult_r = MetagraphHelper().custom_multiply_matrices(g2, g1_t, self.edges)
        row_index = 0
        edge_list = []
        lookup = dict()
        for row in mult_r:
            col_index = 0
            invertices = []
            outvertices = []
            for elt in row:
                if len(elt) > 0 and isinstance(list(elt)[0], tuple):
                    extracted = list(elt)[0]
                    if 1 in extracted:
                        invertex = []
                        local_indices = [row.index(elt2) for elt2 in row if elt.issubset(elt2)]
                        for local_index in local_indices:
                            value = list(self.generating_set)[applicable_rows[local_index]]
                            if value not in invertex:
                                invertex.append(value)

                        if set(invertex) not in invertices:
                            invertices.append(set(invertex))
                        if repr(invertex) not in lookup:
                            lookup[repr(invertex)] = extracted[1]

                    elif -1 in extracted:
                        outvertex = []
                        local_indices = [row.index(elt2) for elt2 in row if elt.issubset(elt2)]
                        for local_index in local_indices:
                            value = list(self.generating_set)[applicable_rows[local_index]]
                            if value not in outvertex:
                                outvertex.append(value)

                        if set(outvertex) not in outvertices:
                            outvertices.append(set(outvertex))
                        if repr(outvertex) not in lookup:
                            lookup[repr(outvertex)] = extracted[1]

                col_index += 1

            # combine the invertices and outvertices
            for invertex in invertices:
                for outvertex in outvertices:
                    # create flow composition
                    label = '%s <%s; %s>' % (list(self.generating_set)[inapplicable_rows[row_index]],
                                             lookup[repr(list(invertex))], lookup[repr(list(outvertex))])
                    edge = Edge(invertex, outvertex, None, label)
                    if not MetagraphHelper().is_edge_in_list(edge, edge_list):
                        edge_list.append(edge)

            row_index += 1

        # combine edges
        final_edge_list = []
        for edge1 in edge_list:
            match = False
            for edge2 in edge_list:
                if edge1 != edge2:
                    if edge1.invertex == edge2.invertex and edge1.outvertex == edge1.outvertex:
                        match = True
                        comp1 = MetagraphHelper().extract_edge_label_components(edge1.label)
                        comp2 = MetagraphHelper().extract_edge_label_components(edge2.label)
                        combined = (comp1[0].union(comp2[0]), comp1[1].union(comp2[1]), comp1[2].union(comp2[2]))
                        label = '%s <%s; %s>' % (list(combined[0]), list(combined[1]), list(combined[2]))
                        combined_edge = Edge(edge1.invertex, edge1.outvertex, None, label)
                        if not MetagraphHelper().is_edge_in_list(combined_edge, final_edge_list):
                            final_edge_list.append(combined_edge)
            if not match:
                if not MetagraphHelper().is_edge_in_list(edge1, final_edge_list):
                    final_edge_list.append(edge1)

        if len(final_edge_list) > 0:
            gen_set = MetagraphHelper().get_generating_set(final_edge_list)
            mg = Metagraph(gen_set)
            mg.add_edges_from(final_edge_list)
            return mg

        return None

    def dominates(self, metagraph2):
        """Checks if the metagraph dominates that provided.
        :param metagraph2: Metagraph object
        :return: boolean
        """

        if metagraph2 is None:
            raise MetagraphException('metagraph2', resources['value_null'])

        #adjacency_matrix = self.adjacency_matrix().tolist()
        #all_metapaths1 = []

        from itertools import combinations
        all_sources1 = sum(map(lambda r: list(combinations(self.generating_set, r)),
                               range(1, len(self.generating_set))), [])
        all_targets1 = copy.copy(all_sources1)

        all_sources2 = sum(map(lambda r: list(combinations(metagraph2.generating_set, r)),
                               range(1, len(metagraph2.generating_set))), [])
        all_targets2 = copy.copy(all_sources2)

        all_metapaths1 = []
        i = 1
        #s1 =  len(all_sources1)
        #t1 =  len(all_targets1)
        #s2 =  len(all_sources2)
        #t2 =  len(all_targets2)

        for source in all_sources1:
            for target in all_targets1:
                if source != target:
                    mp = self.get_all_metapaths_from(set(source), set(target))
                    if mp is not None and len(mp) > 0 and (mp not in all_metapaths1):
                        all_metapaths1.append(mp)
                    #print(i)
                    i += 1

        all_metapaths2 = []
        for source in all_sources2:
            for target in all_targets2:
                if source != target:
                    mp = self.get_all_metapaths_from(set(source), set(target))
                    if mp is not None and len(mp) > 0 and (mp not in all_metapaths2):
                        all_metapaths2.append(mp)

        for mp1 in all_metapaths2:
            dominated = False
            for mp2 in all_metapaths1:
                if mp2.dominates(mp1):
                    dominated = True
                    break
            if not dominated:
                return False

        return True

    def __repr__(self):
        edge_desc = [repr(edge) for edge in self.edges]
        full_desc = ''
        for desc in edge_desc:
            if full_desc == '':
                full_desc = desc
            else:
                full_desc += ", " + desc
        desc = '%s(%s)' % (str(type(self)), full_desc)
        desc = desc.replace('\\', '')
        return desc


class ConditionalMetagraph(Metagraph):
    """ Represents a conditional metagraph that is instantiated using a set of variables and a set of propositions.
    """

    def __init__(self, variables_set, propositions_set):
        if not isinstance(variables_set, set):
            raise MetagraphException('variable_set', resources['format_invalid'])
        if not isinstance(propositions_set, set):
            raise MetagraphException('propositions_set', resources['format_invalid'])
        if len(variables_set.intersection(propositions_set)) > 0:
            raise MetagraphException('variables_and_propositions', resources['partition_invalid'])
        self.nodes = []
        self.edges = []
        self.mg = None
        self.variables_set = variables_set
        self.propositions_set = propositions_set
        self.generating_set = variables_set.union(propositions_set)
        super(ConditionalMetagraph, self).__init__(self.generating_set)

    def add_edges_from(self, edge_list):
        """ Adds the given list of edges to the conditional metagraph.
        :param edge_list: list of Edge objects
        :return: None
        """
        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        for edge in edge_list:
            if not isinstance(edge, Edge):
                raise MetagraphException('edge', resources['format_invalid'])
            if len(edge.invertex.union(edge.outvertex)) == 0:
                raise MetagraphException('edge', resources['value_null'])
             # if outvertex contains a proposition, the outvertex cannot contain any other element
            for proposition in self.propositions_set:
                if proposition in edge.outvertex:
                    if len(edge.outvertex) > 1:
                        raise MetagraphException('edge', resources['value_invalid'])

        for edge in edge_list:
            node1 = Node(edge.invertex)
            node2 = Node(edge.outvertex)
            if not MetagraphHelper().is_node_in_list(node1, self.nodes):
                self.nodes.append(node1)
            if not MetagraphHelper().is_node_in_list(node2, self.nodes):
                self.nodes.append(node2)
            if edge not in self.edges:
                self.edges.append(edge)

    def get_context(self, true_propositions, false_propositions):
        """Retrieves the context metagraph for the given true and false propositions.
        :param true_propositions: set
        :param false_propositions: set
        :return: ConditionalMetagraph object
        """
        if true_propositions is None or len(true_propositions) == 0:
            raise MetagraphException('true_propositions', resources['value_null'])
        if false_propositions is None or len(false_propositions) == 0:
            raise MetagraphException('false_propositions', resources['value_null'])

        for proposition in true_propositions:
            if proposition not in self.propositions_set:
                raise MetagraphException('true_propositions', resources['range_invalid'])
        for proposition in false_propositions:
            if proposition not in self.propositions_set:
                raise MetagraphException('false_propositions', resources['range_invalid'])

        edges_to_remove = []
        edges_copy = copy.copy(self.edges)
        for edge in edges_copy:
            for proposition in list(true_propositions):
                if proposition in edge.invertex:
                    edge.invertex.difference({proposition})
                    # remove if this results in an invertex that is null
                    if len(edge.invertex) == 0 and edge not in edges_to_remove:
                        edges_to_remove.append(edge)
                if proposition in edge.outvertex:
                    edge.outvertex.difference({proposition})
                    # remove if this results in an outvertex that is null
                    if len(edge.outvertex) == 0 and edge not in edges_to_remove:
                        edges_to_remove.append(edge)

            for proposition in list(false_propositions):
                if proposition in edge.invertex or proposition in edge.outvertex:
                    # remove edge
                    if edge not in edges_to_remove:
                        edges_to_remove.append(edge)

        # create new conditional metagraph describing context
        context = ConditionalMetagraph(self.variables_set, self.propositions_set)
        for edge in edges_to_remove:
            if edge in edges_copy:
                edges_copy.remove(edge)
        context.add_edges_from(edges_copy)

        return context

    def get_projection(self, variables_subset):
        """ Gets the conditional metagraph projection for a subset of its variable set.
        :param variables_subset: set
        :return: Metagraph object
        """
        if variables_subset is None or len(variables_subset) == 0:
            raise MetagraphException('variables_subset', resources['value_null'])

        subset = variables_subset.union(self.propositions_set)
        generator_set = self.variables_set.union(self.propositions_set)
        mg = Metagraph(generator_set)
        mg.add_edges_from(self.edges)
        return mg.get_projection(subset)

    def get_all_metapaths_from(self, source, target):
        """ Retrieves all metapaths between given source and target in the conditional metagraph.
        :param source: set
        :param target: set
        :return: list of Metapath objects
        """

        if source is None or len(source) == 0:
            raise MetagraphException('subset1', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('subset2', resources['value_null'])
        if not source.issubset(self.generating_set):
            raise MetagraphException('subset1', resources['not_a_subset'])
        if not target.issubset(self.generating_set):
            #print('error: %s - %s'%(target, self.generating_set))
            raise MetagraphException('subset2', resources['not_a_subset'])

        generator_set = self.variables_set.union(self.propositions_set)
        if self.mg is None:
            self.mg = Metagraph(generator_set)
            self.mg.add_edges_from(self.edges)
        ## debug dr:: replace source below with this- source.union(self.propositions_set)
        return self.mg.get_all_metapaths_from(source, target)  # source

    def get_all_metapaths(self):
        """ Retrieves all metapaths in the conditional metagraph.
        :return: List of Metapath objects
        """

        #TODO: should we consider metapaths involving node groups?
        #all_subsets=sum(map(lambda r: list(combinations(self.nodes, r)), range(1, len(self.nodes)+1)), [])
        all_subsets = self.nodes

        cap_reached = False
        all_metapaths = []
        for subset1 in all_subsets:
            for subset2 in all_subsets:
                if subset1 != subset2:
                    # TODO: can source and target in a metapath overlap?
                    if not MetagraphHelper().nodes_overlap([subset1], [subset2]):  # (list(subset1), list(subset2)):
                        #print('subset1: %s'%set(subset1))
                        #print('subset2: %s'%set(subset2))
                        source = MetagraphHelper().get_element_set([subset1])  # (list(subset1))
                        target = MetagraphHelper().get_element_set([subset2])  # (list(subset2))
                        mps = self.get_all_metapaths_from(source, target)
                        if mps is None or len(mps) == 0:
                            continue
                        # noinspection PyTypeChecker
                        for mp in mps:
                            if mp not in all_metapaths:
                                all_metapaths.append(mp)
                        if len(all_metapaths) >= 10:
                            cap_reached = True
                            break
            if cap_reached:
                break

        return all_metapaths

    def has_conflicts(self, metapath):
        """Checks whether the given metapath has any conflicts.
        :param metapath: Metapath object
        :return: boolean
        """

        invertices = set()
        edges = metapath.edge_list
        for edge in edges:
            invertices = invertices.union(edge.invertex)

        potential_conflicts_set = invertices.intersection(self.propositions_set)
        if self.edge_attributes_conflict(potential_conflicts_set):
            return True

        return False

    def has_redundancies(self, metapath):
        """ Checks if given metapath has redundancies.
        :param metapath: Metapath object
        :return: boolean
        """

        # check input metapath is valid
        if not self.is_metapath(metapath):
            raise MetagraphException('metapath', resources['arguments_invalid'])

        return not self.is_dominant_metapath(metapath)

    def edge_attributes_conflict(self, potential_conflicts_set):
        """ Checks if given edge attributes conflict.
        :param potential_conflicts_set: set
        :return: boolean
        """

        if potential_conflicts_set is None:
            raise MetagraphException('potential_conflicts_set', resources['value_null'])

        # currently checks if actions conflict
        # extend later to include active times etc
        actions = self.get_actions(potential_conflicts_set)
        #TODO: extend to support more attributes

        if len(actions) > 1:
            return True

        return False

    @staticmethod
    def get_actions(attributes):
        """ Filters the given list of attributes and returns a list of action-attribute values.
        :param attributes:  list
        :return: list of strings
        """

        if attributes is None:
            raise MetagraphException('attributes', resources['value_null'])
        actions = []
        for attribute in attributes:
            if 'action' in attribute:
                value = attribute.replace('action=', '')
                if value not in actions:
                    actions.append(value)
        return actions

    def is_connected(self, source, target, logical_expressions, interpretations):
        """Checks if subset1 is connected to subset2.
        :param source: set
        :param target: set
        :param logical_expressions: list of strings
        :param interpretations: lists of tuples
        :return: boolean
        """

        if source is None or len(source) == 0:
            raise MetagraphException('source', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('target', resources['value_null'])
        if logical_expressions is None or len(logical_expressions) == 0:
            raise MetagraphException('logical_expressions', resources['value_null'])
        if interpretations is None or len(interpretations) == 0:
            raise MetagraphException('interpretations', resources['value_null'])
        if not source.issubset(self.variables_set):
            raise MetagraphException('source', resources['not_a_subset'])
        if not target.issubset(self.variables_set):
            raise MetagraphException('target', resources['not_a_subset'])

        # check expressions are over X_p
        for logical_expression in logical_expressions:
            logical_expression_copy = copy.copy(logical_expression)
            logical_expression_copy = logical_expression_copy.replace('.', ' ')
            logical_expression_copy = logical_expression_copy.replace('|', ' ')
            logical_expression_copy = logical_expression_copy.replace('!', ' ')
            logical_expression_copy = logical_expression_copy.replace('(', '')
            logical_expression_copy.replace(')', '')
            items = logical_expression_copy.split(' ')
            for item in items:
                item = item.replace(' ', '')
                if item != '' and item not in self.propositions_set:
                    raise MetagraphException('logical_expression', resources['arguments_invalid'])

        # check metapath exists for at least one interpretation
        for interpretation in interpretations:
            true_propositions = []
            false_propositions = []
            for tuple_elt in interpretation:
                if tuple_elt[0] not in self.propositions_set:
                    raise MetagraphException('interpretations', resources['arguments_invalid'])
                if tuple_elt[1] and tuple_elt[0] not in true_propositions:
                    true_propositions.append(tuple_elt[0])
                elif tuple_elt[0] not in true_propositions:
                    false_propositions.append(tuple_elt[0])

            # compute context metagraph
            context = self.get_context(true_propositions, false_propositions)
            metapaths = context.get_all_metapaths_from(source, target)

            if metapaths is not None and len(metapaths) >= 1:
                return True

        return False

    def is_fully_connected(self, source, target, logical_expressions, interpretations):
        """Checks if subset1 is fully connected to subset2.
        :param source: set
        :param target: set
        :param logical_expressions: list of strings
        :param interpretations: lists of tuples
        :return: boolean
        """

        if source is None or len(source) == 0:
            raise MetagraphException('source', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('target', resources['value_null'])
        if logical_expressions is None or len(logical_expressions) == 0:
            raise MetagraphException('logical_expressions', resources['value_null'])
        if interpretations is None or len(interpretations) == 0:
            raise MetagraphException('interpretations', resources['value_null'])
        if not source.issubset(self.variables_set):
            raise MetagraphException('source', resources['not_a_subset'])
        if not target.issubset(self.variables_set):
            raise MetagraphException('target', resources['not_a_subset'])

        # check expressions are over X_p
        for logical_expression in logical_expressions:
            logical_expression_copy = copy.copy(logical_expression)
            logical_expression_copy = logical_expression_copy.replace('.', ' ')
            logical_expression_copy = logical_expression_copy.replace('|', ' ')
            logical_expression_copy = logical_expression_copy.replace('!', ' ')
            logical_expression_copy = logical_expression_copy.replace('(', '')
            logical_expression_copy.replace(')', '')
            items = logical_expression_copy.split(' ')
            for item in items:
                item = item.replace(' ', '')
                if item != '' and item not in self.propositions_set:
                    raise MetagraphException('logical_expression', resources['arguments_invalid'])

        # check metapath exists for every interpretation
        for interpretation in interpretations:
            true_propositions = []
            false_propositions = []
            for tuple_elt in interpretation:
                if tuple_elt[0] not in self.propositions_set:
                    raise MetagraphException('interpretations', resources['arguments_invalid'])
                if tuple_elt[1] and tuple_elt[0] not in true_propositions:
                    true_propositions.append(tuple_elt[0])
                elif tuple_elt[0] not in true_propositions:
                    false_propositions.append(tuple_elt[0])

            # compute context metagraph
            context = self.get_context(true_propositions, false_propositions)
            metapaths = context.get_all_metapaths_from(source, target)

            if not(metapaths is not None and len(metapaths) >= 1):
                return False

        return True

    def is_redundantly_connected(self, source, target, logical_expressions, interpretations):
        """Checks if subset1 is non-redundantly connected to subset2.
        :param source: set
        :param target: set
        :param logical_expressions: list of strings
        :param interpretations: lists of tuples
        :return: boolean
        """

        if source is None or len(source) == 0:
            raise MetagraphException('source', resources['value_null'])
        if target is None or len(target) == 0:
            raise MetagraphException('target', resources['value_null'])
        if logical_expressions is None or len(logical_expressions) == 0:
            raise MetagraphException('logical_expressions', resources['value_null'])
        if interpretations is None or len(interpretations) == 0:
            raise MetagraphException('interpretations', resources['value_null'])
        if not source.issubset(self.variables_set):
            raise MetagraphException('source', resources['not_a_subset'])
        if not target.issubset(self.variables_set):
            raise MetagraphException('target', resources['not_a_subset'])

        # check expressions are over X_p
        for logical_expression in logical_expressions:
            logical_expression_copy = copy.copy(logical_expression)
            logical_expression_copy = logical_expression_copy.replace('.', ' ')
            logical_expression_copy = logical_expression_copy.replace('|', ' ')
            logical_expression_copy = logical_expression_copy.replace('!', ' ')
            logical_expression_copy = logical_expression_copy.replace('(', '')
            logical_expression_copy.replace(')', '')
            items = logical_expression_copy.split(' ')
            for item in items:
                item = item.replace(' ', '')
                if item != '' and item not in self.propositions_set:
                    raise MetagraphException('logical_expression', resources['arguments_invalid'])

        # check metapath exists for every interpretation
        for interpretation in interpretations:
            true_propositions = []
            false_propositions = []
            for tuple_elt in interpretation:
                if tuple_elt[0] not in self.propositions_set:
                    raise MetagraphException('interpretations', resources['arguments_invalid'])
                if tuple_elt[1] and tuple_elt[0] not in true_propositions:
                    true_propositions.append(tuple_elt[0])
                elif tuple_elt[0] not in true_propositions:
                    false_propositions.append(tuple_elt[0])

            # compute context metagraph
            context = self.get_context(true_propositions, false_propositions)
            metapaths = context.get_all_metapaths_from(source, target)

            if metapaths is not None and len(metapaths) > 1:
                return False

        return True

    def is_non_redundant(self, logical_expressions, interpretations):
        """ Checks if a conditional metagraph is non redundant.
        :param logical_expressions: list of strings
        :param interpretations: lists of tuples
        :return: boolean
        """

        if logical_expressions is None or len(logical_expressions) == 0:
            raise MetagraphException('logical_expressions', resources['value_null'])
        if interpretations is None or len(interpretations) == 0:
            raise MetagraphException('interpretations', resources['value_null'])

        # check expressions are over X_p
        for logical_expression in logical_expressions:
            logical_expression_copy = copy.copy(logical_expression)
            logical_expression_copy = logical_expression_copy.replace('.', ' ')
            logical_expression_copy = logical_expression_copy.replace('|', ' ')
            logical_expression_copy = logical_expression_copy.replace('!', ' ')
            logical_expression_copy = logical_expression_copy.replace('(', '')
            logical_expression_copy.replace(')', '')
            items = logical_expression_copy.split(' ')
            for item in items:
                item = item.replace(' ', '')
                if item != '' and item not in self.propositions_set:
                    raise MetagraphException('logical_expression', resources['arguments_invalid'])

        # check metapath exists for at least one interpretation
        for interpretation in interpretations:
            true_propositions = []
            false_propositions = []
            for tuple_elt in interpretation:
                if tuple_elt[0] not in self.propositions_set:
                    raise MetagraphException('interpretations', resources['arguments_invalid'])
                if tuple_elt[1] and tuple_elt[0] not in true_propositions:
                    true_propositions.append(tuple_elt[0])
                elif tuple_elt[0] not in true_propositions:
                    false_propositions.append(tuple_elt[0])

            # compute context metagraph
            context = self.get_context(true_propositions, false_propositions)

            for x in self.variables_set:
                edge_list = []
                for edge in context.edges:
                    if x in edge.outvertex and edge not in edge_list:
                        edge_list.append(edge)
                if len(edge_list) > 1:
                    return False

            return True

    def __repr__(self):
        edge_desc = [repr(edge) for edge in self.edges]
        full_desc = ''
        for desc in edge_desc:
            if full_desc == '':
                full_desc = desc
            else:
                full_desc += ', ' + desc
        desc = '%s(%s)' % (str(type(self)), full_desc)
        desc = desc.replace('\\', '')
        return desc


# noinspection PyShadowingNames,PyShadowingNames
@singleton
class MetagraphHelper:
    """ Helper class that facilitates metagraph operations.
    """

    def __init__(self):
        pass

    def add_adjacency_matrices(self, adjacency_matrix1, generator_set1, adjacency_matrix2, generator_set2):
        """ Adds the two adjacency matrices provided and returns a combined matrix.
        :param adjacency_matrix1: numpy.matrix
        :param generator_set1: set
        :param adjacency_matrix2: numpy.matrix
        :param generator_set2: set
        :return: numpy.matrix
        """

        if adjacency_matrix1 is None:
            raise MetagraphException('adjacency_matrix1', resources['value_null'])
        if adjacency_matrix2 is None:
            raise MetagraphException('adjacency_matrix2', resources['value_null'])

        if generator_set1 is None:
            raise MetagraphException('generator_set1', resources['value_null'])
        if generator_set2 is None:
            raise MetagraphException('generator_set2', resources['value_null'])

        # check if the generating sets of the matrices overlap (otherwise no sense in combining metagraphs)
        intersection = generator_set1.intersection(generator_set2)
        if intersection is None:
            raise MetagraphException('generator_sets', resources['no_overlap'])

        #combined_adjacency_matrix = None
        if len(generator_set1.difference(generator_set2)) == 0 and len(generator_set2.difference(generator_set1)) == 0:
            # generating sets are identical..use adjacency matrices as is
            size = len(generator_set1)
            combined_adjacency_matrix = MetagraphHelper().get_null_matrix(size, size)
            for i in range(size):
                for j in range(size):
                    # take the union
                    if adjacency_matrix1[i][j] is None:
                        combined_adjacency_matrix[i][j] = adjacency_matrix2[i][j]
                    elif adjacency_matrix2[i][j] is None:
                        combined_adjacency_matrix[i][j] = adjacency_matrix1[i][j]
                    else:
                        temp = list()
                        temp.append(adjacency_matrix1[i][j])
                        temp.append(adjacency_matrix2[i][j])
                        combined_adjacency_matrix[i][j] = temp

        else:
            # generating sets overlap but are different...need to redefine adjacency matrices before adding them
            combined_generating_set = generator_set1.union(generator_set2)
            mg1 = Metagraph(combined_generating_set)

            # add all metagraph1 edges
            edge_list1 = self.get_edges_in_matrix(adjacency_matrix1, generator_set1)
            for edge in edge_list1:
                mg1.add_edge(edge)
            modified_adjacency_matrix1 = mg1.adjacency_matrix().tolist()

            mg2 = Metagraph(combined_generating_set)
            # add all metagraph2 edges
            edge_list2 = self.get_edges_in_matrix(adjacency_matrix2, generator_set2)
            for edge in edge_list2:
                mg2.add_edge(edge)
            modified_adjacency_matrix2 = mg2.adjacency_matrix().tolist()

            #combined_mg = Metagraph(combined_generating_set)
            size = len(combined_generating_set)
            combined_adjacency_matrix = MetagraphHelper().get_null_matrix(size, size)
            for i in range(size):
                for j in range(size):
                    # take the union
                    if modified_adjacency_matrix1[i][j] is None:
                        combined_adjacency_matrix[i][j] = modified_adjacency_matrix2[i][j]
                    elif modified_adjacency_matrix2[i][j] is None:
                        combined_adjacency_matrix[i][j] = modified_adjacency_matrix1[i][j]
                    else:
                        temp = modified_adjacency_matrix1[i][j]
                        for triple in modified_adjacency_matrix2[i][j]:
                            if not triple in modified_adjacency_matrix1[i][j]:
                                temp.append(triple)
                        combined_adjacency_matrix[i][j] = temp

        return combined_adjacency_matrix

    def get_triples(self, nested_triples_list):
        """ Returns a list of non-nested Triple objects.
        :param nested_triples_list: list of nested Triple objects
        :return: list of Triple objects
        """

        if nested_triples_list is None or len(nested_triples_list) == 0:
            raise MetagraphException('triples_list', resources['value_null'])

        result = []
        if isinstance(nested_triples_list, list):
            for elt in nested_triples_list:
                if isinstance(elt, Triple):
                    result.append(elt)
                else:
                    temp = self.get_triples(elt)
                    for item in temp:
                        result.append(item)

        return result

    def multiply_adjacency_matrices(self, adjacency_matrix1, generator_set1, adjacency_matrix2, generator_set2):
        """ Multiplies the two adjacency matrices provided and returns the result.
        :param adjacency_matrix1: numpy.matrix
        :param generator_set1: set
        :param adjacency_matrix2: numpy.matrix
        :param generator_set2: set
        :return: numpy.matrix
        """

        if adjacency_matrix1 is None:
            raise MetagraphException('adjacency_matrix1', resources['value_null'])
        if adjacency_matrix2 is None:
            raise MetagraphException('adjacency_matrix2', resources['value_null'])

        if generator_set1 is None:
            raise MetagraphException('generator_set1', resources['value_null'])
        if generator_set2 is None:
            raise MetagraphException('generator_set2', resources['value_null'])

        # check generating sets are identical
        if not(len(generator_set1.difference(generator_set2)) == 0 and
               len(generator_set2.difference(generator_set1)) == 0):
            raise MetagraphException('generator_sets', resources['not_identical'])

        size = len(generator_set1)
        resultant_adjacency_matrix = MetagraphHelper().get_null_matrix(size, size)

        for i in range(size):
            for j in range(size):
                resultant_adjacency_matrix[i][j] = self.multiply_components(adjacency_matrix1,
                                                                            adjacency_matrix2,
                                                                            generator_set1, i,
                                                                            j, size)
                #print('multiply_components')

        return resultant_adjacency_matrix

    def multiply_components(self, adjacency_matrix1, adjacency_matrix2, generator_set1, i, j, size):
        """ Multiplies elements of two adjacency matrices.
        :param adjacency_matrix1: numpy.matrix
        :param adjacency_matrix2: numpy.matrix
        :param generator_set1: set
        :param i: int
        :param j: int
        :param size: int
        :return: list of Triple objects.
        """

        if adjacency_matrix1 is None:
            raise MetagraphException('adjacency_matrix1', resources['value_null'])
        if adjacency_matrix2 is None:
            raise MetagraphException('adjacency_matrix2', resources['value_null'])
        if generator_set1 is None or len(generator_set1) == 0:
            raise MetagraphException('generator_set1', resources['value_null'])

        result = []
        # computes the outermost loop (ie., k=1...K where K is the size of each input matrix)
        for k in range(size):
            a_ik = adjacency_matrix1[i][k]
            b_kj = adjacency_matrix2[k][j]
            #print('multiply_triple_lists')
            temp = self.multiply_triple_lists(a_ik, b_kj, list(generator_set1)[i],
                                              list(generator_set1)[j], list(generator_set1)[k])
            if temp is not None:
                #print('len(temp): %s'%len(temp))
                for triple in temp:
                    if not MetagraphHelper().is_triple_in_list(triple, result):
                        result.append(triple)
                    #if triple not in result: result.append(triple)
        if len(result) == 0:
            return None

        return result

    def multiply_triple_lists(self, triple_list1, triple_list2, x_i, x_j, x_k):
        """ Multiplies two list of Triple objects and returns the result.
        :param triple_list1: list of Triple objects
        :param triple_list2: list of Triple objects
        :param x_i: generator set element
        :param x_j: generator set element
        :param x_k: generator set element
        :return: list of Triple objects
        """

        if triple_list1 is None or triple_list2 is None:
            return None

        result = []
        # computes the middle loop (ie., n=1...N where N is the size of triple_list1
        #print('len(triple_list1): %s'%len(triple_list1))
        #print('len(triple_list2): %s'%len(triple_list2))
        #if len(triple_list1)==256:
        #    print('here')
        for triple1 in triple_list1:
            # computes the innermost loop (ie., m=1...M where M is the size of triple_list2
            for triple2 in triple_list2:
                #print('multiply_triples')
                temp = self.multiply_triples(triple1, triple2, x_i, x_j, x_k)
                if temp is not None:
                    if not MetagraphHelper().is_triple_in_list(temp, result):
                        result.append(temp)
                    #if temp not in result: result.append(temp)

        return result

    @staticmethod
    def multiply_triples(triple1, triple2, x_i, x_j, x_k):
        """ Multiplies two Triple objects and returns the result.
        :param triple1: Triple object
        :param triple2: Triple object
        :param x_i: generator set element
        :param x_j: generator set element
        :param x_k: generator set element
        :return: Triple object
        """

        if triple1 is None or triple2 is None:
            return None

        # compute alpha(R)
        alpha_r = triple2.coinputs
        if triple2.coinputs is None:
            alpha_r = triple1.coinputs
        elif triple1.coinputs is not None:
            alpha_r = triple1.coinputs.union(triple2.coinputs)
        if alpha_r is not None and triple1.cooutputs is not None:
            alpha_r = alpha_r.difference(({x_i}).union(triple1.cooutputs))
        elif alpha_r is not None:
            alpha_r = alpha_r.difference(({x_i}))

        # compute beta(R)
        beta_r = triple2.cooutputs
        if triple2.cooutputs is None:
            beta_r = triple1.cooutputs
        elif triple1.cooutputs is not None:
            beta_r = triple1.cooutputs.union(triple2.cooutputs)
        if beta_r is not None:
            beta_r = beta_r.union({x_k})
            beta_r = beta_r.difference({x_j})
        else:
            beta_r = {x_k}
            beta_r = beta_r.difference(({x_j}))

        # compute gamma(R)
        truncated = []
        if triple1.edges not in truncated:
            if isinstance(triple1.edges, Edge):
                truncated.append(triple1.edges)
            else:
                truncated = [edge for edge in triple1.edges]

        if triple2.edges not in truncated:
            if isinstance(triple2.edges, Edge):
                truncated.append(triple2.edges)
            else:
                truncated = [edge for edge in triple2.edges]
            #truncated.append(triple2.edges)

        gamma_r = truncated

        return Triple(alpha_r, beta_r, gamma_r)

    @staticmethod
    def get_null_matrix(rows, cols):
        """ Returns a null matrix of dimension rows x cols.
        :param rows: int
        :param cols: int
        :return: list
        """
        psi = None
        result = []
        for i in range(rows):
            # noinspection PyUnusedLocal
            item = [psi for j in range(cols)]
            result.append(item)
        return result

    @staticmethod
    def get_edges_in_matrix(adjacency_matrix, generator_set):
        """ Returns the list of edges in the provided adjacency matrix.
        :param adjacency_matrix: numpy.matrix
        :param generator_set: set
        :return: list of Edge objects
        """

        if adjacency_matrix is None:
            raise MetagraphException('adjacency_matrix', resources['value_null'])
        if generator_set is None or len(generator_set) == 0:
            raise MetagraphException('generator_set', resources['value_null'])

        size = len(generator_set)
        edge_list = []
        for i in range(size):
            for j in range(size):
                if adjacency_matrix[i][j] is not None:
                    # list of triples
                    triples_list = adjacency_matrix[i][j]
                    for triple in triples_list:
                        # gamma_R describes the edge
                        if triple[2] not in edge_list:
                            edge_list.append(triple[2])

        return edge_list

    def get_edge_list(self, nested_edges):
        """ Returns a non-nested list of edges.
        :param nested_edges: nested list of Edge objects
        :return: non-nested list of Edge objects.
        """

        edge_list = []
        if nested_edges is None or len(nested_edges) == 0:
            return edge_list

        for element in nested_edges:
            if isinstance(element, list):
                temp = self.get_edge_list(element)
                for edge in temp:
                    if edge not in edge_list:
                        edge_list.append(edge)
            elif isinstance(element, Edge):
                if element not in edge_list:
                    edge_list.append(element)

        return edge_list

    def get_edges_from_triple_list(self, nested_triples):
        """ Returns the edges present in a nested list of Triple objects.
        :param nested_triples: nested list of Triple objects
        :return: non-nested list of Triple objects
        """

        result = []
        if nested_triples is None:
            return result

        if isinstance(nested_triples, Triple):
            return nested_triples.edges

        elif isinstance(nested_triples, list):
            for element in nested_triples:
                temp = self.get_edges_from_triple_list(element)
                if isinstance(temp, list):
                    for elt in temp:
                        if isinstance(elt, Edge) and (elt not in result):
                            result.append(elt)
                        elif isinstance(elt, list):
                            for elt2 in elt:
                                if elt2 not in result:
                                    result.append(elt2)
                elif isinstance(temp, Edge) and (temp not in result):
                    result.append(temp)

        return result

    def is_triple_in_list(self, triple, triples_list):
        """ Checks whether a particular Triple object is in a given list of Triples.
        :param triple: Triple object
        :param triples_list: list of Triple object
        :return: boolean
        """

        if triple is None:
            raise MetagraphException('triple', resources['value_null'])
        if triples_list is None:
            raise MetagraphException('triples_list', resources['value_null'])

        result = False

        if isinstance(triples_list, list):
            for element in triples_list:
                result = self.is_triple_in_list(triple, element)
                if result:
                    break

        elif isinstance(triples_list, Triple):
            if self.are_triples_equal(triple, triples_list):
                result = True

        return result

        #for elt in triples_list:
        #    if self.are_triples_equal(triple,elt): return True
        #return False

    def is_edge_in_list(self, edge, nested_edges):
        """ Checks whether a particular edge is in the nested list of edges.
        :param edge: Edge object
        :param nested_edges: nested list of Edge objects
        :return: boolean
        """

        if edge is None:
            raise MetagraphException('edge', resources['value_null'])
        if nested_edges is None:
            raise MetagraphException('nested_edges', resources['value_null'])
        result = False

        if isinstance(nested_edges, list):
            for element in nested_edges:
                result = self.is_edge_in_list(edge, element)
                if result:
                    break

        elif isinstance(nested_edges, Edge):
            if self.are_edges_equal(edge, nested_edges):
                result = True

        return result

    def is_node_in_list(self, node, node_list):
        """ Checks if a particular node is in the given list of nodes.
        :param node: Node object
        :param node_list: list of Node objects
        :return: boolean
        """

        if node is None:
            raise MetagraphException('node', resources['value_null'])
        if node_list is None:
            raise MetagraphException('node_list', resources['value_null'])
        result = False

        if isinstance(node_list, list):
            for element in node_list:
                result = self.is_node_in_list(node, element)
                if result:
                    break

        elif isinstance(node_list, Node):
            if self.are_nodes_equal(node, node_list):
                result = True

        return result

    def are_triples_equal(self, triple1, triple2):
        """ Checks if the two given triples are equal.
        :param triple1: Triple object
        :param triple2: Triple object
        :return: boolean
        """

        if triple1 is None:
            raise MetagraphException('triple1', resources['value_null'])
        if triple2 is None:
            raise MetagraphException('triple2', resources['value_null'])
        if not isinstance(triple1, Triple):
            raise MetagraphException('triple1', resources['format_invalid'])
        if not isinstance(triple2, Triple):
            raise MetagraphException('triple2', resources['format_invalid'])

        edge_list_match = True
        for edge in triple1.edges:
            if not self.is_edge_in_list(edge, triple2.edges):
                edge_list_match = False
                break

        for edge in triple2.edges:
            if not self.is_edge_in_list(edge, triple1.edges):
                edge_list_match = False
                break

        return (triple1.coinputs == triple2.coinputs and
                triple1.cooutputs == triple2.cooutputs and
                len(triple1.edges) == len(triple2.edges) and
                edge_list_match)

    @staticmethod
    def are_edges_equal(edge1, edge2):
        """ Checks if the two given edges are equal.
        :param edge1: Edge object
        :param edge2: Edge object
        :return: boolean
        """

        if edge1 is None:
            raise MetagraphException('edge1', resources['value_null'])
        if edge2 is None:
            raise MetagraphException('edge2', resources['value_null'])
        if not isinstance(edge1, Edge):
            raise MetagraphException('edge1', resources['format_invalid'])
        if not isinstance(edge2, Edge):
            raise MetagraphException('edge2', resources['format_invalid'])

        if edge1.attributes is not None and edge2.attributes is not None:
            return (edge1.invertex == edge2.invertex and
                    edge1.outvertex == edge2.outvertex and
                    set(edge1.attributes) == set(edge2.attributes) and
                    edge1.label == edge2.label)
        else:
            return (edge1.invertex == edge2.invertex and
                    edge1.outvertex == edge2.outvertex and
                    edge1.label == edge2.label)

    @staticmethod
    def are_nodes_equal(node1, node2):
        """ Checks if two given nodes are equal.
        :param node1: Node object
        :param node2: Node object
        :return: boolean
        """

        if node1 is None:
            raise MetagraphException('node1', resources['value_null'])
        if node2 is None:
            raise MetagraphException('node2', resources['value_null'])
        if not isinstance(node1, Node):
            raise MetagraphException('node1', resources['format_invalid'])
        if not isinstance(node2, Node):
            raise MetagraphException('node2', resources['format_invalid'])

        return node1.element_set == node2.element_set

    @staticmethod
    def is_edge_list_included(edges, reference_edge_list):
        """ Checks if an edge list is included in the reference edge list.
        :param edges: list of Edge objects
        :param reference_edge_list: reference lists of Edge objects
        :return: boolean
        """

        if edges is None or len(edges) == 0:
            raise MetagraphException('edges', resources['value_null'])
        if reference_edge_list is None or len(reference_edge_list) == 0:
            raise MetagraphException('reference_edge_list', resources['value_null'])

        for ref_edges in reference_edge_list:
            inclusive_list = True
            for edge1 in edges:
                if not MetagraphHelper().is_edge_in_list(edge1, ref_edges):
                #match=False
                #for edge2 in ref_edges:
                #    if edge1.invertex==edge2.invertex and edge1.outvertex==edge2.outvertex:
                #        match=True
                #        break
                #if not match:
                    inclusive_list = False
                    break
            if inclusive_list and len(edges) == len(ref_edges):
                return True

        return False

    def get_netinputs(self, edge_list):
        """ Retrieves a list of net inputs corresponding to the given edge list.
        :param edge_list: list of Edge objects
        :return: list
        """

        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        all_inputs = []
        for edge in edge_list:
            if isinstance(edge, Edge):
                for input_elt in edge.invertex:
                    if input_elt not in all_inputs:
                        all_inputs.append(input_elt)
            elif isinstance(edge, list):
                temp = self.get_netinputs(edge)
                for item in temp:
                    if item not in all_inputs:
                        all_inputs.append(item)

        return all_inputs

    def get_netoutputs(self, edge_list):
        """ Retrieves a list of net outputs corresponding to the given edge list.
        :param edge_list: list of Edge objects
        :return: list
        """

        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        all_outputs = []
        for edge in edge_list:
            if isinstance(edge, Edge):
                for output in edge.outvertex:
                    if output not in all_outputs:
                        all_outputs.append(output)
            elif isinstance(edge, list):
                temp = self.get_netoutputs(edge)
                for item in temp:
                    if item not in all_outputs:
                        all_outputs.append(item)

        return all_outputs

    @staticmethod
    def get_coinputs_from_triples(triples_list):
        """ Retrieves a list of co-inputs corresponding to the given triples list.
        :param triples_list: list of Triple objects
        :return: list
        """

        if triples_list is None or len(triples_list) == 0:
            raise MetagraphException('triples_list', resources['value_null'])

        all_coinputs = []
        for triple in triples_list:
            if triple.coinputs is not None:
                for coinput in triple.coinputs:
                    if coinput not in all_coinputs:
                        all_coinputs.append(coinput)

        return all_coinputs

    @staticmethod
    def get_cooutputs_from_triples(triples_list):
        """ Retrieves a list of co-outputs corresponding to the given triples list.
        :param triples_list: list of Triple objects
        :return: list
        """

        if triples_list is None or len(triples_list) == 0:
            raise MetagraphException('triples_list', resources['value_null'])

        all_cooutputs = []
        for triple in triples_list:
            if triple.cooutputs is not None:
                for cooutput in triple.cooutputs:
                    if cooutput not in all_cooutputs:
                        all_cooutputs.append(cooutput)

        return all_cooutputs

    def extract_edge_list(self, nested_edge_list):
        """ Retrieves a non-nested edge list from the given nested list.
        :param nested_edge_list: nested list of Edge objects
        :return: non-nested list of Edge objects.
        """

        if nested_edge_list is None or len(nested_edge_list) == 0:
            raise MetagraphException('nested_edge_list', resources['value_null'])
        result = []

        for element in nested_edge_list:
            if isinstance(element, list):
                temp = self.extract_edge_list(element)
                for item in temp:
                    result.append(item)

            elif isinstance(element, Edge):
                result.append(element)

        return result

    def node_lists_overlap(self, nodes_list1, nodes_list2):
        """ Checks if two lists of nodes overlap.
        :param nodes_list1: list of Node objects
        :param nodes_list2: list of Node objects
        :return: boolean
        """

        for node1 in nodes_list1:
            if self.is_node_in_list(node1, nodes_list2):
                return True

        return False

    @staticmethod
    def nodes_overlap(nodes_list1, nodes_list2):
        """ Checks if two lists of nodes overlap.
        :param nodes_list1: list of Node objects
        :param nodes_list2: list of Node objects
        :return: boolean
        """

        for node1 in nodes_list1:
            for node2 in nodes_list2:
                intersection = node1.get_element_set.intersection(node2.get_element_set)
                if intersection is not None and len(intersection) > 0:
                    return True

        return False

    @staticmethod
    def get_generating_set(edge_list):
        """ Retrieves the generating set of the metagraph from its edge list.
        :param edge_list: list of Edge objects
        :return: set
        """

        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        generating_set = []
        for edge in edge_list:
            for input_elt in edge.invertex:
                if input_elt not in generating_set:
                    generating_set.append(input_elt)

            for output in edge.outvertex:
                if output not in generating_set:
                    generating_set.append(output)

        return set(generating_set)

    @staticmethod
    def get_element_set(nodes_list):
        """ Retrieves the set of elements within a given list of nodes
        :param nodes_list: list of Node objects
        :return: set
        """
        if nodes_list is not None and len(nodes_list) > 0:
            result = set()
            for node in nodes_list:
                result = result.union(node.get_element_set)

            return result

        return set()

    @staticmethod
    def transpose_matrix(matrix):
        """ Computes the transpose matrix of given matrix
        :param matrix: 2D array
        :return: 2D array
        """

        if matrix is None:
            raise MetagraphException('matrix', resources['value_null'])

        #rows = len(matrix)
        cols = len(matrix[0])

        result = []

        for j in range(cols):
            column = [row[j] for row in matrix]
            result.append(column)

        return result

    @staticmethod
    def custom_multiply_matrices(matrix1, matrix2, edge_list):
        """Multiplies the Triple lists of two matrices
        :param matrix1: 2D array
        :param matrix2: 2D array
        :param edge_list: list of Edge objects
        :return: 2D array
        """

        if matrix1 is None:
            raise MetagraphException('matrix1', resources['value_null'])
        if matrix2 is None:
            raise MetagraphException('matrix2', resources['value_null'])
        if edge_list is None or len(edge_list) == 0:
            raise MetagraphException('edge_list', resources['value_null'])

        matrix1_cols = len(matrix1[0])
        matrix2_rows = len(matrix2)
        if matrix1_cols != matrix2_rows:
            raise MetagraphException('matrix1, matrix2', resources['structures_incompatible'])

        result = MetagraphHelper().get_null_matrix(len(matrix1), len(matrix2[0]))

        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                intermediate_result = set()
                for k in range(len(matrix1[0])):
                    a_ik = matrix1[i][k]
                    b_kj = matrix2[k][j]
                    temp = MetagraphHelper().custom_add_matrix_elements(k, a_ik, b_kj, edge_list)
                    intermediate_result = intermediate_result.union(temp)

                result[i][j] = intermediate_result

        return result

    @staticmethod
    def custom_add_matrix_elements(k, a_ik, b_kj, y):
        """Custom addition of matrix elements.
        :param k: int
        :param a_ik: int
        :param b_kj: int
        :param y: list
        :return: set
        """

        if len(y) < k+1:
            raise MetagraphException('k', resources['value_out_of_bounds'])

        if a_ik == 1 and b_kj == -1:
            return {(1, y[k])}
        elif a_ik == -1 and b_kj == -1:
            return {(-1, y[k])}
        else:
            return set()

    @staticmethod
    def extract_edge_label_components(label):
        """Extracts components of an edge label.
        :param label: string
        :return: string tuple
        """

        if label is None or label == '':
            raise MetagraphException('label', resources['value_null'])

        label = label.replace('>', '')
        items = label.split('<')
        if len(items) < 2:
            raise MetagraphException('label', resources['format_invalid'])

        r_ij = {items[0]}
        tuples = items[1].split(';')
        if len(tuples) < 2:
            raise MetagraphException('label', resources['format_invalid'])

        t_a = {tuples[0]}
        t_b = {tuples[1]}

        # noinspection PyRedundantParentheses
        return (r_ij, t_a, t_b)































