#coding=utf-8
from graphviz import Digraph

def test():
    a = TestNode('A')
    b = TestNode('B')
    c = TestNode('C')
    d = TestNode('D')
    e = TestNode('E')
    a.appendchild(b)
    a.appendchild(c)
    b.appendchild(d)
    d.appendchild(e)
    e.appendchild(a)
    tree = a
    TreePlot(tree,'TestTree').show()
    pass

class TreePlotNode:
    IDs = 0 #static member
    def __init__(self):
        '''
            Plot Node
                member content() must be implemented,content()'s return
                value will be shown in the plot
        '''
        self.firstchild = None
        self.nextsibling = None
        self.ID = self.IDs.__str__()
        self.type = 'node'
        self.shape = 'ellipse'
        self.color = 'black'
        self.edges = {}
        self.name = ''
        self.hasbeendrawn = False
        TreePlotNode.IDs += 1

    def content(self):
        raise NotImplementedError,'You should implement TreePlotNode.content()!'

    def appendchild(self,child,edge=''):
        '''
        append a child for self,and connect self and child with (param edge)
        or create an edge named (param edge)
        :param child: child node
        :param edge: edge from self to child
                    if edge is a str,then create a TreePlotEdge(edge)
                    edge's startnode and endnode will be setted as self and chile
        :return: None
        '''
        if(isinstance(edge,str)):
            edge = TreePlotEdge(edge)
        edge.startnode = self
        edge.endnode = child
        self.edges[edge.name] = edge
        if(self.firstchild == None):
            self.firstchild = edge
        else:
            p = self.firstchild
            while(p.nextsibling != None):
                p = p.nextsibling
            p.nextsibling = edge

    def draw(self,dot):
        '''
        draw self in a dot
        draw self's children in dot include edges and node recursively
        :param dot: graphviz.Digraph object
        :return:None
        '''
        #draw self
        if(self.hasbeendrawn):
            return
        else:
            self.hasbeendrawn = True
        attrs = {'color':self.color,'shape':self.shape}
        dot.node(self.ID ,self.content(),attrs)
        #draw children
        child = self.firstchild
        while (child != None):
            child.draw(dot)
            child = child.nextsibling

    def reset(self):
        '''
        reset the .hasbeendrawn mark
        :return:
        '''
        if(self.hasbeendrawn):
            self.hasbeendrawn = False
            for edge in self.edges.values():
                edge.reset()

class TreePlotEdge(TreePlotNode):
    def __init__(self,name='',startnode=None,endnode=None):
        '''
        Plot Edge
        :param startnode:
        :param endnode:
        '''
        TreePlotNode.__init__(self)
        self.type = 'edge'
        self.shape = 'solid'
        self.startnode = startnode
        self.endnode = endnode
        self.name = name

    def draw(self,dot):
        '''
        draw self in dot
        draw self.endnode in dot
        :param dot:
        :return:
        '''
        #draw self
        attrs = {'color':self.color,'style':self.shape}
        dot.edge(self.startnode.ID,self.endnode.ID,self.content(),attrs)
        #draw endnode
        self.endnode.draw(dot)

    def content(self):
        return self.name

class TreePlot:
    def __init__(self,plottree,name):
        '''
        response for creating graphviz.Digraph object and invoke PlotNode's draw() funciton
        :param plottree:tree need to be drawed
        :param name:dot file's name
        '''
        self.root = plottree
        self.name = name
        self.dot = Digraph(comment=self.name)
        pass

    def show(self):
        '''
        draw and open the .pdf file
        :return:
        '''
        self.root.draw(self.dot)
        self.dot.render('TreePlot-output/'+self.name+'.gv', view=True)
        pass

class TestNode(TreePlotNode):
    def __init__(self, name):
        '''
        for test use
        :param name:
        '''
        TreePlotNode.__init__(self)
        self.name = name

    def content(self):
        return self.name
