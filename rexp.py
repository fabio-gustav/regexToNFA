import sys

class NFA:
    def __init__(self,expression):
        self.regString = expression
        self.transitionFunctions = {}
        self.states = set()
        self.acceptingStates = set()
        self.initialState = "q0"
        #self.preProcessString()
        self.create_nfa()


    def create_nfa(self):
        self.states = {self.initialState}
        self.transitionFunctions = {self.initialState: {}}
        self.nfaRunner(self.regString, self.initialState)
        
    def nfaRunner(self,expression, startState):
        
        currentState = startState
        alternateStates = []
        
        for i in range(len(expression)):
            symbol = expression[i]
            
            if symbol == "(":
                
                nests = 1
                nextIndex = i + 1
                
                while nextIndex < len(expression) and nests > 0:
                    if expression[nextIndex] == "(":
                        nests += 1
                    elif expression[nextIndex] == ")":
                        nests -= 1

                    nextIndex += 1
                
                pExpression = expression[i+1:nextIndex-1]
                newState = self.addState()
                
                if '' not in self.transitionFunctions[currentState]:
                    self.transitionFunctions[currentState][''] = set()
                self.transitionFunctions[currentState][''].add(newState)
                
                currentState = self.nfaRunner(pExpression, newState)
                
                
                if nextIndex < len(expression) & (expression[nextIndex] == "*" | expression[nextIndex] == '.'):
                    repeatState = self.addState() #change this name
                    if expression[nextIndex] == '*':
                        if '' not in self.transitionFunctions[currentState]:
                            self.transitionFunctions[currentState][''] = set()
                        self.transitionFunctions[currentState][''].add(repeatState)
                        self.transitionFunctions[currentState][''].add(newState)
                    elif expression[nextIndex] == '.':
                        if '' not in self.transitionFunctions[currentState]:
                            self.transitionFunctions[currentState][''] = set()
                        self.transitionFunctions[currentState][''].add(repeatState)
                        
                    if '' not in self.transitionFunctions[repeatState]:
                        self.transitionFunctions[repeatState][""] = set()
                    self.transitionFunctions[repeatState][""].add(newState)
                    
                    currentState = repeatState
                    nextIndex +=1
                    
                i = nextIndex
            
            elif symbol == "|":
                branchState = self.addState()
                if "" not in self.transitionFunctions[startState]:
                    self.transitionFunctions[startState][""] = set()
                self.transitionFunctions[startState][""].add(branchState)
                
                alternateStates.append(self.nfaRunner(expression[i+1:], branchState))
                break
                
            elif symbol == "*":
                prev_symbol = expression[i-1]
                starState = self.addState()
                #create function for these
                if prev_symbol not in self.transitionFunctions[currentState]:
                    self.transitionFunctions[currentState][prev_symbol] = set()
                self.transitionFunctions[currentState][prev_symbol].add(currentState)
                
                if "" not in self.transitionFunctions[currentState]:
                    self.transitionFunctions[currentState][""] = set()
                self.transitionFunctions[currentState][""].add(starState)
                
                currentState = starState
                i+=1
                
            # elif symbol == ".":
            #     prev_symbol = expression[i-1]
            #     concatState = self.addState()
                
            #     if prev_symbol not in self.transitionFunctions[currentState]:
            #         self.transitionFunctions[currentState][prev_symbol] = set()
            #     self.transitionFunctions[currentState][prev_symbol].add(concatState)
                
            #     currentState = concatState
            #     i+=1
                
            else:
                newState = self.addState()
                if symbol not in self.transitionFunctions[currentState]:
                    self.transitionFunctions[currentState][symbol] = set()
                self.transitionFunctions[currentState][symbol].add(newState)
                currentState = newState
                i+=1
                
        for state in alternateStates:
            if "" not in self.transitionFunctions[alternateStates]:
                self.transitionFunctions[alternateStates][""] = set()
            self.transitionFunctions[alternateStates][""].add(currentState)
            
            
        self.acceptingStates.add(currentState)
        return currentState
                    


    def preProcessString(self):
        for i in range(len(self.regString)):
            if self.regString[i] not in ["(",")","|","."] and self.regString[i+1] not in ["*","|",")"]:
                self.regString = self.regString[:i+1] + '.' + self.regString[i+1:]
            

    def addTransition(self,transition,endState):
        self.states.update({transition: endState})
        
    def addState(self):
        newState = "q" + str(len(self.states))
        self.states.add(newState)
        self.transitionFunctions[newState] = {}
        return newState

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


def main():
    dingus = NFA(reg)

    print(dingus.transitionFunctions)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        reg = sys.argv[1]
        main()
    else:
        print("No regular expression entered, defaulting to ab*a|a(ba)*")
        reg = "ab*a"
        main()
        


