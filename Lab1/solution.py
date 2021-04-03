import argparse
from queue import PriorityQueue


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

    def __lt__(self, node2):
        if self.heuristic:
            if (self.cost + self.heuristic[self.name]) == (node2.cost + self.heuristic[node2.name]):
                return self.name < node2.name
            return (self.cost + self.heuristic[self.name]) < (node2.cost + self.heuristic[node2.name])
        else:
            if self.cost == node2.cost:
                return self.name < node2.name
            return self.cost < node2.cost

    def __eq__(self, node2):
        return self.name == node2.name and self.cost == node2.cost


class StateSpace:
    def __init__(self, file_statespace, file_heuristic=""):
        self.file_statespace = file_statespace
        self.file_heuristic = file_heuristic

        with open(file_statespace, "r") as input_file1:
            self.init = self.readline_clean(input_file1)
            self.goals = set(self.readline_clean(input_file1).split(" "))
            self.transitions = dict()
            for line in input_file1.readlines():
                if line[0] == "#":
                    continue
                transition = line.strip().split(" ")
                for i in range(1, len(transition)):
                    child = transition[i].split(",")
                    self.transitions.setdefault(
                        transition[0][:-1], []).append((child[0], float(child[1])))

        if file_heuristic:
            with open(file_heuristic, "r") as input_file2:
                self.heuristic = dict()
                for line in input_file2.readlines():
                    if line[0] == "#":
                        continue
                    pair = line.strip().split(": ")
                    self.heuristic[pair[0]] = float(pair[1])

    @staticmethod
    def readline_clean(input_file):
        line = input_file.readline().strip()
        while line[0] == '#':
            line = input_file.readline().strip()
        return line

    def __str__(self):
        ret = "Initial state: {}\n\n".format(self.init)
        ret += "Goal states: {}\n\n".format(" ".join(self.goals))
        ret += "Transitions: {}\n\n".format(str(self.transitions))
        ret += "Heuristic: {}\n".format(str(self.heuristic))
        return ret

    def bfs_traverse(self, begin):
        opened = [Node(False, begin, 0)]
        closed = dict()
        while opened:
            n = opened.pop(0)
            if n.name in closed.keys():
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in sorted(self.transitions[n.name], key=lambda following: following[0]):
                if child[0] in closed.keys():
                    continue
                opened.append(Node(n, child[0], child[1]))
        return (False, dict())

    @staticmethod
    def path(curr, closed):
        res = []
        res.append(curr)
        while closed[curr][0] != "#":
            res.append(closed[curr][0])
            curr = closed[curr][0]
        res.reverse()
        return res

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

    def bfs(self):
        print("# BFS")
        self.output(self.bfs_traverse(self.init))

    def ucs_traverse(self, begin):
        opened = PriorityQueue()
        opened.put(Node(False, begin, 0))
        closed = dict()
        while opened:
            n = opened.get()
            if n.name in closed.keys():
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in self.transitions[n.name]:
                if child[0] in closed.keys():
                    continue
                opened.put(Node(n, child[0], child[1]))
        return (False, dict())

    def ucs(self):
        print("# UCS")
        self.output(self.ucs_traverse(self.init))

    def a_star_traverse(self, begin):
        opened = PriorityQueue()
        opened.put(Node(False, begin, 0, self.heuristic))
        closed = dict()
        while opened:
            n = opened.get()
            if n.name in closed.keys():
                continue
            closed[n.name] = (n.parent_name, n.cost)
            if n.name in self.goals:
                return (n, closed)
            for child in self.transitions[n.name]:
                child_node = Node(n, child[0], child[1], self.heuristic)
                if child_node.name in closed.keys():
                    if closed[child_node.name][1] < child_node.cost:
                        continue
                    else:
                        closed.pop(child_node.name)
                opened.put(Node(n, child[0], child[1], self.heuristic))
        return (False, dict())

    def a_star(self):
        print("# A-STAR {}".format(self.file_heuristic))
        self.output(self.a_star_traverse(self.init))

    def pred_cost(self, node):
        return node[0] + self.heuristic[node[1]]

    def determine_optimism(self):
        if not self.file_heuristic:
            print("# HEURISTIC-OPTIMISTIC HEURISTIC NOT DEFINED")
            return
        print("# HEURISTIC-OPTIMISTIC {}".format(self.file_heuristic))
        conclusion = True
        for state in sorted(self.heuristic.keys()):
            h_star = self.ucs_traverse(state)[0].cost
            res = self.heuristic[state] <= h_star
            conclusion = conclusion and res
            print("[CONDITION]: {} h({}) <= h*: {} <= {}".format('[OK]' if res else '[ERR]', state, self.heuristic[state], float(h_star)))
        if conclusion:
            print("[CONCLUSION]: Heuristic is optimistic.")
        else:
            print("[CONCLUSION]: Heuristic is not optimistic.")
        return conclusion

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
