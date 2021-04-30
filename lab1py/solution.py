import argparse
from queue import PriorityQueue, Queue

# Class that represents nodes in the search tree
class Node:
    def __init__(self, parent, name, transition_cost, heuristic=None):
        if parent:
            self.cost = parent.cost + transition_cost
            self.parent_name = parent.name
        else:
            self.cost = 0
            self.parent_name = "#"
        self.name = name
        self.heuristic = heuristic

    # Less than relation defined so that Node class could be used in PriorityQueue
    def __lt__(self, node2):
        if self.heuristic: # If the heuristic is given, the nodes will be sorted by the sum of node cost and value of the heuristic function
            if (self.cost + self.heuristic[self.name]) == (node2.cost + self.heuristic[node2.name]):
                return self.name < node2.name
            return (self.cost + self.heuristic[self.name]) < (node2.cost + self.heuristic[node2.name])
        else: # If no heuristic is given, the nodes will be sorted only by cost
            if self.cost == node2.cost:
                return self.name < node2.name
            return self.cost < node2.cost

    def __eq__(self, node2):
        return self.name == node2.name and self.cost == node2.cost

# Class that models the state space of the problem
class StateSpace:
    def __init__(self, file_statespace, file_heuristic=""):
        self.file_statespace = file_statespace
        self.file_heuristic = file_heuristic

        # Parsing the state space descriptor file
        with open(file_statespace, "r") as input_file1:
            self.init = self.readline_clean(input_file1)
            self.goals = set(self.readline_clean(input_file1).split(" "))
            self.transitions = dict()
            self.transpose = dict() # Transpose dictionary is used for dijkstra's algorithm, it represents the reversed transition relation
            for line in input_file1.readlines():
                if line[0] == "#":
                    continue
                transition = line.strip().split(" ")
                for i in range(1, len(transition)):
                    child = transition[i].split(",")
                    self.transitions.setdefault(transition[0][:-1], []).append((child[0], float(child[1])))
                    self.transpose.setdefault(child[0],[]).append((transition[0][:-1], float(child[1])))
                self.transitions.setdefault(transition[0][:-1], []) # In case of empty transition
        
        # Parsing the heuristic descriptor file
        if file_heuristic:
            with open(file_heuristic, "r") as input_file2:
                self.heuristic = dict()
                for line in input_file2.readlines():
                    if line[0] == "#":
                        continue
                    pair = line.strip().split(": ")
                    self.heuristic[pair[0]] = float(pair[1])

    # Method for reading the next non-comment line of a file
    @staticmethod
    def readline_clean(input_file):
        line = input_file.readline().strip()
        while line[0] == '#':
            line = input_file.readline().strip()
        return line

    # String represantation of a state space - for use in testing
    def __str__(self):
        ret = "Initial state: {}\n\n".format(self.init)
        ret += "Goal states: {}\n\n".format(" ".join(self.goals))
        ret += "Transitions: {}\n\n".format(str(self.transitions))
        ret += "Heuristic: {}\n".format(str(self.heuristic))
        return ret

    # Method that implements the BFS strategy - outputs final node and dictionary containing closed nodes
    def bfs_traverse(self, begin):
        opened = Queue()
        opened.put(Node(False, begin, 0))
        closed = dict() # Dictionary value is tuple (parent name, node cost) - used in path reconstruction
        while not opened.empty():
            n = opened.get()
            if n.name in closed:
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in sorted(self.transitions[n.name], key=lambda following: following[0]):
                if child[0] in closed:
                    continue
                opened.put(Node(n, child[0], child[1]))
        return (False, dict())

    # Method that reconstructs the path from closed dictionary, returns the path as a list of node names
    @staticmethod
    def path(curr, closed):
        res = []
        res.append(curr)
        while closed[curr][0] != "#":
            res.append(closed[curr][0])
            curr = closed[curr][0]
        res.reverse()
        return res

    # Method that outputs the result of <algorithm>_traverse methods formatted per the given instructions
    def output(self, res):
        if not res[0]:
            print("[FOUND_SOLUTION]: no")
            return
        print("[FOUND_SOLUTION]: yes")
        print("[STATES_VISITED]: {}".format(len(res[1])))
        path_res = self.path(res[0].name, res[1])
        print("[PATH_LENGTH]: {}".format(len(path_res)))
        print("[TOTAL_COST]: {}".format(res[0].cost))
        print("[PATH]: {}".format(" => ".join(path_res)))

    # Wrapper method for outputting BFS results
    def bfs(self):
        print("# BFS")
        self.output(self.bfs_traverse(self.init))

    # Method that implements the UCS strategy - outputs final node and dictionary containing closed nodes
    def ucs_traverse(self, begin):
        opened = PriorityQueue()
        opened.put(Node(False, begin, 0))
        closed = dict() # Dictionary value is tuple (parent name, node cost) - used in path reconstruction
        while not opened.empty():
            n = opened.get()
            if n.name in closed:
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in self.transitions[n.name]:
                if child[0] in closed:
                    continue
                opened.put(Node(n, child[0], child[1]))
        return (False, dict())

    # Wrapper method for outputting UCS results
    def ucs(self):
        print("# UCS")
        self.output(self.ucs_traverse(self.init))

    # Method that implements the A-star search algorithm - outputs final node and dictionary containing closed nodes
    def a_star_traverse(self, begin):
        opened = PriorityQueue()
        opened.put(Node(False, begin, 0, self.heuristic))
        closed = dict() # Dictionary value is tuple (parent name, node cost) - used in path reconstruction
        while not opened.empty():
            n = opened.get()
            if n.name in closed:
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in self.transitions[n.name]:
                child_node = Node(n, child[0], child[1], self.heuristic)
                if child_node.name in closed:
                    if closed[child_node.name][1] < child_node.cost:
                        continue
                    else:
                        closed.pop(child_node.name)
                opened.put(Node(n, child[0], child[1], self.heuristic))
        return (False, dict())

    # Wrapper method for outputting A-star results
    def a_star(self):
        print("# A-STAR {}".format(self.file_heuristic))
        self.output(self.a_star_traverse(self.init))
    
    # Dijkstra's algorithim for finding distances from every state to any of the goal nodes
    def dijkstra(self):
        distances_final = dict() # Minimal distances from every state to any of the goal states
        for goal in self.goals:
            opened = PriorityQueue()
            processed = set()
            distances_final[goal] = 0
            distances = dict() # Minimal distances from every state to current goal node
            distances[goal] = 0
            opened.put(Node(False, goal, 0))
            while not opened.empty():
                n = opened.get()
                if n.name in processed:
                    continue
                processed.add(n.name)
                if not n.name in self.transpose: # Source nodes in the state space graph do not have children in the transpose graph
                    continue
                for child in self.transpose.get(n.name):
                    if (not distances.get(child[0])) or distances.get(n.name) + child[1] < distances.get(child[0]):
                        distances[child[0]] = distances.get(n.name) + child[1]
                        opened.put(Node(n, child[0], distances[child[0]]-n.cost))
            for state in distances.keys(): # Updating distances to any goal state if a smaller distance was found for the current goal node
                if (not state in distances_final) or distances[state] < distances_final[state]:
                    distances_final[state] = distances[state]
        return distances_final

    # Method for determining whether the given heuristic is optimistic or not
    def determine_optimism(self):
        if not self.file_heuristic:
            print("# HEURISTIC-OPTIMISTIC HEURISTIC NOT DEFINED")
            return
        print("# HEURISTIC-OPTIMISTIC {}".format(self.file_heuristic))
        conclusion = True
        h_star = self.dijkstra() # We use the modified Dijkstra's algorithm implemented above to compute the oracle heuristic
        for state in sorted(self.heuristic.keys()):
            res = self.heuristic[state] <= h_star[state]
            conclusion = conclusion and res
            print("[CONDITION]: {} h({}) <= h*: {} <= {}".format('[OK]' if res else '[ERR]', state, self.heuristic[state], float(h_star[state])))
        if conclusion:
            print("[CONCLUSION]: Heuristic is optimistic.")
        else:
            print("[CONCLUSION]: Heuristic is not optimistic.")
        return conclusion

    # Method for determining whether the given heuristic is consistent or not
    def determine_consistency(self):
        if not self.file_heuristic:
            print("# HEURISTIC-CONSISTENT HEURISTIC NOT DEFINED")
            return
        print("# HEURISTIC-CONSISTENT {}".format(self.file_heuristic))
        conclusion = True
        for transitionset in sorted(self.transitions.items()):
            state1 = transitionset[0]
            for transition in sorted(transitionset[1]):
                cost = transition[1]
                state2 = transition[0]
                res = self.heuristic[state1] <= (self.heuristic[state2] + cost)
                conclusion = conclusion and res
                print("[CONDITION]: {} h({}) <= h({}) + c: {} <= {} + {}".format('[OK]' if res else '[ERR]',state1, state2, self.heuristic[state1], self.heuristic[state2], cost))
        if conclusion:
            print("[CONCLUSION]: Heuristic is consistent.")
        else:
            print("[CONCLUSION]: Heuristic is not consistent.")
        return conclusion


def main():
    parser = argparse.ArgumentParser(
        description="Search the state space of a problem")
    parser.add_argument("--alg", type=str, required=False, choices=["astar", "ucs", "bfs"],
                        help="search algorithm used", metavar="algorithm")
    parser.add_argument("--ss", type=str, required=True,
                        help="state space descriptor file", metavar="statespace")
    parser.add_argument("--h", type=str, required=False,
                        help="heuristic descriptor file", metavar="heuristic")
    parser.add_argument("--check-optimistic", required=False, action='store_true',
                        help="check whether the heuristic is optimistic")
    parser.add_argument("--check-consistent", required=False, action='store_true',
                        help="check whether the heuristic is optimistic")
    args = parser.parse_args()

    problem = StateSpace(args.ss, args.h)
    if args.alg == "astar":
        problem.a_star()
    elif args.alg == "bfs":
        problem.bfs()
    elif args.alg == "ucs":
        problem.ucs()
    if args.check_optimistic:
        problem.determine_optimism()
    if args.check_consistent:
        problem.determine_consistency()


if __name__ == "__main__":
    main()