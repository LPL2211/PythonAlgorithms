from algs4.fundamentals.java_helper import java_string_hash

import sys

sys.setrecursionlimit(3100)


class Pipe:

    def __init__(self, key, val, height, predecessor=None):
        self.key = key
        self.value = val
        self.height = height
        self.previous_pipe = predecessor
        self._boxes = [None] * height
        self._top_reference = -1

    def insert_at(self, idx, pipe):
        self._boxes[idx] = pipe
        if pipe is not None:
            self._top_reference = max(idx, self._top_reference)

    @property
    def boxes(self):
        """
        Returns the references in top to bottom order.
        """
        return self._boxes[::-1]

    @property
    def top_reference(self):
        return self._top_reference

    @property
    def next_pipe(self):
        return self._boxes[0]

    def key_at_height(self, height):
        return self._boxes[height].key if height <= self.top_reference else None


class HashPipe:

    def __init__(self):
        self.root = Pipe(-float('inf'), "ROOT", 32, None)
        self.max_pipe = self.root
        self.min_pipe = None

    def size(self):
        pass

    def put(self, key, val):

        predecessor = self.floor(self.root, key, self.root)

        # key already exists
        if predecessor.key == key:
            predecessor.value = val
            return

        height = calculate_pipe_height(key)
        new_pipe = Pipe(key, val, height)
        new_pipe.previous_pipe = predecessor

        # update the max key and min key
        if self.max_pipe.value == "ROOT":
            self.max_pipe = new_pipe
            self.min_pipe = new_pipe

        if self.max_pipe.key < key:
            self.max_pipe = new_pipe

        if self.min_pipe.key > key:
            self.min_pipe = new_pipe

        # min element till now
        if predecessor.value is "ROOT":
            for i in range(height):
                old_ref = self.root._boxes[i]
                self.root.insert_at(i, new_pipe)
                new_pipe.insert_at(i, old_ref)
            return


        # otherwise, update the references
        predecessor_height = predecessor.height
        next_pipe = predecessor.next_pipe

        if next_pipe:
            next_pipe.previous_pipe = new_pipe

        # fit upto the common height
        for i in range(min(height, predecessor_height)):
            old_ref = predecessor._boxes[i]
            predecessor.insert_at(i, new_pipe)
            new_pipe.insert_at(i, old_ref)

        # if our new pipe is taller than the predecessor
        # we need to add forward references
        while height > predecessor_height and next_pipe:
            if next_pipe.height > predecessor_height:
                for i in range(predecessor_height,
                               min(next_pipe.height, height)):
                    new_pipe.insert_at(i, next_pipe)
                predecessor_height = min(next_pipe.height, height)
            next_pipe = next_pipe.next_pipe

        # we also need to check backward references
        if height > predecessor.height:
            covered_height = predecessor.height
            predecessor = predecessor.previous_pipe
            while predecessor is not None and covered_height < height:
                if predecessor.height > covered_height:
                    for i in range(covered_height, min(predecessor.height, height)):
                        predecessor.insert_at(i, new_pipe)
                    covered_height = min(predecessor.height, height)
                predecessor = predecessor.previous_pipe


    def get(self, key):
        pipe = self.floor(self.root, key, self.root)
        return pipe.value if pipe and pipe.key == key else None

    def exists(self, key):
        p = self.floor(self.root, key, self.root)
        return True if p and p.key == key else False

    def floor(self, start, key, cand):
        try:
            if self.max_pipe.key < key:
                return self.max_pipe
            if self.min_pipe.key > key:
                return self.root
        except:
            pass

        if start.key == key:
            return start

        top_ref = start.top_reference

        if top_ref == -1:
            return cand

        elif start.value != "ROOT" and start.key > key:
            return cand

        elif start._boxes[top_ref].key <= key:
            cand = start._boxes[top_ref]
            return self.floor(start._boxes[top_ref], key, cand)

        else:
            refs = start._boxes
            top_ref -= 1
            while top_ref >= 0:
                if refs[top_ref].key <= key:
                    cand = refs[top_ref]
                    res = self.floor(refs[top_ref], key, cand)
                    if res:
                        return res
                top_ref -= 1

        return cand

    def control(self, key, height):
        """
        Returns the key referenced at height `height`.
        """
        if self.exists(key):
            return self.floor(self.root, key, self.root).key_at_height(height)
        else:
            return None


def calculate_pipe_height(key):
    hash_code = java_string_hash(key)
    num_trailing_zeroes = 0

    while not hash_code & 1:
        num_trailing_zeroes += 1
        hash_code = hash_code >> 1

    return num_trailing_zeroes + 1


import string
# ex = list('SEARCHEXAMPLE')
ex = [ str(i) for i in range(5000) ]
# ex = [ str(i) for i in range(5000)]
ex = [k+'B' if java_string_hash(k+'A') % 2 == 0 else k+'A' for k in ( str(i) for i in range(25) )]
H =  HashPipe()
j=0
for k in ex:
    print("Insert: ", k)
    H.put(k, j)
    cl = [ H.control(-float('inf'), h) for h in range(32) ]
    #        print(cl)
    print( " ".join(x if x else '.' for x in cl) + "  : " + "ROOT" )
    for g in range(j+1):
        cl = [ H.control(ex[g], h) for h in range(32) ]
        #        print(cl)
        pipe = H.floor(H.root, ex[g], H.root)
        prev = pipe.previous_pipe.key if pipe.previous_pipe else "None"
        nxt = pipe.next_pipe.key if pipe.next_pipe else "None"
        print( " ".join(x if x else '.' for x in cl) + "  : " + ex[g] + " {} {}".format(pipe.height, prev, nxt))
    j += 1
