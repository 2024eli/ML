import sys;args = sys.argv[1:]
import math;
import random
import re;
import time;

#input looks like: G[graphType]#[W#][R#] Vvslcs[R[#]TB]+ E[mngmnt]vslcs1[=~]vslcs2[R[#]T]* E[mngmnt]vslcs1[NSEW]+[=~][R[#]T]*

def generate_grid(graph):
    #0 available
    grid = 'o'*graph['size']
    for i in graph["vertexProperties"]:
        grid = grid[:i] + 'R' + grid[i+1:]
    return grid

def print_grid(graph, grid):
    s = ''
    for i in range(graph["gH"]):
        s = s + grid[graph["gW"]*i:graph["gW"]*(i+1)] + '\n'
    return s

def buildGraph(size):
    max = int(size**0.5)
    width = 0
    difference = 100000
    for i in range(1, max+1):
        if size/i - int(size/i) == 0:
            if int(size/i) - size/int(size/i) < difference:
                width = int(size/i)
                difference = width - size/width
    height = int(size/width)
    return width, height

def valid1(graph, newR, newC, newInd):
  return (0 <= newR < graph["gH"] and 0 <= newC < graph["gW"] and 0 <= newInd < graph["size"])

def grfNbrs(graph, node):
    dy = [0, 0, 1, -1]
    dx = [1, -1, 0, 0]
    if graph['width'] == 0: return []
    nbrs = list()
    row = node // graph['gW']
    col = node % graph['gW']
    for i in range(len(dy)):
        newR = row + dy[i]
        newC = col + dx[i]
        newInd = newR * graph['gW'] + newC
        if valid1(graph, newR, newC, newInd) and ((node, newInd) in graph["edges_ds"]):
            nbrs.append(newInd)
    #jumps
    for i, j in graph["jumps"]:
        if (node == i) and ((i,j) in graph["edges_ds"]): nbrs.append(j)
    return nbrs

def nbrs(graph, node):
    dy = [0, 0, 1, -1]
    dx = [1, -1, 0, 0]
    if graph['width'] == 0: return []
    nbrs = list()
    row = node // graph["gW"]
    col = node % graph["gW"]
    for i in range(len(dy)):
        newR = row + dy[i]
        newC = col + dx[i]
        newInd = newR * graph["gW"] + newC
        if valid1(graph, newR, newC, newInd):
            nbrs.append(newInd)
    return nbrs

def isValid_edge(graph, index, direc):
    direction = {'N': -graph["gW"], 'S': graph["gW"], 'E': 1, 'W': -1}
    next = index+direction[direc]
    if direc == 'E' or direc == 'W':
        if next//graph["gW"] != index//graph["gW"]: return False
    if direc == 'S' or direc == 'N':
        if next%graph["gW"] != index%graph["gW"]: return False
    if not (0<=next<graph['size']): return False
    return True

def process_edge_directive1(graph, edg, vb, jum, toggle, edges, connector, reward): #list of (toggle, first, connector, second, reward)
    edges_ds = {i: edg[i] for i in edg}
    vBound = {i for i in vb}
    jumps = {j for j in jum}
    ed = []
    direction = {-graph["gW"], graph["gW"], 1, -1}
    if connector == '=':
        for s1, s2 in edges:
            if s1 != s2:
                ed.append((s2, s1))
    # print("edges to del: ", edges)
    edges += ed
    # toggles -----------
    if toggle == '+':
        for e in edges:
            if e not in edges_ds:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    elif toggle == '!':
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
    elif toggle == '*':
        for e in edges:
            edges_ds[e] = reward
            if e in vBound: vBound -= {e}
            # else: vBound.add(e)
    elif toggle == '~':
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
            else:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    elif toggle == '@':
        for e in edges:
            if e in edges_ds:
                edges_ds[e] = reward
    else: #actually toggle
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
            else:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    for i, j in edges_ds:
        if i-j not in direction or (i+1==j and i//graph["gW"] != j//graph["gW"]) or (j+1==i and i//graph["gW"] != j//graph["gW"]):
            jumps.add((i,j))
            # print(i,j)
    # print(graph)
    return edges_ds, vBound, jumps

def process_edge_directive2(graph, edg, vb, jum, toggle, slice, direc, connector, reward): #list of (toggle, first, connector, second, reward)
    direction = {'N': -graph["gW"], 'S': graph["gW"], 'E': 1, 'W': -1}
    dire = {-graph["gW"], graph["gW"], 1, -1}
    edges_ds = {i: edg[i] for i in edg}
    jumps = {j for j in jum}
    vBound = {i for i in vb}
    s1 = stringSlc(slice, [i for i in range(graph["size"])])
    edges = []
    for s in s1:
        for d in direc:
            if isValid_edge(graph, s, d):
                edges.append((s, s+direction[d]))
                if connector=='=':
                    edges.append((s+direction[d], s))
   # toggles -----------
    if toggle == '+':
        for e in edges:
            if e not in edges_ds:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    elif toggle == '!':
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
    elif toggle == '*':
        for e in edges:
            edges_ds[e] = reward
            if e in vBound: vBound -= {e}
            # else: vBound.add(e)
    elif toggle == '~':
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
            else:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    elif toggle == '@':
        for e in edges:
            if e in edges_ds:
                edges_ds[e] = reward
    else: #actually toggle
        for e in edges:
            if e in edges_ds:
                del edges_ds[e]
                vBound.add(e)
            else:
                edges_ds[e] = reward
                if e in vBound: vBound -= {e}
    for i, j in edges_ds:
        if i-j not in dire or (i+1==j and i//graph["gW"] != j//graph["gW"]) or (j+1==i and i//graph["gW"] != j//graph["gW"]):
            jumps.add((i,j))
    return edges_ds, vBound, jumps

def stringSlc(slc, arr):
    #indexing
    if ':' not in slc:
        index = int(slc)
        return [arr[index]]
    #slicing
    parts = [int(part) if part else None for part in slc.split(':')]
    start, stop, step = parts + [None] * (3 - len(parts))
    return arr[slice(start, stop, step)]

def findBoundarySet(graph, arrSlices):
    #if theyre the same, then treat it as one
    dy = [0, 0, 1, -1]
    dx = [1, -1, 0, 0]
    bndSet = list()
    setOfSlicedIndices = set()
    # print(arrSlices)
    for slc in arrSlices:
        setOfSlicedIndices |= {*stringSlc(slc, [i for i in range(graph["size"])])}
    # print("listOfSlicedIndices", listOfSlicedIndices)
    for i in setOfSlicedIndices:
        row = i // graph["gW"]
        col = i % graph["gW"]
        for ct in range(4):
            newR = row + dy[ct]
            newC = col + dx[ct]
            ind = newR * graph["gW"] + newC
            if valid1(graph, newR, newC, ind):
                if dy[ct]+dx[ct] > 0:
                    bndSet.append((i, ind))
                else:
                    bndSet.append((ind, i))
        # if graph["jumps"]:
        #     for x, y in graph["edges_ds"]:
        #         # print(x, y, i, y==i and (y,x) in graph["jumps"])
        #         if x == i and (x,y) in graph["jumps"]:
        #             bndSet.append((x,y))
    # print(bndSet)
    return bndSet

def grfParse(lstArgs):
    SIZE = None
    gW = None
    gH = None
    wanted_jumps = set()
    vBound = set()
    jumps = set()
    vertexProperties = dict()
    graph = {"vertexProperties": vertexProperties, "size": 0, "width": 0, "gH":0, "gW":0, "rwd": 0, "type": None, "vBound": vBound, "wanted_jumps": wanted_jumps, "jumps": jumps}
    if (result := (re.search('^G([NGW]?)(\d*)(W(\d*))?(R(\d*))?$', lstArgs[0]))):
        graph["type"] = result.group(1)
        SIZE = int(result.group(2))
        graph["size"] = SIZE
        widthOverride = int(result.group(4)) if result.group(4) else None
        gW, gH = buildGraph(SIZE)
        if widthOverride == 0:
            print("Graph has width of 0")
        else:
            if widthOverride:
                gW, gH = widthOverride, int(SIZE / widthOverride)
            graph["width"], graph["gH"] = gW, gH
            graph['gW'] = gW
        if graph['type'] == 'N':
            graph['width'] = 0
            graph["gW"] = 0
        defRew = int(result.group(6)) if result.group(6) else 12
        graph["rwd"] = defRew

    indices = [i for i in range(SIZE)]
    edges_ds = dict()
    graph["edges_ds"] = edges_ds
    for node in range(SIZE):
        nb = nbrs(graph, node)
        for n in nb:
            edges_ds[(node, n)] = None

    for arg in lstArgs[1:]:
        #create more else cases
        if (result := (re.search('^V(.*?)((B)?R(\d*))?([TB]+)?$', arg))): #fix regex
            # print(result.groups())
            reward = int(result.group(4)) if result.group(4) else ''
            B = True if result.group(5) or result.group(3) else False
            indexOfReward = None
            if arg.find('R') != -1:
                indexOfReward = arg.find('R')
            if B and arg.find('R') != -1 and arg.find('B')<arg.find('R'):
                indexOfReward = arg.find('B')
            elif indexOfReward == None and B: indexOfReward = arg.find('B')
            setSlices = set(arg[1:indexOfReward].split(','))
            if B: #Boundary vertices----------------
                boundSet = findBoundarySet(graph, setSlices)
                # print(boundSet)
                # print(vBound)
                for i in boundSet:
                    if i[0] == i[1]: continue
                    iinJumps = False
                    if i in vBound:
                        # print('vBound.delete(i)', i)
                        vBound = vBound - {i}
                        edges_ds[i] = None
                        if i in jumps: 
                            jumps-={i}
                            iinJumps=True
                        if (i[1], i[0]) in edges_ds:
                            del edges_ds[(i[1], i[0])]
                            vBound.add((i[1], i[0]))
                            if (i[1], i[0]) in jumps:
                                jumps-={(i[1], i[0])}
                        else: 
                            if iinJumps:
                                continue
                                # jumps.add((i[1], i[0]))
                            edges_ds[(i[1], i[0])] = None
                            vBound -= {(i[1], i[0])}
                    else:
                        # print('vBound.add(i)', i)
                        vBound.add(i)
                        if i in edges_ds: 
                            del edges_ds[i]
                            if i in jumps:
                                iinJumps=True
                                jumps-={i}
                        if (i[1], i[0]) in edges_ds:
                            del edges_ds[(i[1], i[0])]
                            vBound.add((i[1], i[0]))
                            if (i[1], i[0]) in jumps:
                                jumps-={(i[1], i[0])}
                        else: 
                            if iinJumps:
                                continue
                                # jumps.add((i[1], i[0]))
                            edges_ds[(i[1], i[0])] = None
                            vBound -= {(i[1], i[0])} 
                setOfSlicedIndices = set()
                for slc in setSlices:
                    setOfSlicedIndices |= {*stringSlc(slc, [i for i in range(graph["size"])])}  
                for i in setOfSlicedIndices:
                    setOfDelJumps = set()
                    for x, y in jumps:  
                        # print(edges_ds)
                        if x==y: continue
                        if x==i and y in (setOfSlicedIndices - {i}): continue
                        if y==i and x in (setOfSlicedIndices - {i}): continue
                        if x == i and (x,y) in edges_ds:
                            del edges_ds[(x,y)]
                            setOfDelJumps.add((x,y))
                            if (y,x) in jumps: setOfDelJumps.add((y,x))
                        if y==i and (x,y) in edges_ds:
                            del edges_ds[(x,y)]
                            setOfDelJumps.add((y,x))
                            if (x,y) in jumps: setOfDelJumps.add((x,y))
                    # print(jumps, setOfDelJumps)
                    jumps -= setOfDelJumps
            # print('\n')
            graph["vBound"] = vBound
            graph["jumps"] = jumps
            if indexOfReward and arg.find('R') != -1:
                for sle in setSlices:
                    slicesCover = stringSlc(sle, indices)
                    for m in slicesCover:
                        if defRew or reward!=None: 
                            vertexProperties[m] = reward if reward!='' else defRew
        elif (result:=(re.search('^E([!+*~@])?([0-9,:\-]+?)([=~])(.+?)(R(\d*)T?)?$', arg))):
            # print(result.groups())
            toggle = result.group(1)
            firsts = result.group(2).split(',')
            connector = result.group(3)
            seconds = result.group(4).split(',')
            reward = None
            if arg.find('R') != -1:
                reward = int(result.group(6)) if result.group(6) else defRew
            # print((toggle, firsts, connector, seconds, reward))
            #prevent repeaters
            prevent = []
            f = []
            s = []
            for x in range(len(firsts)):
                f += [*stringSlc(firsts[x], indices)]
            for x in range(len(seconds)):
                s += [*stringSlc(seconds[x], indices)]
            for x in range(len(f)):
                s1 = f[x]
                s2 = s[x]
                # print(s1, s2)
                if connector=='=':
                    if (s1, s2) not in prevent and (s2, s1) not in prevent: prevent.append((s1, s2))
                else:
                    if (s1, s2) not in prevent: prevent.append((s1, s2))
            # print(prevent)
            edges_ds, vBound, jumps = process_edge_directive1(graph, edges_ds, vBound, jumps, toggle, prevent, connector, reward)
            graph["edges_ds"] = edges_ds
            graph["vBound"] = vBound
            graph["jumps"] = jumps
                # print(jumps)
        elif (result := (re.search('^E([!+*~@])?(.*?)([NSWE]+)([=~])(R(\d*)T?)?$', arg))):
            # print(result.groups())
            toggle = result.group(1)
            slices = result.group(2).split(',')
            direc = [*result.group(3)]
            connector = result.group(4)
            reward = None
            if arg.find('R') != -1:
                reward = int(result.group(6)) if result.group(6) else defRew
            for slice in slices:
                edges_ds, vBound, jumps = process_edge_directive2(graph, edges_ds, vBound, jumps, toggle, slice, direc, connector, reward)
                graph["edges_ds"] = edges_ds
                graph["vBound"] = vBound
                graph["jumps"] = jumps
        # print(graph)
    
    # print(f"\nVertex Policies: {vertexProperties}")
    # print(f"Boundaries @ Vertices: {vBound}")
    # print(f"Edges Directive: {edges_ds}\n")
    # print(graph)

    return graph #complete graph datastructure constructed from lstArgs

def grfSize(graph):
    return graph["size"]

def grfGProps(graph):
    ty = graph["type"]
    if ty == 'N':
        return {"rwd": graph['rwd']}
    return {"width": graph["width"], "rwd": graph["rwd"]} #dict of properties for graph, including "width" and "rwd"

def grfVProps(graph, v): 
    if v in graph['vertexProperties'] and graph['vertexProperties'][v]!=None:
        return {"rwd": graph['vertexProperties'][v]}
    return {} #dict of properties of vertex v

def grfEProps(graph, v1, v2):
    if (v1,v2) in graph["edges_ds"] and graph["edges_ds"][(v1,v2)]!=None:
        return {"rwd": graph["edges_ds"][(v1,v2)]}
    return {} #dict of properties of edge (v1,v2)

def grfStrEdges(graph, command=False):
    if graph['width'] == 0: return ''
    if graph['width'] != 0: 
        policy = solve(graph)
        if command: policy = print_grid(graph, policy)            
    #jumps
    for i, j in graph["jumps"]:
        if (i,j) in graph["edges_ds"]:
            graph["wanted_jumps"].add(f"{i}>{j}")
    j = jumpsfunc(graph["wanted_jumps"])
    return policy + '\n' + j #str of graph edges

def grfStrProps(graph):
    s = ''
    edg = graph["edges_ds"]
    for v in graph['vertexProperties']:
        s += str(v) + ": " + str(grfVProps(graph, v))[1:-1] + '\n'
    e = "\n".join(f"{v}: rwd: {edg[v]}" for v in edg if edg[v] != None)
    return str(grfGProps(graph))[1:-1] + '\n' + s + e #str of graph edges and properties

def policy_converter(graph, listOfPaths, ct):
    # print(ct, ":", listOfPaths)
    policy_key = {'ENW': '^', 'ENS': '>', 'NSW': '<', 'ESW':'v', 'ENSW': '+',
                'SW':'7', 'ES':'r','EN':'L','NW':'J','EW':'-','NS':'|', '*':'*',
                'N':'N', 'E':'E', 'S':'S', 'W':'W'}
    condense = set()
    if listOfPaths == []:
        return "*"
    directions = {1: 'E', -1:'W', graph['gW']: 'S', -graph['gW']: 'N'}
    direction = ''
    for p in listOfPaths:
        diff = p-ct
        if diff in directions and isValid_edge(graph, ct, directions[diff]): direction+=directions[diff]
    return policy_key[''.join(sorted(direction))] if direction else '.'

def possiblePath(graph, start):
    listOfPaths = set()
    for i, j in graph["edges_ds"]:
        if start == i:
            listOfPaths.add(j)
        # elif start == tup[1]:
        #     listOfPaths.add(tup[0])
    return listOfPaths, start

def jumpsfunc(wanted_jumps):
    if wanted_jumps == None: return
    repeats = set()
    onedir = []
    visited = {ju for ju in wanted_jumps}
    for ju in wanted_jumps:
        i, j = ju.split('>')
        if j!=i and j+'>'+i in wanted_jumps:
            if j+'>'+i in visited:
                repeats.add((i,j))
                visited = visited - {j+'>'+i}
        else:
            onedir.append((i,j))
        visited = visited - {ju}
    rStr = ''
    if repeats:
        front = ''
        back = ''
        for c in repeats:
            front = front+c[0]+ ','
            back = back+ c[1]+','
        rStr = front[:-1]+'='+back[:-1]
    odStr = ''
    if onedir:
        front = ''
        back = ''
        for c in onedir:
            front = front+c[0]+ ','
            back += c[1]+','
        odStr = front[:-1]+'~'+back[:-1]
    if odStr and rStr: rStr += ';'
    if odStr or rStr: return f"Jumps: {rStr}{odStr}"
    else: return ''
    
def solve(graph):
    policy = ''
    grid = generate_grid(graph)
    if not graph["vertexProperties"] and not graph["edges_ds"]:
        return '.'*graph["size"]
    for ind, it in enumerate(grid):
        policy+=policy_converter(graph, *possiblePath(graph, ind))
    return policy

def main():
    graph = grfParse(args)
    print(grfStrEdges(graph, True))
    print(grfStrProps(graph))
    # print("EProps: ", grfEProps(graph, 27, 28))
    # print("VProps: ", grfVProps(graph, 5))
    # print("Neighbors: ", grfNbrs(graph, 4),'\n')

if __name__ == '__main__': 
    if args == None: args = 'GG8W4'.split(' ')
    main()

#Evelyn Li, pd 7, 2024