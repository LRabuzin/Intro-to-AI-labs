import argparse


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

    @staticmethod
    def initial(state):
        return (0, state, "#")

    @staticmethod
    def node(curr, following, cost):
        return (curr[0]+cost, following, curr[1])

    def bfs_traverse(self, begin):
        opened = [self.initial(begin)]
        closed = dict()
        while opened:
            n = opened.pop(0)
            if n[1] in closed.keys():
                continue
            closed[n[1]] = (n[2], n[0])
            if n[1] in self.goals:
                return (n, closed)
            for child in sorted(self.transitions[n[1]], key=lambda following: following[0]):
                if child[0] in closed.keys():
                    continue
                opened.append(self.node(n, child[0], child[1]))
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
        path_res = self.path(res[0][1], res[1])
        print("[PATH_LENGTH]: {}".format(len(path_res)))
        print("[TOTAL_COST]: {}".format(res[0][0]))
        print("[PATH]: {}".format(" => ".join(path_res)))

    def bfs(self):
        print("# BFS")
        self.output(self.bfs_traverse(self.init))

    def ucs_traverse(self, begin):
        opened = [self.initial(begin)]
        closed = dict()
        while opened:
            n = opened.pop(0)
            if n[1] in closed.keys():
                continue
            closed[n[1]] = (n[2], n[0])
            if n[1] in self.goals:
                return (n, closed)
            for child in self.transitions[n[1]]:
                if child[0] in closed.keys():
                    continue
                opened.append(self.node(n, child[0], child[1]))
            opened = sorted(opened, key=lambda t: (t[0], t[1]))
        return (False, dict())

    def ucs(self):
        print("# UCS")
        self.output(self.ucs_traverse(self.init))

    def a_star_traverse(self, begin):
        opened = [self.initial(begin)]
        closed = dict()
        while opened:
            n = opened.pop(0)
            closed[n[1]] = (n[2], n[0])
            if n[1] in self.goals:
                return (n, closed)
            for child in self.transitions[n[1]]:
                child_node = self.node(n, child[0], child[1])
                if child_node[1] in closed.keys():
                    if closed[child_node[1]][1] < child_node[0]:
                        continue
                    else:
                        closed.pop(child_node[1])
                same_ind = next((i for i in range(len(opened))
                                 if opened[i][1] == child_node[1]), -1)
                if same_ind != -1:
                    if opened[same_ind][0] < child_node[0]:
                        continue
                    else:
                        opened.pop(same_ind)
                opened.append(self.node(n, child[0], child[1]))
            opened = sorted(opened, key=lambda t: (self.pred_cost(t), t[1]))
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
            h_star = self.ucs_traverse(state)[0][0]
            res = self.heuristic[state] <= h_star
            conclusion = conclusion and res
            print(
                f"[CONDITION]: {'[OK]' if res else '[ERR]'} h({state}) <= h*: {self.heuristic[state]} <= {h_star}")
        if conclusion:
            print("[CONCLUSION]: Heuristic is optimistic")
        else:
            print("[CONCLUSION]: Heuristic is not optimistic")
        return conclusion

    def determine_consistency(self):
        if not self.file_heuristic:
            print("# HEURISTIC-CONSISTENT HEURISTIC NOT DEFINED")
            return
        print(f"# HEURISTIC-CONSISTENT {self.file_heuristic}")
        conclusion = True
        for transitionset in sorted(self.transitions.items()):
            state1 = transitionset[0]
            for transition in sorted(transitionset[1]):
                cost = transition[1]
                state2 = transition[0]
                res = self.heuristic[state1] <= self.heuristic[state2] + cost
                conclusion = conclusion and res
                print(
                    f"[CONDITION]: {'[OK]' if res else '[ERR]'} h({state1}) <= h({state2}) + c: {self.heuristic[state1]} <= {self.heuristic[state2]} + {cost}")
        if conclusion:
            print("[CONCLUSION]: Heuristic is consistent")
        else:
            print("[CONCLUSION]: Heuristic is not consistent")
        return conclusion


def main():
    parser = argparse.ArgumentParser(
        description="Search the state space of a problem")
    parser.add_argument("--alg", type=str, required=True, choices=["astar", "ucs", "bfs"],
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
