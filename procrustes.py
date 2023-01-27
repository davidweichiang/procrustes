#!/usr/bin/env python

# usage: procrustes.py <force-tok> < <input-tagged> > <output-tagged>
# imposes tokenization of <force-tok> onto <input-tagged>

import sys
import optparse
import collections
import trees
import functools
import xml.etree.ElementTree as ET

spacepenalty = 0.5

class EditFailure(Exception):
    pass

@functools.total_ordering
class Item(object):
    def __init__(self, cost=0., ant=None, align=None):
        self.cost = cost
        self.align = align or []
        self.ant = ant

    def __eq__(self, other):
        return self.cost == other.cost
    def __ne__(self, other):
        return self.cost != other.cost
    def __lt__(self, other):
        return self.cost < other.cost

def levenshtein(s,t):
    """http://en.wikipedia.org/wiki/Levenshtein_distance"""
    m = len(s)
    n = len(t)
    # d[i][j] says how to get t[:j] from s[:i]
    d = [[None for j in range(n+1)] for i in range(m+1)]
    d[0][0] = Item()
    for i in range(m+1):
        for j in range(n+1):
            if i == j == 0: continue

            cands = []
            
            if i > 0 and j > 0:
                ant = d[i-1][j-1]
                if s[i-1] == t[j-1]:
                    cands.append(Item(cost=ant.cost+0, ant=ant, align=[(i-1,j-1)]))
                elif not s[i-1].isspace() and not t[j-1].isspace():
                    # substitution. don't allow substitution of/for space
                    cands.append(Item(cost=ant.cost+1, ant=ant, align=[(i-1,j-1)]))

            if i > 0:
                # deletion
                ant = d[i-1][j]
                if s[i-1].isspace():
                    cost = ant.cost+spacepenalty
                else:
                    cost = ant.cost+1
                cands.append(Item(cost=cost, ant=ant))

            if j > 0:
                # insertion
                ant = d[i][j-1]
                if t[j-1].isspace():
                    cost = ant.cost+spacepenalty
                else:
                    cost = ant.cost+1
                cands.append(Item(cost=cost, ant=ant))

            d[i][j] = min(cands)

    goal = d[m][n]
    if goal is not None:
        align = []
        cur = goal
        while cur is not None:
            align.extend(cur.align)
            cur = cur.ant
        align.reverse()
        return align
    else:
        raise EditFailure()

class XML(object):
    def __init__(self, s):
        self.xml = ET.fromstring(s)

    def __str__(self):
        return ET.tostring(self.xml, encoding='unicode', method='xml')

    def getchars(self):
        return ET.tostring(self.xml, encoding='unicode', method='text')

    def project(self, forcechars, charalign):
        # Inserted characters arbitrarily go to the right, except for
        # appended characters, which go to the left.

        sub = []
        si = di = 0
        for ai, a in enumerate(charalign):
            while si < a[0]:
                sub.append('')
                si += 1
            sub.append(forcechars[di:a[1]+1])
            si += 1
            di = a[1]+1
        while si < len(self.getchars()):
            sub.append('')
            si += 1
        sub[-1] += forcechars[di:]

        def visit(node, si):
            n = len(node.text)
            node.text = ''.join(sub[si:si+n])
            si += n
            for child in node:
                si = visit(child, si)
            if node.tail is not None:
                n = len(node.tail)
                node.tail = ''.join(sub[si:si+n])
                si += n
            return si

        visit(self.xml, 0)

class Tree(object):
    def __init__(self, s):
        self.t = trees.Tree.from_str(s)
        self.chars = " ".join(n.label for n in self.t.leaves())
        i = 0
        for node in self.t.bottomup():
            if len(node.children) == 0:
                if i > 0:
                    i += 1 # space
                node.span = (i,i+len(node.label))
                i += len(node.label)
            else:
                node.span = (node.children[0].span[0],node.children[-1].span[-1])

    def __str__(self):
        return str(self.t)

    def getchars(self):
        return self.chars
    
    def project(self, forcechars, charalign):
        raise NotImplementedError()

class Alignment(object):
    def __init__(self, s, english=False):
        self.english = english
        fields = s.split("\t")
        self.fwords = fields[0].split()
        self.ewords = fields[1].split()
        if english:
            self.fwords, self.ewords = self.ewords, self.fwords
        align = collections.defaultdict(set)
        for a in fields[2].split():
            fi, ei = a.split('-',1)
            fi, ei = int(fi),int(ei)
            if english: fi, ei = ei, fi
            align[fi].add(ei)

        # Convert to character alignment (on French side)
        self.fchars = []
        self.align = collections.defaultdict(set)
        for fi,fword in enumerate(self.fwords):
            if fi > 0:
                self.fchars.append(" ")
            for ei in align[fi]:
                for fci in range(len(self.fchars), len(self.fchars)+len(fword)):
                    self.align[fci].add(ei)
            self.fchars.extend(fword)

    def __str__(self):
        # Convert back to word alignment (on French side)
        align = []
        fci = 0
        for fi, fword in enumerate(self.fwords):
            if fi > 0:
                fci += 1
            a = set()
            for fcj in range(fci, fci+len(fword)):
                a |= self.align[fcj]
            align.extend((fi,ei) for ei in a)
            fci += len(fword)

        if not self.english:
            return "%s\t%s\t%s" % ("".join(self.fchars), " ".join(self.ewords), " ".join("%s-%s" % (fi,ei) for (fi,ei) in align))
        else:
            return "%s\t%s\t%s" % (" ".join(self.ewords), "".join(self.fchars), " ".join("%s-%s" % (ei,fi) for (fi,ei) in align))

    def getchars(self):
        return self.fchars

    def project(self, forcechars, charalign):
        align = collections.defaultdict(set)
        for fci,tci in charalign:
            align[tci] |= self.align[fci]
        self.align = align
        self.fchars = forcechars
        self.fwords = forcechars.split()

if __name__ == "__main__":
    optparser = optparse.OptionParser("usage: %prog [options] force-tok")
    optparser.add_option("-m", "--mode", dest="mode", default="align", help="input/output mode (trees)")
    optparser.add_option("--english", dest="english", action="store_true", default=False, help="operate on English side instead of French")
    optparser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="verbose output")
    (opts, args) = optparser.parse_args()

    if len(args) != 1:
        optparser.error("force-tok argument required (use -h option for help)")

    forcetokfile = open(args[0])

    for li, (inline, forceline) in enumerate(zip(sys.stdin, forcetokfile)):
        if opts.mode == "align":
            inlabel = Alignment(inline, opts.english)
        elif opts.mode == "tree":
            inlabel = Tree(inline)
        elif opts.mode == "xml":
            inlabel = XML(inline)
        forceline = " ".join(forceline.split())

        align = levenshtein(inlabel.getchars(), forceline)
        if opts.verbose:
            print(inlabel, file=sys.stderr)
            print(inlabel.getchars(), file=sys.stderr)
            print(forceline, file=sys.stderr)
            for si, ti in align:
                print(f'[{inlabel.getchars()[si]}]-[{forceline[ti]}]', file=sys.stderr)

        inlabel.project(forceline, align)
        if inlabel.getchars() != forceline:
            raise EditFailure(f'{inlabel.getchars()} != {forceline}')
        print(inlabel)
