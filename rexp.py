import sys


reg = ""
class NFA:
    
    node_total = 0
    
    def __init__(self,expression):
        self.reg_string = expression
        self.transition = {}
        self.states = set()
        self.accepting_states = set()
        self.initial = NFA.node_total
        self.create_nfa()


    def create_nfa(self):
        self.states = {self.initial}
        NFA.node_total += 1
        self.transition = {self.initial: {}}
        self.nfaRunner(self.reg_string)
        
    def nfaRunner(self,expression):
        
        if len(expression) <= 0:
            return
        
        
        
        
        for i in range(len(expression)):
            if expression[i] == "|":
                self.union_nfa(i)
                return
                
        for i in range(len(expression)):
            if expression[i] == ".":
                self.concat_nfa(i)
                return
            
        for i in range(len(expression)):
            if expression[i] == "*":
                self.star_nfa()
                return
        
        
        for i in range(len(expression)):
            if expression[i] == "(":
                
                nests = 1
                nextIndex = i + 1
                
                while nextIndex < len(expression) and nests > 0:
                    if expression[nextIndex] == "(":
                        nests += 1
                    elif expression[nextIndex] == ")":
                        nests -= 1

                    nextIndex += 1
                
                new_nfa = NFA(expression[i+1:nextIndex-1])
                
                self.transition.update(new_nfa.transition)
                self.accepting_states = new_nfa.accepting_states
                self.add_transition(self.initial,"",new_nfa.initial)
                
                # self.nfaRunner(self.reg_string[1:-1])
                return
        
        self.literal_nfa()
        return
                
                
        
                    
    def lambda_nfa(self):
        self.accepting_states.add(self.initial)
        
    def literal_nfa(self):
        new_state = self.add_state()
        self.add_transition(self.initial,self.reg_string,new_state)
        self.accepting_states.add(new_state)     

    def union_nfa(self,index):
        left_nfa = NFA(self.reg_string[:index])
        right_nfa = NFA(self.reg_string[index+1:])
        
        self.transition.update(left_nfa.transition)
        self.transition.update(right_nfa.transition)
        
        self.add_transition(self.initial,"",left_nfa.initial)
        self.add_transition(self.initial,"",right_nfa.initial)
        
        self.accepting_states = self.accepting_states.union(left_nfa.accepting_states)
        self.accepting_states = self.accepting_states.union(right_nfa.accepting_states)
        
    def concat_nfa(self,index):
        left_nfa = NFA(self.reg_string[:index])
        right_nfa = NFA(self.reg_string[index+1:])
        
        self.transition.update(left_nfa.transition)
        self.transition.update(right_nfa.transition)
        
        for states in left_nfa.accepting_states:
            self.add_transition(states,"",right_nfa.initial)
        
        self.add_transition(self.initial,"",left_nfa.initial)
        
        self.accepting_states = right_nfa.accepting_states

    def star_nfa(self):
        prev_nfa = NFA(self.reg_string[:-1])
        
        self.transition.update(prev_nfa.transition)
        
        self.add_transition(self.initial,"",prev_nfa.initial)
        
        for states in prev_nfa.accepting_states:
            self.add_transition(states,"",self.initial)
            
        self.accepting_states.add(self.initial)

    def add_transition(self,previous_state,symbol,new_state):
        if symbol not in self.transition[previous_state]:
            self.transition[previous_state][symbol] = set()
        self.transition[previous_state][symbol].add(new_state)
        
    def add_state(self):
        new_state = len(self.states) + self.initial
        NFA.node_total += 1
        self.states.add(new_state)
        self.transition[new_state] = {}
        return new_state




def main():
    
    def preProcessString(regString):
        for i in range(len(regString)):
            if regString[i] not in ["(",")","|","."] and regString[i+1] not in ["*","|",")"]:
                regString = regString[:i+1] + '.' + regString[i+1:]
        return regString

    regg = preProcessString(reg)

    dingus = NFA(regg)

    print(dingus.transition)
    print(dingus.accepting_states)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        reg = sys.argv[1]
        main()
    else:
        print("No regular expression entered, defaulting to ab*a|a(ba)*")
        reg = "(ab)*"
        main()
        


