import sys

def readlines_clean(input_file):
    lines = input_file.readlines()
    cleaned = []
    for line in lines:
        if line[0] != "#":
            cleaned.append(line.strip())
    return cleaned

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
        self.children = set()
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
            if self.parents:
                parent1 = self.parents.pop()
                parent2 = self.parents.pop()
                self.parents.add(parent1)
                self.parents.add(parent2)
            else:
                parent1 = None
                parent2 = None
            res.add(Clause(repr(new_literal), parent1=parent1, parent2=parent2))
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
        new_clause = self.literals.copy().union(other.literals)
        new_clause.remove(compl_intersection)
        new_clause.remove(compl_intersection.negate())
        res = Clause(parent1=self, parent2=other)
        res.set_literals(new_clause)
        # print(f"Got {res} from {self} and {other}")
        self.children.add(res)
        other.children.add(res)
        return res

class KnowledgeBase:
    def __init__(self, list_of_clauses = None, user_commands = None):
        self.base = set()
        self.goal = None
        if list_of_clauses is not None:
            with open(list_of_clauses, 'r') as f:
                lines = readlines_clean(f)
                self.goal = Clause(lines.pop())
                for line in lines:
                    self.base.add(Clause(line))
        self.deletion()
    
    def deletion(self):
        to_remove = set()
        for clause in self.base:
            if clause.is_irrelevant():
                to_remove.add(clause)
        for outer in self.base:
            for inner in self.base:
                if outer != inner:
                    if outer.subsumes(inner):
                        # for child in inner.children:
                        #     child.switch_parent(inner, outer)
                        #     print(f"Switched parent for {child}:\n  {inner} with {outer}")
                        # outer.children.update(inner.children)
                        to_remove.add(inner)
        self.base = self.base.difference(to_remove)

    def update(self, new_set):
        self.base.update(new_set)

    def resolution(self):
        sos = KnowledgeBase()
        negated_goal = self.goal.negate()
        new = set()
        for outer in sorted(list(negated_goal), key = len):
            for inner in sorted(list(self.base), key = len):
                c = outer|inner
                if c.nil:
                    return c, sos, negated_goal
                if not c.is_empty():
                    for clause in sos.base.union(negated_goal).union(self.base):
                        if not clause.subsumes(c):
                            new.add(c)
        if new.issubset(sos.base.union(negated_goal).union(self.base)):
            return None, None, None
        sos.update(new)
        # sos.deletion()
        while True:
            new = set()
            for outer in sorted(list(sos.base), key = len):
                for inner in sorted(list(sos.base), key = len):
                    c = outer|inner
                    if c.nil:
                        return c, sos, negated_goal
                    if not c.is_empty():
                        for clause in sos.base.union(negated_goal).union(self.base):
                            if not clause.subsumes(c):
                                new.add(c)
            for outer in sorted(list(sos.base), key = len):
                for inner in sorted(list(self.base), key = len):
                    c = outer|inner
                    if c.nil:
                        return c, sos, negated_goal
                    if not c.is_empty():
                        for clause in sos.base.union(negated_goal).union(self.base):
                            if not clause.subsumes(c):
                                new.add(c)
            if new.issubset(sos.base.union(negated_goal).union(self.base)):
                return None, None, None
            sos.update(new)
            # sos.deletion()
        
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
        res += "\nGoal: " + str(self.goal)
    


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments given!")
    elif sys.argv[1] == "resolution":
        if len(sys.argv) != 3:
            print("Incorrect number of arguments given")
        file_path = sys.argv[2]
        base = KnowledgeBase(file_path)
        base.resolve()
    # base = KnowledgeBase("Lab2/lab2_files/resolution_examples/coffee_noheater.txt")
    # base.resolve()
