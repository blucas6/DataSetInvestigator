import networkx as nx
import matplotlib.pyplot as plt

class Figures:
    def __init__(self):
        self.FIGURE = 0
        self.figurelist = []
    
    def createHistogram(self, datadict, name, depth=10):
        self.figurelist.append(Histo(datadict, name, self.FIGURE, depth))
        self.FIGURE += 1

    def createGraph(self, data):
        self.figurelist.append(Graph(data))
    
    def showFigures(self):
        for f in self.figurelist:
            f.Show()
        plt.show()

class Histo:
    def __init__(self, datadict, name, figure, depth=10):
        self.data = datadict
        self.name = name
        self.depth = depth
        categories = list(self.data.keys())[len(self.data.keys())-depth:]
        categories = categories[::-1]
        values = list(self.data.values())[len(self.data.values())-depth:]
        values = values[::-1]
        plt.figure(figure)
        plt.bar(categories, values)
        plt.xticks(rotation=45)
        plt.xlabel('Values')
        plt.ylabel('Frequency')
        plt.title(f"Histogram for '{self.name}' column")
    
    def Show(self):
        pass

class Graph:
    def __init__(self, data):
        self.font_size = 10
        self.width = 1
        self.font_color = "black"
        self.edge_color = "red"
        self.font_weight = "bold"
        self.graph = nx.Graph()
        self.createNodes(data)
        self.createEdges(data)

    def Show(self):
        colors = nx.get_edge_attributes(self.graph, 'color').values()
        weights = nx.get_edge_attributes(self.graph, 'weight').values()
        nx.draw(self.graph, with_labels=True, edge_color=colors, font_color=self.font_color, font_weight=self.font_weight, font_size=self.font_size, width=list(weights))

    def createNodes(self, data):
        for review in data.keys():
            self.graph.add_node(review[-6:])

    def createEdges(self, data):
        for review in data.keys():
            for sim_rev in data[review]:
                self.graph.add_edge(review[-6:], sim_rev[-6:], color=self.edge_color, weight=data[review][sim_rev]*10)