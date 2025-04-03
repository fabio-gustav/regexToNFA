import re
import nfa

reg = "ab*a|a(ba)*"



class nfa:

    def __init__(self):
        self.thing = {}
        self.acceptingStates = []
        self.initialState = 0
        self.nodeCount = 0
        self.currentNode = 0

    def addTransition(self,transition,endState):
        self.thing.update({transition: endState})

    def addLiteral(self,literal):
        if self.nodeCount > 0:
            self.thing.update({(self.currentNode,""):self.currentNode+1})
            self.nodeCount+=1
            self.currentNode+=1
            
        self.thing.update({(self.currentNode, literal):self.currentNode+1})
        self.nodeCount+=1
        self.currentNode+=1
    
    def addStarClosure(self,literals):
        #startNode = self.currentNode
        #for literal in literals:
            #self.addLiteral(literal)
        pass
        
    def addAlternation(self):
        pass
    
#def addStarClosure(inNode,)

dingus = nfa()

dingus.addLiteral("a")
dingus.addLiteral("b")

print(dingus.thing)

