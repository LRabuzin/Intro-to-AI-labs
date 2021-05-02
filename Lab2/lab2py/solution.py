import sys

#Helper method for reading input without comments
def readlines_clean(input_file):
    lines = input_file.readlines()
    cleaned = []
    for line in lines:
        if line[0] != "#":
            cleaned.append(line.strip())
    return cleaned

#Class that represents a single literal
class Literal:
    def __init__(self, name):
        self.name = None
        self.negated = None
        self.set_name(name.strip())
    
    def negate(self):
        self.negated = not self.negated
        return self
    
    def set_name(self, name):
        if name[0] == '~':
            self.negated = True
            self.name = name[1:].lower()
        else:
            self.negated = False
            self.name = name.lower()
    
    def __eq__(self, other):
        return self.name == other.name and self.negated == other.negated
    
    def __repr__(self):
        ret = ""
        if self.negated:
            ret+='~'
        ret += self.name
        return ret
    
    def __hash__(self):
        return hash(repr(self))

class Clause:
    def __init__(self, line = None, parent1 = None, parent2 = None, is_nil = False):
        self.nil = is_nil
        self.num = None
        if parent1 is not None or parent2 is not None:
            self.parents = set([parent1, parent2])
        else:
            self.parents = set()
        self.literals = set()
        if line is not None:
            line = line.strip().lower().split(" v ")
            for name in line:
                self.literals.add(Literal(name.strip()))
    
    def set_literals(self, literals):
        self.literals = literals
    
    def is_empty(self):
        return self.literals == set()
    
    def is_tautology(self):
        for literal in self.literals:
            if Literal(repr(literal)).negate() in self.literals:
                return True
        return False
    
    def is_irrelevant(self):
        return self.is_empty() or self.is_tautology()
    
    def subsumes(self, other):
        return self.literals.issubset(other.literals)
    
    def switch_parent(self, original, subsequent):
        self.parents.remove(original)
        self.parents.add(subsequent)
    
    def negate(self):
        res = set()
        for literal in self.literals:
            new_literal = Literal(repr(literal))
            new_literal.negate()
            res.add(Clause(repr(new_literal)))
        return res
    
    def set_num(self, n):
        self.num = n
        
    def __eq__(self, other):
        return self.literals == other.literals
    
    def __len__(self):
        return len(self.literals)
    
    def __repr__(self):
        if self.nil:
            return "NIL"
        return " v ".join(sorted([str(item) for item in self.literals]))
    
    def __hash__(self):
        return hash(repr(self))
    
    #| operator represents resolution of two clauses, empty resolvent means tautology or impossible resolution
    def __or__(self, other):
        compl_intersection = None
        intersections = 0
        for literal in self.literals:
            temp = Literal(repr(literal))
            temp.negate()
            if temp in other.literals:
                compl_intersection = Literal(repr(literal))
                if intersections != 0:
                    return Clause()
                intersections += 1
        if compl_intersection is None:
            return Clause()
        if len(self) == 1 and len(other) == 1:
            return Clause(parent1 = self, parent2 = other, is_nil = True)
        new_clause = self.literals.union(other.literals)
        new_clause.remove(compl_intersection)
        new_clause.remove(compl_intersection.negate())
        res = Clause(parent1=self, parent2=other)
        res.set_literals(new_clause)
        return res

class KnowledgeBase:
    def __init__(self, list_of_clauses = None, user_commands = None):
        self.base = set()
        self.goal = None
        self.removed = set()
        if list_of_clauses is not None and user_commands is None:
            with open(list_of_clauses, 'r') as f:
                lines = readlines_clean(f)
                self.goal = Clause(lines.pop())
                for line in lines:
                    self.base.add(Clause(line))
        elif list_of_clauses is not None and user_commands is not None:
            self.commands = []
            with open(list_of_clauses, 'r') as f:
                lines = readlines_clean(f)
                for line in lines:
                    self.base.add(Clause(line))
            with open(user_commands, 'r') as f:
                commands = readlines_clean(f)
                for command in commands:
                    action = command[-2:].strip()
                    clause = Clause(command[:-2])
                    self.commands.append((action, clause))
        self.deletion()
    
    # method that implements deletion strategy
    def deletion(self):
        to_remove = set()
        for clause in self.base:
            if clause.is_irrelevant():
                to_remove.add(clause)
        for outer in self.base:
            for inner in self.base:
                if outer != inner:
                    if outer.subsumes(inner):
                        to_remove.add(inner)
        self.base = self.base.difference(to_remove)
        self.removed.update(to_remove)

    def update(self, new_set):
        self.base.update(new_set)

    # resolution algorithm (using deletion and set of support)
    def resolution(self):
        sos = KnowledgeBase()
        negated_goal = self.goal.negate()
        new = set()
        for outer in sorted(list(negated_goal), key = len):
            for inner in sorted(list(self.base), key = len):
                c = outer|inner
                if c.nil:
                    return c, sos, negated_goal
                if not c.is_empty() and not c in self.removed:
                    subsumed = False
                    for clause in sos.base.union(negated_goal).union(self.base):
                        if clause.subsumes(c):
                            subsumed = True
                            break
                    if not subsumed:
                        new.add(c)
        if new.issubset(sos.base.union(negated_goal).union(self.base)):
            return None, None, None
        sos.update(new)
        sos.deletion()
        while True:
            new = set()
            for outer in sorted(list(sos.base), key = len):
                for inner in sorted(list(sos.base), key = len):
                    c = outer|inner
                    if c.nil:
                        return c, sos, negated_goal
                    if not c.is_empty() and not c in self.removed:
                        subsumed = False
                        for clause in sos.base.union(negated_goal).union(self.base):
                            if clause.subsumes(c):
                                subsumed = True
                                break
                        if not subsumed:
                            new.add(c)
            for outer in sorted(list(sos.base), key = len):
                for inner in sorted(list(self.base), key = len):
                    c = outer|inner
                    if c.nil:
                        return c, sos, negated_goal
                    if not c.is_empty() and not c in self.removed:
                        subsumed = False
                        for clause in sos.base.union(negated_goal).union(self.base):
                            if clause.subsumes(c):
                                subsumed = True
                                break
                        if not subsumed:
                            new.add(c)
            if new.issubset(sos.base.union(negated_goal).union(self.base)):
                return None, None, None
            sos.update(new)
            sos.deletion()
    
    # method for outputting results for cooking call
    def execute(self):
        print("Constructed with knowledge:")
        print(self)
        print()
        for command in self.commands:
            print(f"User's command: {command[1]} {command[0]}")
            if command[0] == '+':
                self.base.add(command[1])
                print(f"added {command[1]}")
            elif command[0] == '-':
                self.base.discard(command[1])
                print(f"removed {command[1]}")
            else:
                self.goal = command[1]
                self.cook()
                self.goal = None
            print()

    # method for outputting results of user defined query
    def cook(self):
        res, support, negated_goal = self.resolution()
        if res is None:
            print(f"[CONCLUSION]: {self.goal} is unknown")
        else:
            n=1
            parents = []
            parents.extend(res.parents)
            closed_parents = []
            closed_base = []
            closed_goal = []
            while len(parents) > 0:
                curr_parent = parents.pop(0)
                parents.extend(curr_parent.parents)
                if curr_parent not in self.base and curr_parent not in negated_goal:
                    closed_parents.append(curr_parent)
                elif curr_parent in self.base:
                    closed_base.append(curr_parent)
                else:
                    closed_goal.append(curr_parent)
            closed_base.reverse()
            closed_goal.reverse()
            closed_parents.reverse()
            closed_parents.append(res)
            for clause in closed_base:
                print(f"{n}. {clause}")
                clause.set_num(n)
                n+=1
            for clause in closed_goal:
                print(f"{n}. {clause}")
                clause.set_num(n)
                n+=1
            print("===============")
            for clause in closed_parents:
                parent1 = clause.parents.pop()
                parent2 = clause.parents.pop()
                num1 = parent1.num
                num2 = parent2.num
                clause.parents.add(parent1)
                clause.parents.add(parent2)
                nums = sorted([num1, num2])
                print(f"{n}. {clause} ({nums[0]}, {nums[1]})")
                clause.set_num(n)
                n+=1
            print("===============")
            print(f"[CONCLUSION]: {self.goal} is true")

    # method for outputting resolution call
    def resolve(self):
        res, support, negated_goal = self.resolution()
        if res is None:
            print(f"[CONCLUSION]: {self.goal} is unknown")
        else:
            n = 1
            for clause in self.base:
                print(f"{n}. {clause}")
                clause.set_num(n)
                n+=1
            for clause in negated_goal:
                print(f"{n}. {clause}")
                clause.set_num(n)
                n+=1
            print("===============")
            parents = []
            parents.extend(res.parents)
            closed_parents = []
            while len(parents) > 0:
                curr_parent = parents.pop(0)
                parents.extend(curr_parent.parents)
                if curr_parent not in self.base and curr_parent not in negated_goal:
                    closed_parents.append(curr_parent)
            closed_parents.reverse()
            closed_parents.append(res)
            for clause in closed_parents:
                parent1 = clause.parents.pop()
                parent2 = clause.parents.pop()
                num1 = parent1.num
                num2 = parent2.num
                clause.parents.add(parent1)
                clause.parents.add(parent2)
                nums = sorted([num1, num2])
                print(f"{n}. {clause} ({nums[0]}, {nums[1]})")
                clause.set_num(n)
                n+=1
            print("===============")
            print(f"[CONCLUSION]: {self.goal} is true")

    def __repr__(self):
        res = "\n".join(sorted([str(item) for item in self.base]))
        if self.goal is not None:
            res += "\nGoal: " + str(self.goal)
        return res
    


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given!")
    elif sys.argv[1] == "resolution":
        if len(sys.argv) != 3:
            print("Incorrect number of arguments given")
        file_path = sys.argv[2]
        base = KnowledgeBase(file_path)
        base.resolve()
    elif sys.argv[1] == "cooking":
        if len(sys.argv) != 4:
            print("Incorrect number of arguments given")
        file_path = sys.argv[2]
        command_path = sys.argv[3]
        base = KnowledgeBase(file_path, command_path)
        base.execute()
