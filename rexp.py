import re
import sys

class NFA:
    def __init__(self):
        self.states = {}
        self.acceptingStates = []
        self.initialState = 0
        self.nodeCount = 0
        self.currentNode = 0

    def preProcessString(self):
        for i in range(len(self.regString)):
            if self.regString[i] not in ["(",")","|","."] and self.regString[i+1] not in ["*","|",")"]:
                self.regString = self.regString[:i+1] + '.' + self.regString[i+1:]
            

    def addTransition(self,transition,endState):
        self.states.update({transition: endState})

    def addLiteral(self,literal):
        if self.nodeCount > 0:
            self.states.update({(self.currentNode,""):self.currentNode+1})
            self.nodeCount+=1
            self.currentNode+=1
            
        self.states.update({(self.currentNode, literal):self.currentNode+1})
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


if __name__ == '__main__':
    if len(sys.argv) == 2:
        reg = sys.argv[1]
    else:
        print("No regular expression entered, defaulting to ab*a|a(ba)*")
        reg = "ab*a|a(ba)*"

    dingus = NFA()
    dingus.addLiteral("a")
    dingus.addLiteral("b")
    print(dingus.states)



