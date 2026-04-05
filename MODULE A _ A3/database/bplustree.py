from graphviz import Digraph


class BPlusTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []
        self.next = None


class BPlusTree:
    def __init__(self, t=3):
        self.root = BPlusTreeNode(leaf=True)
        self.t = t

    def search(self, key):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, k in enumerate(node.keys):
            if k == key:
                return node.values[i]
        return None

    def insert(self, key, value):
        root = self.root

        if len(root.keys) == (2 * self.t - 1):
            new_root = BPlusTreeNode()
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        if node.leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1

            if len(node.children[i].keys) == (2 * self.t - 1):
                self._split_child(node, i)
                if key >= node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, index):
        t = self.t
        node = parent.children[index]
        new_node = BPlusTreeNode(leaf=node.leaf)

        if node.leaf:
            new_node.keys = node.keys[t - 1:]
            new_node.values = node.values[t - 1:]

            node.keys = node.keys[:t - 1]
            node.values = node.values[:t - 1]

            new_node.next = node.next
            node.next = new_node

            parent.keys.insert(index, new_node.keys[0])
            parent.children.insert(index + 1, new_node)

        else:
            parent.keys.insert(index, node.keys[t - 1])

            new_node.keys = node.keys[t:]
            node.keys = node.keys[:t - 1]

            new_node.children = node.children[t:]
            node.children = node.children[:t]

            parent.children.insert(index + 1, new_node)

    def delete(self, key):
        if not self.root:
            return False

        self._delete(self.root, key)

        if not self.root.leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]

        return True

    def _delete(self, node, key):
        if node.leaf:
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                node.values.pop(idx)
            return

        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1

        child = node.children[i]

        if len(child.keys) < self.t:
            self._fix_child(node, i)

        if i >= len(node.children):
            i = len(node.children) - 1

        self._delete(node.children[i], key)

    def _fix_child(self, parent, idx):
        if idx > 0 and len(parent.children[idx - 1].keys) >= self.t:
            self._borrow_from_prev(parent, idx)
        elif idx < len(parent.children) - 1 and len(parent.children[idx + 1].keys) >= self.t:
            self._borrow_from_next(parent, idx)
        else:
            if idx < len(parent.children) - 1:
                self._merge(parent, idx)
            else:
                self._merge(parent, idx - 1)

    def _borrow_from_prev(self, parent, idx):
        child = parent.children[idx]
        sibling = parent.children[idx - 1]

        if child.leaf:
            child.keys.insert(0, sibling.keys.pop())
            child.values.insert(0, sibling.values.pop())
            parent.keys[idx - 1] = child.keys[0]
        else:
            child.keys.insert(0, parent.keys[idx - 1])
            parent.keys[idx - 1] = sibling.keys.pop()
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, parent, idx):
        child = parent.children[idx]
        sibling = parent.children[idx + 1]

        if child.leaf:
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))
            parent.keys[idx] = sibling.keys[0]
        else:
            child.keys.append(parent.keys[idx])
            parent.keys[idx] = sibling.keys.pop(0)
            child.children.append(sibling.children.pop(0))

    def _merge(self, parent, idx):
        child = parent.children[idx]
        sibling = parent.children[idx + 1]

        if child.leaf:
            child.keys.extend(sibling.keys)
            child.values.extend(sibling.values)
            child.next = sibling.next
        else:
            child.keys.append(parent.keys[idx])
            child.keys.extend(sibling.keys)
            child.children.extend(sibling.children)

        parent.keys.pop(idx)
        parent.children.pop(idx + 1)

    def update(self, key, new_value):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, k in enumerate(node.keys):
            if k == key:
                node.values[i] = new_value
                return True
        return False

    def range_query(self, start, end):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and start >= node.keys[i]:
                i += 1
            node = node.children[i]

        result = []
        while node:
            for i, key in enumerate(node.keys):
                if start <= key <= end:
                    result.append((key, node.values[i]))
                elif key > end:
                    return result
            node = node.next

        return result

    def get_all(self):
        node = self.root
        while not node.leaf:
            node = node.children[0]

        result = []
        while node:
            for i, key in enumerate(node.keys):
                result.append((key, node.values[i]))
            node = node.next

        return result

    def visualize_tree(self):
        dot = Digraph()
        self._add_nodes(dot, self.root)
        self._add_edges(dot, self.root)
        return dot

    def _add_nodes(self, dot, node):
        node_id = str(id(node))
        label = "|".join(map(str, node.keys))

        if node == self.root:
            dot.node(node_id, f"ROOT\n{label}", shape="ellipse", style="filled", color="lightblue")
        elif node.leaf:
            dot.node(node_id, f"Leaf\n{label}", shape="box", style="filled", color="lightgreen")
        else:
            dot.node(node_id, label, shape="ellipse")

        for child in node.children:
            self._add_nodes(dot, child)

    def _add_edges(self, dot, node):
        node_id = str(id(node))
        for child in node.children:
            dot.edge(node_id, str(id(child)))
            self._add_edges(dot, child)

        if node.leaf and node.next:
            dot.edge(str(id(node)), str(id(node.next)), style="dashed")
