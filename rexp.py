import sys

class NFA:
    node_total = 0

    def __init__(self, expression):
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

    def add_transition(self, current_state, symbol, next_state):
        if symbol not in self.transition[current_state]:
            self.transition[current_state][symbol] = set()
        self.transition[current_state][symbol].add(next_state)

    def add_state(self):
        new_state = len(self.states) + self.initial
        NFA.node_total += 1
        self.states.add(new_state)
        self.transition[new_state] = {}
        return new_state

    def print_NFA(self):
        """Prints the NFA."""
        print("\nNFA:")
        print("Sigma:\t" + " ".join(sorted(self.input_set)))
        print("------")
        all_states = sorted(self.transition.keys())
        for state in all_states:
            state_line = f"{state}:"

            for symbol in sorted(self.input_set):
                targets = self.transition[state].get(symbol, set())
                state_line += (f" {symbol}->" + "{" + ", ".join(str(t) for t in sorted(targets)) + "}")

            lambda_targets = self.transition[state].get("", set())
            state_line += (' ""->' + "{" + ", ".join(str(t) for t in sorted(lambda_targets)) + "}")

            print(state_line)
        print("------")
        print(str(self.initial) + ":  Initial State")
        print(",".join(str(t) for t in sorted(self.accepting_states)) + ":  Accepting State(s)")

    def literal_nfa(self, symbol):
        new_nfa = NFA(symbol)

        new_state = new_nfa.add_state()
        if new_nfa.reg_string not in new_nfa.input_set:
            new_nfa.input_set.add(new_nfa.reg_string)
        new_nfa.add_transition(new_nfa.initial, new_nfa.reg_string, new_state)
        new_nfa.accepting_states.add(new_state)

        return new_nfa

    def union_nfa(self, left_nfa, right_nfa):
        new_nfa = NFA("")

        new_nfa.transition.update(left_nfa.transition)
        new_nfa.transition.update(right_nfa.transition)

        new_nfa.add_transition(new_nfa.initial, "", left_nfa.initial)
        new_nfa.add_transition(new_nfa.initial, "", right_nfa.initial)

        new_nfa.accepting_states = new_nfa.accepting_states.union(left_nfa.accepting_states)
        new_nfa.accepting_states = new_nfa.accepting_states.union(right_nfa.accepting_states)

        new_nfa.input_set.update(left_nfa.input_set)
        new_nfa.input_set.update(right_nfa.input_set)

        return new_nfa

    def concat_nfa(self, left_nfa, right_nfa):
        new_nfa = NFA("")

        new_nfa.transition.update(left_nfa.transition)
        new_nfa.transition.update(right_nfa.transition)

        for states in left_nfa.accepting_states:
            new_nfa.add_transition(states, "", right_nfa.initial)

        new_nfa.add_transition(new_nfa.initial, "", left_nfa.initial)

        new_nfa.accepting_states = right_nfa.accepting_states

        new_nfa.input_set.update(left_nfa.input_set)
        new_nfa.input_set.update(right_nfa.input_set)

        return new_nfa

    def star_nfa(self, prev_nfa):
        new_nfa = NFA("")

        new_nfa.transition.update(prev_nfa.transition)
        new_nfa.add_transition(new_nfa.initial, "", prev_nfa.initial)

        for states in prev_nfa.accepting_states:
            new_nfa.add_transition(states, "", new_nfa.initial)

        new_nfa.accepting_states.add(new_nfa.initial)
        new_nfa.input_set.update(prev_nfa.input_set)

        return new_nfa

    def regex_to_postfix(self, regex):
        precedence = {"*": 3, ".": 2, "|": 1}
        output = []
        stack = []

        for token in regex:
            if token.isalnum():  # Token is a literal
                output.append(token)
            elif token == "(":
                stack.append(token)
            elif token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                stack.pop()  # Remove '('
            else:
                # token is an operator
                while (
                    stack
                    and stack[-1] != "("
                    and precedence.get(stack[-1], 0) >= precedence[token]
                ):
                    output.append(stack.pop())
                stack.append(token)

        # Pop any remaining operators
        while stack:
            output.append(stack.pop())

        return "".join(output)

    def postfix_to_nfa(self, postfix):
        stack = []

        for token in postfix:
            if token.isalnum():  # Treat as literal
                stack.append(self.literal_nfa(token))
            elif token == "*":
                # Kleene star is unary
                frag = stack.pop()
                stack.append(self.star_nfa(frag))
            elif token == ".":
                # Concatenation is binary
                frag2 = stack.pop()
                frag1 = stack.pop()
                stack.append(self.concat_nfa(frag1, frag2))
            elif token == "|":
                # Union is binary
                frag2 = stack.pop()
                frag1 = stack.pop()
                stack.append(self.union_nfa(frag1, frag2))
            else:
                raise ValueError("Unsupported token: " + token)

        # The final NFA fragment on the stack represents the complete NFA
        return stack.pop()


class DFA:
    def __init__(self, nfa):
        self.transition_table = {}
        self.initial_state = None
        self.accepting_states = set()
        self.input_set = sorted(nfa.input_set)
        self.convert_nfa_to_dfa(nfa)

    def convert_nfa_to_dfa(self, nfa):
        # define transition table
        t = nfa.transition

        # Get initial states
        p0 = lambda_closure(nfa.initial, t)

        # big_p's structure is -> key={the set of states}: value=int corresponding to the p number
        #   ex: {{q0, q1, q2}:0, {q0,q1}:1}
        big_p = {frozenset(p0): 0}

        # result will be the output transition table with a structure like so ->
        #   key=int p number: value=dict with structure-> key=letter from input set: value={set of states that value leads to}
        #   ex: {0:{'a':{p0,p1,p2}, 'b':{p0,p1}}, 1:{'a':{...}, ...}}
        result = {}

        # to_process will be a queue for DFA states (as frozensets) that still need processing
        to_process = [frozenset(p0)]

        p_count = 0
        alphabets = self.input_set

        while to_process:
            # pop the next DFA state set to process
            current_set = to_process.pop(0)
            current_num = big_p[current_set]

            # make sure the current DFA state has a dict in result
            if current_num not in result:
                result[current_num] = {}

            # go through each alphabet symbol for the current state set
            for alphabet in alphabets:
                found_set = set()
                # go through each NFA state in the current DFA state to see what states are reachable
                for state in sorted(current_set):
                    if alphabet in t[state]:
                        for destination in sorted(t[state][alphabet]):
                            found_set.update(lambda_closure(destination, t))

                # found_set done updating, so freeze it so it can hashed
                found_frozenset = frozenset(found_set)

                # if this new set of states hasn't been seen before, give it a new DFA number and add to queue
                if found_frozenset not in big_p:
                    p_count += 1
                    big_p[found_frozenset] = p_count
                    to_process.append(found_frozenset)

                # update the DFA transition table
                destination_p = big_p[found_frozenset]
                result[current_num][alphabet] = destination_p

        self.transition_table = result
        self.initial_state = 0 # initial state should always be 0
        # get accepting states
        for state_set, p_num in big_p.items():
            for num in nfa.accepting_states:
                if num in state_set:
                    self.accepting_states.add(p_num)

    # minimizes the DFA
    def minimize(self):
        self.remove_inaccessible()
        distinguishable_matrix = self.get_distinguishable_matrix()

        # reads from the distinguishable matrix to remove extra states from the transition diagram
        removed_states = {}
        states = list(self.transition_table.keys())
        number_of_states = len(states)
        for i in range(number_of_states):
            for j in range(i + 1, number_of_states):
                state1, state2 = states[i], states[j]
                if distinguishable_matrix[i][j] == 0 and self.transition_table.get(state2):
                    # print("Can compress " + str(state1) + " and " + str(state2))
                    self.transition_table.pop(state2)
                    removed_states[state2] = state1

                    # removing from accessible states if removed from transition
                    if state2 in self.accepting_states:
                        self.accepting_states.remove(state2)

        # updating transition table to get rid of old states
        for state, transition in self.transition_table.items():
            for token in self.input_set:
                next_state = transition.get(token)
                if next_state in removed_states:
                    transition[token] = removed_states[next_state]

    # removes extra inaccesible states from the DFA
    def remove_inaccessible(self):
        accessible = set()
        states_to_visit = [self.initial_state]

        while states_to_visit:
            current_state = states_to_visit.pop()
            if current_state not in accessible:
                accessible.add(current_state)
                for symbol in self.input_set:
                    next_state = self.transition_table.get(current_state).get(symbol)
                    states_to_visit.append(next_state)

        for current_state in self.transition_table:
            if current_state not in accessible:
                 del self.transition_table[current_state]

    # returns a matrix of distinguishability
    def get_distinguishable_matrix(self):
        states = list(self.transition_table.keys())
        index_map = {state: i for i, state in enumerate(states)} # extra dict that maps each DFA state to index in state list
        number_of_states = len(states)
        distinguishable_matrix = [[0 for i in range(number_of_states)] for i in range(number_of_states)] # set everything as not distinguishable to start

        # first sweep - marking states as distinguishable if they are accepting or not
        for i in range(number_of_states):
            for j in range(i+1, number_of_states):
                state1, state2 = states[i], states[j]
                state_1_accepting = state1 in self.accepting_states
                state_2_accepting = state2 in self.accepting_states
                if state_1_accepting != state_2_accepting:
                    distinguishable_matrix[i][j] = 1

        # check all remaining 0s - if their inputs are not both accepting/not accepting, mark as 1
        # exit loop if matrix has not been updated
        matrix_updated = True
        while matrix_updated == True:
            matrix_updated = False
            for i in range(number_of_states):
                for j in range(i+1, number_of_states):
                    if distinguishable_matrix[i][j] == 1:
                        continue # already distinguishable, no need to look more!
                    state1, state2 = states[i], states[j]
                    for token in self.input_set:
                        state_1_next = self.transition_table[state1].get(token)
                        state_2_next = self.transition_table[state2].get(token)
                        index_next_1, index_next_2 = sorted([index_map.get(state_1_next), index_map.get(state_2_next)]) # staying in the filled part of the matrix

                        # setting as distinguishable if next states are also distinguishable
                        if distinguishable_matrix[index_next_1][index_next_2] == 1:
                            distinguishable_matrix[i][j] = 1
                            matrix_updated = True
                            break

        return distinguishable_matrix


    def is_valid_sentence(self, sentence):
        current_state = self.initial_state

        # Go through each char in given sentence
        for char in sentence:
            if char in self.transition_table.get(current_state, []):
                # Transition to the next state, based on the current char/alphabet
                current_state = self.transition_table[current_state][char]
            else:
                # Fail as character/alphabet not defined for current state
                return False

        # return true if sentence ends at accepting state
        return current_state in self.accepting_states

    def print_DFA(self):
        """ Prints out the DFA. """
        print(" Sigma:\t\t" + "\t".join(sorted(self.input_set)))
        print("------------------")

        all_states = sorted(self.transition_table.keys())
        for state in all_states:
            state_line = f"\t{state}:"

            for symbol in sorted(self.input_set):
                target = self.transition_table[state].get(symbol, "-")
                state_line += "\t" + str(target)
            print(state_line)

        print("------------------")
        print(str(self.initial_state) + ":  Initial State")
        print(",".join(str(t) for t in sorted(self.accepting_states)) + ":  Accepting State(s)")

# string preprocessesing that adds dots between operators
def preprocess_string(regString):
    result = []
    n = len(regString)

    for i in range(n - 1):
        result.append(regString[i])
        if regString[i] not in "(.|." and regString[i+1] not in "*|).":
            result.append('.')

    # add last char
    result.append(regString[-1])
    return ''.join(result)


# checks that parentheses match and all operators are valid
def check_valid_regex(regex_string):
    stack = []
    index = 0
    operator = ["*", "|", "."]

    while index < len(regex_string):
        char = regex_string[index]
        if char == "(":
            stack.append(char)
        elif char == ")":
            if len(stack) == 0:
                return False
            else:
                stack.pop()
        elif not char.isalpha() and char not in operator:
            return False
        index += 1

    if len(stack) == 0:
        return True
    return False

# finds all states accessible through a given state/transition diagrams
def lambda_closure(state, transition_diagram, result=None):
    if result is None:
        result = set()

    result.add(state)

    current_transitions = transition_diagram[state]
    # if empty-string/lambda is a key
    if "" in current_transitions:
        for other_state in sorted(current_transitions[""]):
            lambda_closure(other_state, transition_diagram, result)

    return result

# reads the given file to see what strings are accepted within it
def list_accepted_strings(dfa, file_name):
    results = []
    with open(file_name, 'r') as file:
        content = file.read()
        for index, sentence in enumerate(content.split()):
            if dfa.is_valid_sentence(sentence):
                results.append(f"{index}:{sentence}")
    return results

def main():
    if len(sys.argv) == 3:
        user_entered_reg = sys.argv[1]
        file_name = sys.argv[2]
    else:
        print("Incorrect usage.")
        print("python rexp.py <regular expression> <input file>")
        quit()

    if check_valid_regex(user_entered_reg) is False:
        print("Invalid regular expression, exiting program.")
        quit()
    print(user_entered_reg + " is a valid regular expression")

    preprocessed_reg = preprocess_string(user_entered_reg)

    nfa = NFA("")
    postfix_reg = nfa.regex_to_postfix(preprocessed_reg)
    nfa = nfa.postfix_to_nfa(postfix_reg)
    nfa.print_NFA()

    dfa = DFA(nfa)
    print("\nDFA:")
    dfa.print_DFA()

    dfa.minimize()
    print("\nMinimized DFA:")
    dfa.print_DFA()

    accepted_strings = list_accepted_strings(dfa, file_name)
    print(f"\nL({user_entered_reg})")
    print(f"Accepted strings in {file_name}:")
    for accepted in accepted_strings:
        print(f"\t {accepted}")


if __name__ == "__main__":
    main()
