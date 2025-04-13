import sys


reg = ""
class NFA:
    
    node_total = 0
    
    def __init__(self,expression):
        self.reg_string = expression
        self.input_set = set()
        self.transition = {}
        self.states = set()
        self.accepting_states = set()
        self.initial = NFA.node_total
        self.create_nfa()


    def create_nfa(self):
        self.states = {self.initial}
        NFA.node_total += 1
        self.transition = {self.initial: {}}
        
    def add_transition(self,current_state, symbol, next_state):
        if symbol not in self.transition[current_state]:
            self.transition[current_state][symbol] = set()
        self.transition[current_state][symbol].add(next_state)
        
    def add_state(self):
        new_state = len(self.states) + self.initial
        NFA.node_total += 1
        self.states.add(new_state)
        self.transition[new_state] = {}
        return new_state
            
        
def literal_nfa(symbol):
    
    new_nfa = NFA(symbol)
    
    new_state = new_nfa.add_state()
    if new_nfa.reg_string not in new_nfa.input_set:
        new_nfa.input_set.add(new_nfa.reg_string)
    new_nfa.add_transition(new_nfa.initial,new_nfa.reg_string,new_state)
    new_nfa.accepting_states.add(new_state)  
    
    return new_nfa   

def union_nfa(left_nfa,right_nfa):
    new_nfa = NFA("")
    
    new_nfa.transition.update(left_nfa.transition)
    new_nfa.transition.update(right_nfa.transition)
    
    new_nfa.add_transition(new_nfa.initial,"",left_nfa.initial)
    new_nfa.add_transition(new_nfa.initial,"",right_nfa.initial)
    
    new_nfa.accepting_states = new_nfa.accepting_states.union(left_nfa.accepting_states)
    new_nfa.accepting_states = new_nfa.accepting_states.union(right_nfa.accepting_states)
    
    new_nfa.input_set.update(left_nfa.input_set)
    new_nfa.input_set.update(right_nfa.input_set)
    
    return new_nfa 
    
        
        
def concat_nfa(left_nfa,right_nfa):
    new_nfa = NFA("")
    
    new_nfa.transition.update(left_nfa.transition)
    new_nfa.transition.update(right_nfa.transition)
    
    for states in left_nfa.accepting_states:
        new_nfa.add_transition(states,"",right_nfa.initial)
    
    new_nfa.add_transition(new_nfa.initial,"",left_nfa.initial)
    
    new_nfa.accepting_states = right_nfa.accepting_states
    
    new_nfa.input_set.update(left_nfa.input_set)
    new_nfa.input_set.update(right_nfa.input_set)
    
    return new_nfa 

def star_nfa(prev_nfa):
    new_nfa = NFA("")
    
    new_nfa.transition.update(prev_nfa.transition)
    
    new_nfa.add_transition(new_nfa.initial,"",prev_nfa.initial)
    
    for states in prev_nfa.accepting_states:
        new_nfa.add_transition(states,"",new_nfa.initial)
        
    new_nfa.accepting_states.add(new_nfa.initial)
    new_nfa.input_set.update(prev_nfa.input_set)
    
    return new_nfa 



def print_nfa(nfa):
    print("\nNFA:")
    print("Sigma:\t" + ' '.join(sorted(nfa.input_set)))
    print("------")
    all_states = sorted(nfa.transition.keys())
    for state in all_states:
        state_line = f"{state}:"

        for symbol in sorted(nfa.input_set):
            targets = nfa.transition[state].get(symbol, set())
            state_line += f" {symbol}->" + "{" + ', '.join(str(t) for t in sorted(targets)) + "}"

        lambda_targets = nfa.transition[state].get("", set())
        state_line += f' ""->' + "{" + ', '.join(str(t) for t in sorted(lambda_targets)) + "}"

        print(state_line)
    print("------")
    print(str(nfa.initial) + "  Initial State")
    print(str(nfa.accepting_states) + ":  Accepting State(s)")


def regex_to_postfix(regex):
    precedence = {'*': 3, '.': 2, '|': 1}
    output = []
    stack = []
    
    # Insert explicit concatenation operator if needed. You may preprocess your regex here.
    # ...
    
    for token in regex:
        if token.isalnum():  # Token is a literal (modify condition as needed)
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Remove '('
        else:
            # token is an operator
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
    
    # Pop any remaining operators
    while stack:
        output.append(stack.pop())
    
    return ''.join(output)


def postfix_to_nfa(postfix):
    stack = []
    
    for token in postfix:
        if token.isalnum():  # Treat as literal; adjust for your allowed symbols
            stack.append(literal_nfa(token))
        elif token == '*':
            # Kleene star is unary
            frag = stack.pop()
            stack.append(star_nfa(frag))
        elif token == '.':
            # Concatenation is binary
            frag2 = stack.pop()
            frag1 = stack.pop()
            stack.append(concat_nfa(frag1, frag2))
        elif token == '|':
            # Union is binary
            frag2 = stack.pop()
            frag1 = stack.pop()
            stack.append(union_nfa(frag1, frag2))
        else:

            raise ValueError("Unsupported token: " + token)
    
    # The final NFA fragment on the stack represents the complete NFA
    return stack.pop()


def main():
    
    def preProcessString(regString):
        for i in range(len(regString)):
            if regString[i-1] not in ["(",")","|",".","*"] and regString[i] not in ["*","|",")"]:
                regString = regString[:i] + '.' + regString[i:]
        return regString

    regg = preProcessString(reg)
    reggg = regex_to_postfix(regg)
    print(reggg)
    dingus = postfix_to_nfa(reggg)
    


    

    print(print_nfa(dingus))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        reg = sys.argv[1]
        main()
    else:
        print("No regular expression entered, defaulting to ab*a|a(ba)*")
        reg = "ab*a|a(ba)*"
        main()