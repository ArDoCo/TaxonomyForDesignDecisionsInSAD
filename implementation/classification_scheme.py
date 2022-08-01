from enum import Enum
from anytree import Node, RenderTree, find_by_attr


class ClassificationSchemeBuilder:
    """
    Represents the classification scheme (taxonomy) for design decisions.
    With the ClassificationSchemeBuilder, one can reproduce the scheme in a tree data structure.
    Use this class to retrieve subclasses of each category and relation between classes in the scheme.
    """
    def __init__(self):
        """
        Default constructor for class ClassificationSchemeBuilder.
        """
        pass

    def build_classification_scheme(self):
        """
        This builds the taxonomy, which is structured hierarchically, and returns its root note for traversing.
        Design decisions can be seen in the view of their parent class. Using the hierarchical order, one can unify
        classes of design decisions to more general parent classes.
        :return: classification scheme root node
        """
        design_decision = Node('design decision')

        existence_decision = Node('existence decision', parent=design_decision)
        property_decision = Node('property decision', parent=design_decision)
        executive_decision = Node('executive decision', parent=design_decision)

        structural_decision = Node('structural decision', parent=existence_decision)
        extra_systemic = Node('extra-systemic', parent=structural_decision)
        intra_systemic = Node('intra-systemic', parent=structural_decision)
        integration = Node('integration', parent=extra_systemic)
        data_file = Node('data file', parent=extra_systemic)
        component = Node('component', parent=intra_systemic)
        interface_ = Node('interface', parent=intra_systemic)
        class_related = Node('class-related', parent=intra_systemic)
        inheritance = Node('inheritance', parent=class_related)
        association = Node('association', parent=class_related)
        class_ = Node('class', parent=class_related)

        behavioral_decision = Node('behavioral decision', parent=existence_decision)
        function = Node('function', parent=behavioral_decision)
        messaging = Node('messaging', parent=behavioral_decision)
        algorithm = Node('algorithm', parent=behavioral_decision)
        relation = Node('relation', parent=behavioral_decision)

        arrangement_decision = Node('arrangement decision', parent=existence_decision)
        architectural_style = Node('architectural style', parent=arrangement_decision)
        architectural_pattern = Node('architectural pattern', parent=arrangement_decision)
        reference_architecture = Node('reference architecture', parent=arrangement_decision)

        design_rule = Node('design rule', parent=property_decision)
        guideline = Node('guideline', parent=property_decision)

        process_related = Node('organizational/process-related', parent=executive_decision)
        technological = Node('technological', parent=executive_decision)
        tool = Node('tool', parent=technological)
        programming_language = Node('programming language', parent=technological)
        platform = Node('platform', parent=technological)
        framework = Node('framework', parent=technological)
        database = Node('data base', parent=technological)
        boundary_interface = Node('boundary interface', parent=technological)
        api = Node('api', parent=boundary_interface)
        user_interface = Node('user interface', parent=boundary_interface)

        classification_scheme = design_decision
        return classification_scheme

