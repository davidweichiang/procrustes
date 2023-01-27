#!/usr/bin/env python

# usage: procrustes.py <force-tok> < <input-tagged> > <output-tagged>
# imposes tokenization of <force-tok> onto <input-tagged>

import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
import optparse
import itertools, collections

spacepenalty = 0.5

class EditFailure(Exception):
    pass

class Item(object):
    def __init__(self, cost=0., ant=None, align=None):
        self.cost = cost
        self.align = align or []
        self.ant = ant

    def __cmp__(self, other):
        return cmp(self.cost, other.cost)

def levenshtein(s,t):
    """http://en.wikipedia.org/wiki/Levenshtein_distance"""
    m = len(s)
    n = len(t)
    # d[i][j] says how to get t[:j] from s[:i]
    d = [[None for j in xrange(n+1)] for i in xrange(m+1)]
    d[0][0] = Item()
    for i in xrange(m+1):
        for j in xrange(n+1):
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

class Tree(object):
    def __init__(self, s):
        self.t = tree.str_to_tree(s)
        self.chars = " ".join(self.t.frontier())
        i = 0
        for node in t.bottomup():
            if node.isleaf():
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
        pass

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
                for fci in xrange(len(self.fchars), len(self.fchars)+len(fword)):
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
            for fcj in xrange(fci, fci+len(fword)):
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

    forcetokfile = file(args[0])

    for li, (inline, forceline) in enumerate(itertools.izip(sys.stdin, forcetokfile)):
        inline = inline.decode('utf-8')
        if opts.mode == "align":
            inlabel = Alignment(inline, opts.english)
        elif opts.mode == "tree":
            inlabel = Tree(inline)
        forceline = forceline.decode('utf-8')
        forceline = " ".join(forceline.split())

        align = levenshtein(inlabel.getchars(), forceline)
        if opts.verbose:
            for si, ti in align:
                sys.stderr.write("[%s]-[%s]\n" % (inlabel.getchars()[si], forceline[ti]))

        inlabel.project(forceline, align)
        if inlabel.getchars() != forceline:
            raise EditFailure()
        print unicode(inlabel)
