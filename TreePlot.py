#coding=utf-8
from graphviz import Digraph

def test():
    tree = TestNode('A')
    tree.firstchild = TestNode('B')
    tree.firstchild.nextsibling = TestNode('C')
    tree.firstchild.firstchild = TestNode('D')
    TreePlot(tree,'TestTree').show()
    pass

class TreePlotNode:
    IDs = 0
    '''
    Plot Node
        member content() must be implemented,content() will be
        showed in the plot
    '''
    def __init__(self):
        self.firstchild = None
        self.nextsibling = None
        self.ID = self.IDs.__str__()
        self.type = 'node'
        self.shape = 'ellipse'
        self.color = 'black'
        TreePlotNode.IDs += 1

    def content(self):
        raise NotImplementedError,'You should implement TreePlotNode.content()!'

    def draw(self,dot):
        #draw self
        attrs = {'color':self.color,'shape':self.shape}
        dot.node(self.ID ,self.content(),attrs)
        #draw children
        child = self.firstchild
        while (child != None):
            child.draw(dot)
            child = child.nextsibling

class TreePlotEdge(TreePlotNode):
    def __init__(self,startnode,endnode):
        TreePlotNode.__init__(self)
        self.type = 'edge'
        self.shape = 'solid'
        self.startnode = startnode
        self.endnode = endnode

    def draw(self,dot):
        #draw self
        attrs = {'color':self.color,'style':self.shape}
        dot.edge(self.startnode.ID,self.endnode.ID,self.content(),attrs)
        #draw endnode
        self.endnode.draw(dot)

class TreePlot:
    def __init__(self,plottree,name):
        self.root = plottree
        self.name = name
        self.dot = Digraph(comment=self.name)
        pass

    def show(self):
        self.root.draw(self.dot)
        self.dot.render('TreePlot-output/'+self.name+'.gv', view=True)
        pass

class TestNode(TreePlotNode):
    def __init__(self, name):
        TreePlotNode.__init__(self)
        self.name = name

    def content(self):
        return self.name
