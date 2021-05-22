import math
import sys

class Node:
    def __init__(self, feature, branches, dataset):
        self.feature = feature
        self.branches = branches
        self.dataset = dataset

class Leaf:
    def __init__(self, label):
        self.label = label

class Dataset:
    def __init__(self, file_path = None, entries = None, features = None, label = None, actives = None):
        if file_path is not None:
            with open(file_path, 'r') as f:
                header = f.readline().strip().split(',')
                self.features = header[:-1]
                self.label = header[-1]
                self.entries = f.readlines()
                self.entries = [elem.strip().split(',') for elem in self.entries]
                self.actives = list(range(len(self.features)))
        else:
            if entries is None or features is None or label is None or actives is None:
                raise AttributeError("If not loading dataset, ALL attributes must be set manually")
            else:
                self.entries = entries
                self.label = label
                self.features = features
                self.actives = actives
        self.calculated_counts = None
        self.calculated_subsets = {}
        self.calculated_valuesets = {}
        self.calculated_labels = None
        self.calculated_entropy = None

    
    def get_subset(self, feature, value):
        res = self.calculated_subsets.setdefault((feature, value), None)
        if res is None:
            ind = self.features.index(feature)
            new_entries =list(filter(lambda elem: elem[ind] == value, self.entries))
            actives = list(self.actives)
            actives.remove(ind)
            res = Dataset(entries = new_entries, features = self.features, label = self.label, actives = actives)
            self.calculated_subsets[(feature, value)] = res
        return res
    
    def label_counts(self):
        res = self.calculated_counts
        if res is None:
            res = {}
            for entry in self.entries:
                count = res.setdefault(entry[-1], 0)
                count += 1
                res[entry[-1]] = count
            self.calculated_counts = res
        return res
    
    def unique_labels(self):
        res = self.calculated_labels
        if res is None:
            res = set([elem[-1] for elem in self.entries])
            self.calculated_labels = res
        return res
    
    def labels(self):
        return [elem[-1] for elem in self.entries]
    
    def entropy(self):
        res = self.calculated_entropy
        if res is None:
            counts = self.label_counts()
            acc = 0
            for _, count in counts.items():
                if count != 0:
                    acc += (count)/len(self) * math.log2((count)/len(self))
            res = -acc
            self.calculated_entropy = res
        return res
    
    def value_set(self, feature):
        res = self.calculated_valuesets.setdefault(feature, None)
        if res is None:
            index = self.features.index(feature)
            res = set([elem[index] for elem in self.entries])
            self.calculated_valuesets[feature] = res
        return res
    
    def discriminative_feature(self):
        information_gains = {}
        for index in self.actives:
            feature = self.features[index]
            gain = self.entropy()
            for value in self.value_set(feature):
                gain -= len(self.get_subset(feature, value))/len(self) * self.get_subset(feature, value).entropy()
            information_gains[feature] = gain
            # print(f"{feature}: {gain}")
        # print("==================================")
        sorted_gains = sorted(list(information_gains.items()), key = lambda val: (-val[1], val[0]))
        return sorted_gains[0][0]
    
    def is_empty(self):
        return len(self.entries) == 0
    
    def __len__(self):
        return len(self.entries)


class ID3():
    def __init__(self, max_depth = None):
        self.max_depth = max_depth
        self.root = None
    
    def fit(self, dataset):
        if self.max_depth is not None:
            d = 0
        else:
            d = None
        self.root = self.id3(dataset, dataset, d)

    def id3(self, dataset, parent_dataset, depth):
        if dataset.is_empty():
            counts = parent_dataset.label_counts()
            counts = sorted(list(counts.items()), key= lambda elem: (-elem[1], elem[0]))
            return Leaf(counts[0][0])
        if depth is not None and depth == self.max_depth:
            counts = dataset.label_counts()
            counts = sorted(list(counts.items()), key= lambda elem: (-elem[1], elem[0]))
            return Leaf(counts[0][0])
        labels = dataset.unique_labels()
        if len(dataset.actives) == 0 or len(labels) == 1:
            return Leaf(labels.pop())
        feature = dataset.discriminative_feature()
        branches = {}
        for value in dataset.value_set(feature):
            new_depth = None if depth is None else depth + 1
            branches[value] = self.id3(dataset.get_subset(feature, value), dataset, new_depth)
        return Node(feature, branches, dataset)
    
    def traverse(self, node, entry, feature_map):
        if isinstance(node, Leaf):
            return node.label
        next_node = node.branches.get(entry[feature_map[node.feature]])
        if next_node is None:
            label_counts = sorted(list(node.dataset.label_counts().items()), key = lambda elem: (-elem[1], elem[0]))
            return label_counts[0][0]
        return self.traverse(next_node, entry, feature_map)

    def predict(self, dataset):
        if self.root is None:
            raise Exception("model has to be fitted before prediction")
        res_predictions = []
        feature_map = {dataset.features[i]:i for i in range(len(dataset.features))}
        for entry in dataset.entries:
            res_predictions.append(self.traverse(self.root, entry, feature_map))
        return res_predictions
        
    def traverse_print(self, node, sequence):
        if isinstance(node, Leaf):
            for i in range(len(sequence)):
                print(f"{i+1}:{sequence[i][0]}={sequence[i][1]}", end = " ")
            print(node.label)
        else:
            for element in node.branches.items():
                self.traverse_print(element[1], sequence + [(node.feature, element[0])])

if __name__ == "__main__":
    training_path = sys.argv[1]
    testing_path = sys.argv[2]
    depth_limit = None
    if len(sys.argv) == 4:
        depth_limit = int(sys.argv[3])
    # training_path = "Lab3/lab3_files/datasets/titanic_train_categorical.csv"
    # testing_path = "Lab3/lab3_files/datasets/titanic_test_categorical.csv"
    # depth_limit = None
    training_dataset = Dataset(training_path)
    testing_dataset = Dataset(testing_path)
    algo = ID3(depth_limit)
    algo.fit(training_dataset)
    print("[BRANCHES]:")
    algo.traverse_print(algo.root, [])
    predictions = algo.predict(testing_dataset)
    print(f"[PREDICTIONS]: {' '.join(predictions)}")
    ground_truths = testing_dataset.labels()
    accuracy = sum([predictions[i] == ground_truths[i] for i in range(len(predictions))])/len(predictions)
    all_labels = sorted(list(set(predictions).union(set(ground_truths))))
    label_map = {all_labels[i]: i for i in range(len(all_labels))}
    print("[ACCURACY]: {:.5f}".format(accuracy))
    print("[CONFUSION_MATRIX]:")
    matrix = []
    for i in range(len(all_labels)):
        matrix.append([0]*len(all_labels))
    iterator = zip((label_map[ground_truths[i]] for i in range(len(predictions))), (label_map[predictions[i]] for i in range(len(predictions))))
    for pair in iterator:
        matrix[pair[0]][pair[1]] += 1
    for row in matrix:
        for elem in row:
            print(elem, end =" ")
        print()