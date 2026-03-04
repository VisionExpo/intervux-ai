import random


class KnowledgeNode:
    def __init__(self, name, difficulty=1):
        self.name = name
        self.difficulty = difficulty
        self.children = []
        self.parent = None


class InterviewKnowledgeGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, difficulty=1):
        if name in self.nodes:
            node = self.nodes[name]
            node.difficulty = difficulty
            return node
        node = KnowledgeNode(name, difficulty)
        self.nodes[name] = node
        return node

    def add_edge(self, parent, child):
        if parent not in self.nodes or child not in self.nodes:
            raise KeyError(f"Unknown node edge: {parent} -> {child}")
        parent_node = self.nodes[parent]
        child_node = self.nodes[child]
        if child_node not in parent_node.children:
            parent_node.children.append(child_node)
        child_node.parent = parent_node


def build_ml_graph():
    graph = InterviewKnowledgeGraph()

    graph.add_node("Machine Learning", difficulty=1)
    graph.add_node("Supervised Learning", difficulty=1)
    graph.add_node("Linear Regression", difficulty=1)
    graph.add_node("Logistic Regression", difficulty=1)
    graph.add_node("CNN", difficulty=2)
    graph.add_node("Transformers", difficulty=3)
    graph.add_node("Gradient Descent", difficulty=1)
    graph.add_node("Learning Rate", difficulty=2)
    graph.add_node("Batch Normalization", difficulty=3)
    graph.add_node("Dropout", difficulty=2)

    graph.add_edge("Machine Learning", "Supervised Learning")
    graph.add_edge("Supervised Learning", "Linear Regression")
    graph.add_edge("Supervised Learning", "Logistic Regression")
    graph.add_edge("Machine Learning", "CNN")
    graph.add_edge("Machine Learning", "Transformers")
    graph.add_edge("Machine Learning", "Gradient Descent")
    graph.add_edge("Gradient Descent", "Learning Rate")
    graph.add_edge("CNN", "Batch Normalization")
    graph.add_edge("CNN", "Dropout")

    return graph


def next_node(current_node, score):
    if current_node is None:
        return None

    if score >= 8 and current_node.children:
        return random.choice(current_node.children)

    if score <= 4 and current_node.parent:
        return current_node.parent

    return current_node


GRAPH = build_ml_graph()
