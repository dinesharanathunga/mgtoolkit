========
Tutorial
========

We provide here a broad overview of the capabilities of our MGtoolkit package.
It includes analysis of metagraph connectivity properties (see subsection 1.2),
transformation of metagraphs (subsection 1.3) and analysis of attributed metagraphs
(subsection 1.4). We illustrate each section with simple and concise code
examples for the reader's benefit.

1.1 Creating metagraphs

Our MGtoolkit package defines a Metagraph class to represent a basic metagraph,
which can be instantiated using a generating set and a set of edges defined on
the generating set as per the example snippet below. Each edge is an instance
of an Edge class that consists of the members: invertex and outvertex, which
are proper subsets of the generating set.

.. code-block:: python

  1 from mgtoolkit.library import *
  2
  3 generating_set = {1,2,3,4,5,6,7}
  4 mg = Metagraph(generating_set)
  5 mg.add_edges_from([ Edge({1},{2,3}), Edge({1,4},{5}), Edge({3},{6,7}) ])


1.2 Connectivity analysis

MGtoolkit supports Metagraph members to derive the adjacency matrix A and
the incidence matrix I as shown below (we use the metagraph created in subsection 1.1).
Each of these matrices provides a complete representation of the
underlying metagraph [1].
Out toolkit allows to select matrix contents visualise them. So, for instance,
each element in the adjacency matrix is a Triple object with members coinput,
cooutput and edge list [1]. In the following example, coinput= None, cooutput={3} and edge list= {({1}, {2, 3})}.

.. code-block:: python

  1 A = mg.adjacency_matrix()
  2 I = mg.incidence_matrix()
  3 # select the 1st row and 1st column of A
  4 row_1 = A[0,:]
  5 column_1 = A[:,0]
  6 # display an element of A
  7 print(repr(A[0][1]))
  8
  9 # output
  10 Triple(None, set([3]), Edge(set([1]), set([2, 3])))

MGtoolkit also allows to derive the closure (A) of an adjacency matrix A
which represents all paths of any length in the metagraph. The contents of the
resultant matrix can also be selected and visualised similar to the adjacency
matrix as shown in the example below. Each element in A is a list of Triple
objects.

.. code-block:: python

  1 A_star= mg.get_closure()
  2 # select the 1st row and 1st column of A_star
  3 row_1 = A_star[0,:]
  4 column_1 = A_star[:,0]
  5 # display an element of A_star
  6 print(repr(A_star[3][4]))
  7
  8 # output
  9 [Triple(set([1]), None, Edge(set([1, 4]), set([5])))]

A metapath is a very useful property that describes the connectivity properties of metagraphs.
This property describes a set of edges from a source set of
elements to a target set of elements in the metagraph, indicating if the source is
connected to the target [1].

Our metagraph package defines a Metapath class with the members: source,
target and edge list, to represent a metapath. The package allows to search
for valid metapaths between a source and a target in a Metagraph object (see
example below). If one or more metapaths exist, it implies that all the target
elements are reachable from the source elements. So, in the following example,
MGtoolkit identifies a single metapath consisting of the two edges: ({1}, {2, 3})
and ({3}, {6, 7}) between the input source and target of the underlying metagraph.

.. code-block:: python

  1 source = {1}
  2 target = {7}
  3 metapaths = mg.get_all_metapaths_from(source,target)
  4 # display results
  5 for metapath in metapaths:
  6 print(repr(metapath))
  7 # output
  8 Metapath({ Edge(set([1]), set([2, 3])), Edge(set([3]), set([6, 7])) })

The property of dominance is useful in determining whether a metapath
has any unnecessary components (edges or elements) [1]. MGtoolkit supports
the Metagraph members below to evaluate whether a particular metapath is
input-dominant: i.e., no proper subset of the source connects to the target,
edge-dominant: i.e., no proper subset of the metapath edges is also a metapath
from the source to the target, or dominant: i.e., a metapath is both input- and
edge-dominant. The following snippet shows that the metapath found in the
previous example is both edge- and input-dominant and hence is a dominant
metapath.

.. code-block:: python

  1 # check metapath dominance
  2 if len(metapaths)>0:
  3 edge_dominant = mg.is_edge_dominant_metapath(metapaths[0])
  4 input_dominant = mg.is_input_dominant_metapath(metapaths[0])
  5 dominant = mg.is_dominant_metapath(metapaths[0])
  6 print('edge_dominant: %s, input_dominant: %s, dominant: %s'%(
    edge_dominant,input_dominant,dominant))
  7
  8 # output
  9 edge_dominant: True, input_dominant: True, dominant: True


The toolkit also allows to check if a particular metapath dominates another
by implementing the members shown below in the Metapath class.


.. code-block:: python

  1 mp1 = mg.get_all_metapaths_from({1},{7})
  2 mp2 = mg.get_all_metapaths_from({1,3},{7})
  3 metapath_dominates = mp1[0].dominates(mp2[0])
  4
  5 print('mp1[0] dominates mp2[0]: %s'%(metapath_dominates))
  6
  7 # output
  8 mp1 dominates mp2: True

MGtoolkit also allows to check if a particular edge is redundant in the context
of a metapath. If non-redundant, removal of this edge will disconnect at least
one of the elements in the source from the target. The snippet below finds that
the edge ({1}, {2, 3}) is non-redundant in the previous metapath example.

.. code-block:: python

  1 redundant = mg.is_redundant_edge(Edge({1},{2,3}), metapaths[0], source,
    target)
  2 print('redundant_edge: %s'%(redundant))
  3
  4 # output
  5 redundant_edge: False

In metagraph theory, the notion of cutsets and bridges allow to locate edges
that are critical [1]. A cutset is a set of edges which if removed, eliminates all
metapaths between a given source and a target. A singleton cutset between a
source and a target is referred to as a bridge [1].

MGtoolkit defines Metagraph members to facilitate checking whether a particular
set of edges is a cutset or a bridge between a particular source and target.
So for instance, the singleton edge set { ({1}, {2, 3}) } is both a cutset and a
bridge in the context of our previous metapath.

.. code-block:: python

  1 edge_list = [ Edge({1}, {2,3}) ]
  2 is_cutset = mg.is_cutset(edge_list, source, target)
  3 is_bridge = mg.is_bridge(edge_list, source, target)
  4 print('is_cutset: %s, is_bridge: %s'%(is_cutset,is_bridge))
  5
  6 # output
  7 is_cutset: True, is_bridge: True


1.3 Transformations

In the previous subsection, we described our implementation of a variety of features of a metagraph.
We now present the implementation of metagraph transformations to other useful forms that disclose
certain structural features and enable useful analysis as described in [1].

MGtoolkit defines a get projection member in its Metagraph class to derive
a projection for a metagraph. A projection is simplified metagraph that provides
a high-level view of the original metagraph by concealing certain details [1]. The
snippet below creates a projection for the subset of the metagraph's generating
set selected and allows to visualise it.

.. code-block:: python

  1 from mgtoolkit.library import *
  2
  3 generating_set2 = {1,2,3,4,5,6,7,8}
  4 mg2 = Metagraph(generating_set2)
  5 mg2.add_edges_from([ Edge({1}, {3,4}), Edge({3}, {6}), Edge({2}, {5}),
    Edge({4,5}, set{7}), Edge({6,7}, {8}) ])
  6 generator_subset = {1,2,6,7,8}
  7 projection = mg2.get_projection(generator_subset)
  8 # display result
  9 print(repr(projection))
  10
  11 # output
  12 <`Metagraph'>(Edge(set([6, 7]), set([8])), Edge(set([1, 7]), set([8])),
     Edge(set([1]), set([6])), Edge(set([1, 2]), set([8, 7]))


MGtoolkit also defines a get inverse member in the Metagraph class to
derive the inverse of a metagraph. The inverse { also a metagraph { has a generating
set consisting of the original metagraph edges and edges that correspond
to combinations of elements from the original metagraph's generating set [1].
The snippet below shows the inverse metagraph for the previous example.

So, the resulting inverse metagraph contains six elements in its generating
set; four edges from the original metagraph and  and  which are the external
source and target respectively [1]. This inverse metagraph also has six edges.

.. code-block:: python

  1 inverse= mg2.get_inverse()
  2 # display results
  3 print('inverse:: %s' %repr(inverse))
  4
  5 # output
  6 inverse:: <`Metagraph'>(Edge(set(['Edge(set([1]), set([3, 4]))']), set(['
    Edge(set([3]), set([6]))'])), Edge(set(['Edge(set([1]), set([3, 4]))
    ', 'Edge(set([2]), set([5]))']), set(['Edge(set([4, 5]), set([7]))'])
    ), Edge(set(['Edge(set([3]), set([6]))', 'Edge(set([4, 5]), set([7]))
    ']), set(['Edge(set([6, 7]), set([8]))'])), Edge(set(['alpha']), set
    (['Edge(set([1]), set([3, 4]))'])), Edge(set(['alpha']), set(['Edge(
    set([2]), set([5]))'])), Edge(set(['Edge(set([6, 7]), set([8]))']),
    set(['beta'])))


The Metagraph class also defined a get efm member to derive a metagraph's
element flow metagraph (EFM). The edges in an EFM depicts direct element
flows [1]. The snippet below generates an EFM for our metagraph example by
considering a subset of the metagraph's generating set. As the output shows, the
generated EFM has a single edge.

.. code-block:: python

  1 generator_subset = {2,4,7}
  2 efm = mg2.get_efm(generator_subset)
  3 # display results
  4 print('efm:: %s' %repr(efm))
  5
  6 # output
  7 efm:: `Metagraph'>(Edge(set([2]), set([4])))

1.4 Conditional metagraphs

We now describe our implementation of a particular type of attributed meta-
graphs known as conditional metagraphs. These metagraphs have propositions
{ statements that may be true or false { as their qualitative attributes [1].

MGtoolkit defines a ConditionalMetagraph class to help create conditional
metagraph instances. The generating set of these metagraphs are partitioned
into variables and propositions [1]. The snippet shows how a conditional metagraph
is instantiated using our toolkit. Each of the conditional metagraph's Edge
objects include an attributes argument, which is assigned a list of propositions
applicable to each edge.

.. code-block:: python

  1 variable_set = set(range(1,8))
  2 propositions_set = set(['p1','p2'])
  3 cm = ConditionalMetagraph(variable_set, propositions_set)
  4 cm.add_edges_from([ Edge({1,2}, {3,4}, attributes=['p1']), Edge({2},
    {4,6}, attributes=['p2']), Edge({3,4}, {5}, attributes=['p1','p2']),
    Edge({4,6}, {5,7}, attributes=['p1']) ])
  5 print(repr(cm))
  6
  7 # output
  8 `<ConditionalMetagraph'>(Edge(set([1,2,'p1']), set([3,4])), Edge(set([2,'
    p2'], set([4,6])), Edge(set([3,4,'p1','p2']), set([5])), Edge(set
    ([4,6,'p1']), set([5,7])))'


MGtoolkit defines a get context member in the ConditionalMetagraph
class to derive the context of a metagraph instance. A context { also a
conditional metagraph { simplifies a conditional metagraph by taking in to account
any propositions that are known to be true or false [1]. The snippet below
creates a context for the previous conditional metagraph example, considering the
true and false proposition sets shown. The output depicts that the context
metagraph only retains two edges (from the original four edges) which are valid in
this context.

The ConditionalMetagraph class also supports four members for determining
connectivity and redundant properties: is connected, is fully connected,
is redundantly connected and non redundant. The rst two members evaluate
connectivity properties; i.e., the ability to connect certain input variables to
output variables. The last two members check redundancy; i.e., they determine
if there is more than one way to connect an input to an output.

.. code-block:: python

  1 true_props = {'p1'}
  2 false_props = {'p2'}
  3 context = cm.get_context(true_props, false_props)
  4 # display result
  5 print('context: %s'%repr(context))
  6
  7 # output
  8 context: `<ConditionalMetagraph'>(Edge(set([1,2,'p1']), set([3,4])), Edge
    (set(['p1',4,6]), set([5,7]))'

The snippet below evaluates each of these properties between the example
source and destination shown.

.. code-block:: python

  1 source = {1,3}
  2 target = {4}
  3 logical_expressions = ['p1 | p2']
  4 interpretations = [ [('p1',True), ('p2',False)] ]
  5 connected = cm.is_connected(source, target, logical_expressions,
    interpretations)
  6 fully_connected = cm.is_fully_connected(source, target,
    logical_expressions, interpretations)
  7 redundantly_connected = cm.is_redundantly_connected(source, target,
    logical_expressions, interpretations)
  8 non_redundant = cm.is_non_redundant(logical_expressions,interpretations)
  9 # display result
  10 print('connected: %s, fully_connected: %s, redundantly_connected: %s,
     non_redundant: %s '%repr(connected, fully_connected,
     redundantly_connected, non_redundant))
  11
  12 # output
  13 connected: False, fully_connected: False, redundantly_connected: True,
     non_redundant: True

References

1. Basu, A. and Blanning, R. W. Metagraphs and their applications, volume 15.
Springer Science & Business Media, 2007.























