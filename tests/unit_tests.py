import unittest
from mgtoolkit.library import Metagraph, ConditionalMetagraph, Edge


# noinspection PyAttributeOutsideInit
class RunTests(unittest.TestCase):

    # noinspection PyPep8Naming
    def setUp(self):
        import numpy
        t = numpy.version

        self.generating_set1 = {1, 2, 3, 4, 5, 6, 7}
        self.mg1 = Metagraph(self.generating_set1)
        self.mg1.add_edges_from([Edge({1}, {2, 3}), Edge({1, 4}, {5}), Edge({3}, {6, 7})])

        self.variable_set = set(range(1, 8))
        self.propositions_set = {'p1', 'p2'}
        self.cmg1 = ConditionalMetagraph(self.variable_set, self.propositions_set)
        self.cmg1.add_edges_from([Edge({1, 2}, {3, 4}, attributes=['p1']), Edge({2}, {4, 6}, attributes=['p2']),
                                  Edge({3, 4}, {5}, attributes=['p1', 'p2']), Edge({4, 6}, {5, 7}, attributes=['p1'])])

    def test_mg_creation(self):
        self.assertEqual(len(self.mg1.edges), 3)
        self.assertEqual(len(self.mg1.nodes), 6)

    def test_mg_adjacency_matrix(self):
        adj_matrix = self.mg1.adjacency_matrix()
        row_count = adj_matrix.shape[0]
        col_count = adj_matrix.shape[1]
        row1 = adj_matrix[0, :]
        col1 = adj_matrix[:, 0]
        self.assertEqual(row_count, 7)
        self.assertEqual(col_count, 7)
        self.assertEqual(len(row1.tolist()[0]), 7)
        self.assertEqual(len(col1.tolist()), 7)
        self.assertEqual(row1.tolist()[0][1][0].coinputs, None)
        self.assertEqual(row1.tolist()[0][1][0].cooutputs, {3})
        self.assertEqual(row1.tolist()[0][1][0].edges.invertex, {1})
        self.assertEqual(row1.tolist()[0][1][0].edges.outvertex, {2, 3})

    def test_mg_incidence_matrix(self):
        incidence_m = self.mg1.incidence_matrix()
        row_count = incidence_m.shape[0]
        col_count = incidence_m.shape[1]
        row1 = incidence_m[0, :]
        col1 = incidence_m[:, 0]
        self.assertEqual(row_count, 7)
        self.assertEqual(col_count, 3)
        self.assertEqual(len(row1.tolist()[0]), 3)
        self.assertEqual(len(col1.tolist()), 7)
        self.assertEqual(row1.tolist()[0], [-1, -1, None])

    def test_mg_closure(self):
        a_star = self.mg1.get_closure()
        row_count = a_star.shape[0]
        col_count = a_star.shape[1]
        row1 = a_star[0, :]
        col1 = a_star[:, 0]
        self.assertEqual(row_count, 7)
        self.assertEqual(col_count, 7)
        self.assertEqual(len(row1.tolist()[0]), 7)
        self.assertEqual(len(col1.tolist()), 7)
        self.assertEqual(row1.tolist()[0][3], None)
        self.assertEqual(row1.tolist()[0][4][0].coinputs, {4})
        self.assertEqual(row1.tolist()[0][4][0].cooutputs, None)
        self.assertEqual(row1.tolist()[0][4][0].edges.invertex, {1, 4})
        self.assertEqual(row1.tolist()[0][4][0].edges.outvertex, {5})

    def test_mg_metapaths(self):
        source = {1}
        target = {7}
        metapaths = self.mg1.get_all_metapaths_from(source, target)

        self.assertEqual(len(metapaths), 1)
        self.assertEqual(metapaths[0].source, {1})
        self.assertEqual(metapaths[0].target, {7})
        self.assertEqual(metapaths[0].edge_list[0].invertex, {1})
        self.assertEqual(metapaths[0].edge_list[0].outvertex, {2, 3})
        self.assertEqual(metapaths[0].edge_list[1].invertex, {3})
        self.assertEqual(metapaths[0].edge_list[1].outvertex, {6, 7})

        edge_dominant = None
        input_dominant = None
        dominant = None
        if len(metapaths) > 0:
            edge_dominant = self.mg1.is_edge_dominant_metapath(metapaths[0])
            input_dominant = self.mg1.is_input_dominant_metapath(metapaths[0])
            dominant = self.mg1.is_dominant_metapath(metapaths[0])

        self.assertEqual(edge_dominant, True)
        self.assertEqual(input_dominant, True)
        self.assertEqual(dominant, True)

        metapaths2 = self.mg1.get_all_metapaths_from({1, 3}, {7})
        metapath_dominates = metapaths[0].dominates(metapaths2[0])

        self.assertEqual(metapath_dominates, True)

    def test_edge_properties(self):
        source = {1}
        target = {7}
        metapaths = self.mg1.get_all_metapaths_from(source, target)
        redundant = self.mg1.is_redundant_edge(Edge({1}, {2, 3}), metapaths[0], source, target)
        self.assertEqual(redundant, False)

        edge_list = [Edge({1}, {2, 3})]
        is_cutset = self.mg1.is_cutset(edge_list, source, target)
        is_bridge = self.mg1.is_bridge(edge_list, source, target)
        self.assertEqual(is_cutset, True)
        self.assertEqual(is_bridge, True)

    def test_mg_projection(self):
        generating_set2 = {1, 2, 3, 4, 5, 6, 7, 8}
        mg2 = Metagraph(generating_set2)
        mg2.add_edges_from([Edge({1}, {3, 4}), Edge({3}, {6}), Edge({2}, {5}), Edge({4, 5}, {7}), Edge({6, 7}, {8})])
        generator_subset = {1, 2, 6, 7, 8}
        projection = mg2.get_projection(generator_subset)

        self.assertEqual(len(projection.edges), 4)
        self.assertEqual(len(projection.nodes), 7)

    def test_mg_inverse(self):
        generating_set2 = {1, 2, 3, 4, 5, 6, 7, 8}
        mg2 = Metagraph(generating_set2)
        mg2.add_edges_from([Edge({1, 2}, {3, 4}), Edge({3, 4, 5}, {6, 8}), Edge({1}, {5}), Edge({6, 7}, {1})])
        inverse = mg2.get_inverse()

        self.assertEqual(len(inverse.edges), 6)
        self.assertEqual(len(inverse.nodes), 6)

    def test_mg_efm(self):
        generating_set2 = {1, 2, 3, 4, 5, 6, 7, 8}
        mg2 = Metagraph(generating_set2)
        mg2.add_edges_from([Edge({1, 2}, {3, 4}), Edge({3, 4, 5}, {6, 8}), Edge({1}, {5}), Edge({6, 7}, {1})])
        generator_subset = {2, 4, 7}
        efm = mg2.get_efm(generator_subset)

        self.assertEqual(len(efm.edges), 3)
        self.assertEqual(len(efm.nodes), 3)

    def test_cmg_creation(self):
        self.assertEqual(len(self.cmg1.edges), 4)
        self.assertEqual(len(self.cmg1.nodes), 8)

    def test_cmg_context(self):
        true_props = {'p1'}
        false_props = {'p2'}
        context = self.cmg1.get_context(true_props, false_props)
        self.assertEqual(len(context.edges), 2)
        self.assertEqual(len(context.nodes), 4)

    def test_cmg_properties(self):
        source = {1, 3}
        target = {4}
        logical_expressions = ['p1 | p2']
        interpretations = [[('p1', True), ('p2', False)]]
        connected = self.cmg1.is_connected(source, target, logical_expressions, interpretations)
        fully_connected = self.cmg1.is_fully_connected(source, target, logical_expressions, interpretations)
        redundantly_connected = self.cmg1.is_redundantly_connected(source, target, logical_expressions, interpretations)
        non_redundant = self.cmg1.is_non_redundant(logical_expressions, interpretations)

        self.assertEqual(connected, False)
        self.assertEqual(fully_connected, False)
        self.assertEqual(redundantly_connected, True)
        self.assertEqual(non_redundant, True)

    def test_from_textbook(self):
        generating_set1 = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        mg1 = Metagraph(generating_set1)
        mg1.add_edges_from([Edge({1}, {2, 3}), Edge({1, 4}, {5}), Edge({3}, {7}), Edge({5, 2}, {6}),
                            Edge({6, 7}, {9}), Edge({3, 4, 8}, {9}), Edge({4, 8}, {1, 5})])
        #a1=mg1.adjacency_matrix()
        #a_star1= mg1.get_closure()
        #incidence_matrix= mg1.incidence_matrix()

        metapaths1 = mg1.get_all_metapaths_from({1, 4}, {6})

        # check metapath dominance
        if len(metapaths1) > 0:
            edge_dominant = mg1.is_edge_dominant_metapath(metapaths1[0])
            input_dominant = mg1.is_input_dominant_metapath(metapaths1[0])
            dominant = mg1.is_dominant_metapath(metapaths1[0])

            self.assertEqual(edge_dominant, True)
            self.assertEqual(input_dominant, True)
            self.assertEqual(dominant, True)

        metapaths3 = mg1.get_all_metapaths_from({1, 4}, {5, 6})
        redundant1 = mg1.is_redundant_edge(Edge({1, 4}, {5}), metapaths3[0], {1, 4}, {5, 6})
        redundant2 = mg1.is_redundant_edge(Edge({4, 8}, {5, 6}), metapaths3[0], {4, 8}, {5, 6})

        self.assertEqual(redundant1, False)
        self.assertEqual(redundant2, True)

        source = {4, 8}
        target = {7}
        edge_list1 = [Edge({4, 8}, {1})]
        edge_list2 = [Edge({1}, {2, 3})]
        is_cutset = mg1.is_cutset(edge_list1, source, target)
        is_bridge = mg1.is_bridge(edge_list2, source, target)

        self.assertEqual(is_cutset, False)
        self.assertEqual(is_bridge, True)

if __name__ == '__main__':
    unittest.main()


