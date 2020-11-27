import json

from django.core import serializers
from nltk.tree import Tree

def capitalize_form(field: str):
    field = field.split('_')
    field = ' '.join(field)
    return field.title()


def serialize_json(arr: list, fields: tuple = ()):
    ser = ''
    if len(fields) == 0:
        ser = serializers.serialize('json', arr)
    else:
        ser = serializers.serialize('json', arr, fields=fields)

    ret = []
    for obj in json.loads(ser):
        filtered_obj = obj['fields']
        filtered_obj['id'] = obj['pk']
        ret.append(filtered_obj)

    return ret


def reconstruct_sentences(snt):
    ret = []
    for s in snt:
        line = { 'uuid': s.uuid, 'body': [] }
        for i in range(len(s.words)):
            line['body'].append({
                'word': s.words[i],
                'category': s.categories[i],
            })
        ret.append(line)
    return ret


def makeCCGDeriv(tree: Tree):
    global i
    i = 0
    global n
    n = tree.height() - 1

    deriv = []
    for _ in range(n):
        deriv.append([])

    def traverse(node: Tree, lvl: int):
        global i
        global n
        if node.label()[1] == 'Leaf':
            deriv[1].append({
                'from': i,
                'to': i,
                'category': str(node.label()[0]),
            })
            deriv[0].append({
                'from': i,
                'to': i,
                'word': node[0][0],
            })
            i += 1
            return (i - 1, i - 1)

        cat = str(node.label()[0])
        opr = node.label()[1]

        if len(node) > 0:
            left = traverse(node[0], lvl + 1)
            if len(node) > 1:
                right = traverse(node[1], lvl + 1)
                frm = min(left[0], right[0])
                to = max(left[1], right[1])
                deriv[n - lvl - 1].append({
                    'from': frm,
                    'to': to,
                    'category': cat,
                    'operator': opr,
                })
                return (frm, to)

            deriv[n - lvl - 1].append({
                'from': left[0],
                'to': left[1],
                'category': cat,
                'operator': opr,
            })
            return (left[0], left[1])

        return (0, 0)

    traverse(tree, 0)
    return deriv

