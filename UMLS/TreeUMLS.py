import numpy as np
from ProcessUMLS import *

degree = 135

goodtypes = [
    'Congenital Abnormality', 'Acquired Abnormality', 'Injury or Poisoning',
    'Pathologic Function', 'Disease or Syndrome', 'None',
    'Mental or Behavioral Dysfunction', 'Cell or Molecular Dysfunction',
    'Experimental Model of Disease', 'Anatomical Abnormality',
    'Neoplastic Process', 'Sign or Symptom', 'Laboratory or Test Result'
]


def is_problem(concept):
    for ty in goodtypes:
        if ty in concept['types']:
            return True
    return False


# exploring the graph
def problem_parents(concept, hash_probs):
    res = []
    for par in concept['parents']:
        if hash_probs.get(par, False) and \
          not (par in res or par == concept['id']):
            res += [par]
    return res


def problem_children(concept, hash_probs):
    res = []
    for par in concept['children']:
        if hash_probs.get(par, False) and \
          not (par in res or par == concept['id']):
            res += [par]
    return res


def descendants(root_id, seen):
    total = 0
    seen[root_id] = 1
    queue = [root_id]
    while len(queue) > 0:
        cid = queue[0]
        children = [pid for pid in children_dic[cid] if seen[pid] == 0]
        for pid in children:
            seen[pid] = 1
            total += 1
            if total % 10000 == 0:
                print total, len(queue), queue[:10]
        queue = queue[1:] + children[:]
    return total


# getting a balanced tree
def descendants_list(root_id, seen):
    total = 0
    res_tree = {}
    seen[root_id] = 1
    queue = [root_id]
    while len(queue) > 0:
        cid = queue[0]
        children = [pid for pid in children_dic[cid] if seen[pid] == 0]
        res_tree[cid] = children
        for pid in children:
            seen[pid] = 1
            total += 1
            if total % 10000 == 0:
                print total, len(queue), queue[:10]
        queue = queue[1:] + children[:]
    return (res_tree, total)


def merge_trees(sta, stb):
    da = stb['depth'] - sta['depth'] - 1
    if sta['depth'] == 0 or da < 0:
        return
    if stb['structure'][da] > 0:
        sta['depth'] = 0    # merged, not useful anymore
        ls = stb['tree']
        for i in range(da):
            ls = ls[stb['structure'][i] - 1]
        ls[stb['structure'][da]] = sta['tree']
        stb['structure'][da] = (stb['structure'][da] + 1) % degree
        for i, num in enumerate(sta['structure']):
            stb['structure'][da + i + 1] = num


def group_trees(st_list):
    multi = (len(st_list) > 1)
    res = {}
    full_list = [st for st in st_list if st['structure'][0] == 0]
    todo_list = [st for st in st_list if st['structure'][0] > 0]
    todo_list = sorted(todo_list, key=lambda x: x['structure'][0])
    while len(todo_list) > 1 \
     and todo_list[0]['structure'][0] + todo_list[1]['structure'][0] <= degree:
        deg_a = todo_list[0]['structure'][0]
        j = len(todo_list) - 1
        while deg_a + todo_list[j]['structure'][0] > degree:
            j -= 1
        deg_b = todo_list[j]['structure'][0]
        for chid in range(deg_a):
            todo_list[j]['tree'][deg_b + chid] = todo_list[0]['tree'][chid]
        todo_list[j]['structure'] = todo_list[0]['structure']
        todo_list[j]['structure'][0] = (deg_a + deg_b) % degree
        todo_list = todo_list[1:]
        todo_list = sorted(todo_list, key=lambda x: x['structure'][0])
        if todo_list[0]['structure'][0] == 0:
            full_list += [todo_list[0]]
            todo_list = todo_list[1:]
    todo_list.reverse()
    stlist = full_list + todo_list
    if multi and len(stlist) == 1:
        res = stlist[0]
    else:
        res['depth'] = stlist[0]['depth'] + 1
        res['tree'] = [[] for d in range(degree)]
        for i, st in enumerate(stlist):
            res['tree'][i] = stlist[i]['tree']
        res['structure'] = [len(stlist) % degree] + stlist[-1]['structure']
    return res


def balance(desc_tree, root, level=0):
    # organise leaf children into tree
    leaves = [cid for cid in desc_tree[root] if len(desc_tree[cid]) == 0]
    leaves = [root] + leaves
    children = [cid for cid in desc_tree[root] if cid not in leaves]
    l_depth = 0
    struct = [len(leaves) % degree]
    if len(leaves) % degree > 0:
        leaves = leaves + [-1 for i in range(degree - len(leaves) % degree)]
    while len(leaves) > degree:
        l_depth += 1
        leaves = [leaves[degree * i:degree * (i+1)]
                  for i in range(len(leaves) / degree)]
        struct = [len(leaves) % degree] + struct
        if len(leaves) % degree > 0:
            empties = degree - len(leaves) % degree
            leaves = leaves + [[] for i in range(empties)]
    l_depth += 1
    leaf_tree = {}
    leaf_tree['tree'] = leaves
    leaf_tree['depth'] = l_depth
    leaf_tree['structure'] = struct
    # get trees from non-leaf children
    sub_trees = [leaf_tree] + [balance(desc_tree, cid, level + 1)
                               for cid in children]
    # merge sub_trees
    sub_trees = sorted(sub_trees, key=lambda x: x['depth'])
    ct = 0
    while len(sub_trees) > 1 and ct < 10:
        ct += 1
        min_depth = sub_trees[0]['depth']
        # insert smaller trees into available spaces
        for i, sta in enumerate(sub_trees):
            for j, stb in enumerate(sub_trees[i + 1:]):
                merge_trees(sta, stb)
        sub_trees = [st for st in sub_trees if st['depth'] > 0]
        # merge all of the shallowest trees
        to_merge = [st for st in sub_trees if st['depth'] == min_depth]
        pre_merge = [to_merge[i * degree:(i + 1) * degree]
                     for i in range(len(to_merge) / degree)]
        if len(to_merge) % degree > 0:
            pre_merge += [to_merge[(len(to_merge) / degree) * degree:]]
        merged = [group_trees(stlist) for stlist in pre_merge]
        sub_trees = merged + sub_trees[len(to_merge):]
    # return
    if level <= 1:
        print 'result depth:', sub_trees[0]['depth'],
        print 'struct:', sub_trees[0]['structure']
    return sub_trees[0]


# exploration and printing
def names(lst):
    ct = 0
    while lst[ct] > 0:
        print concepts[cuilist[lst[ct]]]['name'], '---',
        ct += 1


def write_tree(tree, depth, path=[], level=1):
    print '-' * level
    if level == depth:
        for i, num in enumerate(tree[:5]):
            if num == -1:
                break
            for p in path:
                print p, '\t',
            cui = cuilist[num]
            print i, '\t', cui, '\t', concepts[cui]['name']
    else:
        for i, tr in enumerate(tree[:5]):
            if tr == []:
                break
            write_tree(tr, depth, path + [i], level + 1)


def main():
    # We first read UMLS
    print 'Reading concepts'
    concepts, strtoid, nametoid, cuilist = read_concepts(METAdir)
    print 'Reading relations'
    read_relations(METAdir, concepts)
    print 'Reading types'
    read_sem_types(METAdir, concepts)

    # We focus on Problems concepts (as defined in goodtypes)
    problems = [(i, cui) for i, cui in enumerate(cuilist)
                if is_problem(concepts[cui])]
    problems_ids = [i for i, cui in problems]
    problems_cuis = [cui for i, cui in problems]
    # >>> concepts[cuilist[858266]]['name'] --- 'reason not stated concept'
    problems_ids.remove(858266)
    hash_probs = dict([(pid, True) for pid in problems_ids])

    # We then need to build the directed graph of parents/children relations
    problems_parents = [(pid,
                         problem_parents(concepts[cuilist[pid]], hash_probs))
                        for pid in problems_ids]
    problems_children = [(pid,
                          problem_children(concepts[cuilist[pid]]), hash_probs)
                         for pid in problems_ids]
    problems_neighbours = [(a[0], a[1] + b[1])
                           for a, b
                           in zip(problems_parents, problems_children)]
    children_dic = dict(problems_children)
    parents_dic = dict(problems_parents)
    neighbours = dict(problems_neighbours)

    # Let's look at the connected components in this graph
    seen = dict([(pid, 0) for pid in problems_ids])
    connected_components = []
    todo = [pid for pid in problems_ids if len(neighbours[pid]) > 0]
    while len(todo) > 0:
        current = todo[0]
        compo = []
        queue = [current]
        seen[current] = 1
        while len(queue) > 0:
            current = queue[0]
            seen[current] = 1
            compo += [current]
            c_neighbours = [pid for pid in neighbours[current]
                            if seen[pid] == 0]
            for pid in c_neighbours:
                seen[pid] = 1
            queue += c_neighbours
            queue = queue[1:]
            if len(compo) % 1000 == 0:
                print len(compo), len(queue)
        print 'compo', len(compo)
        connected_components += [compo[:]]
        todo = [pid for pid in todo if seen[pid] == 0]
        print 'todo', len(todo)

    # It turns out that the largest connected component accounts for 97.34%
    # of all the CUIs in SemEval (98.08 when counting cui-less), so let's
    # focus on that
    connected = sorted(connected_components, key=len, reverse=True)
    my_ids = connected[0][:]

    # The roots are the nodes of the directed graph which do not have a parent
    roots = [pid for pid in my_ids
             if len(children_dic[pid]) > 0 and len(parents_dic[pid]) == 0]
    roots = sorted(roots, key=lambda x: len(children_dic[x]), reverse=True)

    # We count the number of descendants of each of these roots
    seen = dict([(pid, 0) for pid in my_ids])
    n_desc = {}
    for root in roots:
        seen = dict([(pid, 0) for pid in my_ids])
        n_desc[root] = descendants(root, seen)

    # We then build a set of covering trees for the selected concepts. We
    # make the choice (heuristic) to assign a node with multiple parents
    # to the one with the least total dependants. The intuition behind the
    # is that it should make balancing slightly easier
    ls_desc = sorted(n_desc.items(), key=lambda x: x[1])
    my_roots = [pid for pid, num in ls_desc]
    root_trees = {}
    seen = dict([(pid, 0) for pid in my_ids])
    for root in my_roots:
        root_trees[root] = descendants_list(root, seen)

    # We add a common root to all of the covering trees
    desc_tree = dict([(pid, cids) for root_tree in root_trees.values()
                      for pid, cids in root_tree[0].items()])
    desc_tree[-2] = root_trees.keys()
    root = -2

    # Finally, we make a tree of fixed degree using our balancing heuristic
    bal_res = balance(desc_tree, root)

    # Some printing. TODO: write to file
    names(bal_res['tree'][0][0])
    write_tree(bal_res['tree'], bal_res['depth'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program loads RRF \
     using ProcessUMLS.py, then uses the children/parents ontology structure \
     of UMLS to make a tree of a given degree, using a heuristic to make it \
     as balanced as possible while keeping "close" concepts (in the original \
     tree distance) close')
    parser.add_argument("-data", "--umls_data",
                        help="location of the UMLS installation directory \
                              (hint: should contain a META and a NET folder)")
    parser.add_argument("-o", "--text_out",
                        help="text format output")
    parser.add_argument("-d", "--degree",
                        help="degree of the tree")
    args = parser.parse_args()
    if args.umls_data:
        METAdir = os.path.abspath(pjoin(args.data, 'META'))
    if args.text_out:
        text_file = os.path.abspath(args.text_out)
        write_text = True
    if args.degree:
        degree = args.degree
    print 'Starting'
    main()
