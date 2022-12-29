'''
Title: Useful functions related to the MarkovGuitar project
Author: Gonzalo Contreras Aso
'''

import numpy as np
import networkx as nx
import guitarpro as gp
import copy


## General functions

def string_to_letter(string) -> str:
    '''
    Translate the gp5 indexing of strings to their actual notes
    '''
    if string == 1:
        return 'e'
    if string == 2:
        return 'B'
    if string == 3:
        return 'G'
    if string == 4:
        return 'D'
    if string == 5:
        return 'A'
    if string == 6:
        return 'E'
    
def letter_to_string(letter) -> int:
    '''
    Translate the base tuning of strings to indexing
    Careful! Not gp5 indexing (1-6), but rather python indexing (0-5)
    '''
    if letter == 'e':
        return 0
    if letter == 'B':
        return 1
    if letter == 'G':
        return 2
    if letter == 'D':
        return 3
    if letter == 'A':
        return 4
    if letter == 'E':
        return 5
    

## Random walk and print the resulting tab

def random_walk(G, start, length):
    '''
    Perform a random walk in G
    of length 'length' starting at 'start'.
    '''
    
    A = nx.to_numpy_array(G)
    nodelist = list(G.nodes())
    
    if start not in nodelist:
        raise Exception('Choose a valid start')
    
    i = 0
    walk = [start]
    
    while i < length:
        prob = A[nodelist.index(start)]
        start = np.random.choice(nodelist, 1, p=prob)[0]
        
        walk.append(start)
        
        i+=1
        
    return walk        


def render_tab(walk, tuning=['e','A','D','G','B','E'], measure = ['|','|','|','|','|','|'], separator = ['--','--','--','--','--','--']):
    '''
    From a random walk, write the corresponding tab.
    '''
    
    def transpose(M):
        return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]

    n = len(walk)
    
    T = [tuning, measure, measure, separator]
    
    # Separate the walk in beats
    for beat in walk:
        
        # Initialize the vertical line to add
        vertline = copy.copy(separator)

        # Count the notes with single digit frets
        single_digit = 0
        
        # Add the corresponding notes to the vertical line
        for subnote in beat.split('-'):
            string = letter_to_string(subnote[-1])
            fret = str(subnote[:-1])
            
            # Convert single digits to two digits
            if len(fret) == 1:
                fret = '-' + fret
                single_digit += 1
            
            vertline[string] = fret
            
        # Remove the extra dash if all of the notes in the 
        # vertical line have single digit frets
        if single_digit == len(beat.split('-')):
            vertline = [v[1] for v in vertline]  
        
        T.append(vertline)
        T.append(separator)
    
    T = transpose(T)    
    
    tab = ''
    
    for line in T:
        tab += ''.join(line) + '\n'
    
    return tab
    

## Get attributes of song
def get_song_attrs(song):
    '''
    From a guitarpro parsed file, obtain some basic info such as
    key, number of tracks, time signature
    '''
    
    ntracks = len(song.tracks)
    
    # Get notes on the graph, and the edges between them, with weights
    for track in song.tracks:

        for measure in track.measures:
            key = measure.keySignature.name
            frac = str(measure.timeSignature.numerator) + "/" + str(measure.timeSignature.denominator.value)
    
    return ntracks, key, frac
    

## Markov ones
def construct_chain(song, create_using=None, silence=True, track=None):
    '''
    From a guitarpro parsed file, build its corresponding
    Markov chain as a network with normalized out-degrees.
    If a graph G is provided in create_using, add new nodes/edges to it.
    '''
    
    if not create_using:
        G = nx.DiGraph()
    else:
        G = create_using
    
    key = None
    frac = None

    # Get notes on the graph, and the edges between them, with weights
    for track in song.tracks:

        for measure in track.measures:

            if measure.keySignature.name != key:
                key = measure.keySignature.name

            if str(measure.timeSignature.numerator) + "/" + str(measure.timeSignature.denominator.value) != frac:
                frac = str(measure.timeSignature.numerator) + "/" + str(measure.timeSignature.denominator.value)

            for voice in measure.voices[:-1]: # there is an extra, empty voice to remove at the end

                for beat in voice.beats:

                    if silence and len(beat.notes) == 0:
                        #### Later we will need to deal with this, including it.
                        continue

                    for i, note in enumerate(beat.notes):
                        
                        if i == 0:
                            node = str(note.value) + string_to_letter(note.string)
                        else:
                            node += '-' + str(note.value) + string_to_letter(note.string)
                        
                    G.add_node(node)

                    if 'prev_node' in locals():

                        edge = (prev_node, node)

                        if (prev_node, node) in G.edges:
                            G.edges[edge[0], edge[1]]['weight'] += 1
                        else:
                            G.add_edge(*edge, weight=1)

                    prev_node = node

    G.key = key
    G.frac = frac
    
    # Normalize the out-edge weights
    if not create_using:
        for node, degree in dict(G.out_degree()).items():

            sum_weights = np.sum([G.edges[edge[0], edge[1]]['weight'] for edge in G.out_edges(node)])

            for edge in G.out_edges(node):
                G.edges[edge[0], edge[1]]['weight'] /= sum_weights
    
    return G


## WITH MEMORY

def get_nodes(song, silence=True, track=None):
    '''
    Get the ordered list of nodes (which can be repeated) 
    involved in the song
    '''
    
    nodelist = []
    
    key = None
    frac = None

    # Get notes on the graph, and the edges between them, with weights
    for track in song.tracks:

        print(track.name)

        for measure in track.measures:

            if measure.keySignature.name != key:
                key = measure.keySignature.name
                print('Measure key:', key)

            if str(measure.timeSignature.numerator) + "/" + str(measure.timeSignature.denominator.value) != frac:
                frac = str(measure.timeSignature.numerator) + "/" + str(measure.timeSignature.denominator.value)
                print('Measure time signature:', frac)

            for voice in measure.voices[:-1]: # there is an extra, empty voice to remove at the end

                for beat in voice.beats:
                    
                    #print(beat)

                    if silence and len(beat.notes) == 0:
                        #### Later we will need to deal with this, including it.
                        nodelist.append('')
                        continue
                    
                    #print('past silence')

                    for i, note in enumerate(beat.notes):
                        
                        #print(i, note.value)
                        if i == 0:
                            node = str(note.value) + string_to_letter(note.string)
                        else:
                            node += '-' + str(note.value) + string_to_letter(note.string)
                        
                    nodelist.append(node)
    
    return nodelist, key, frac

def line_datagraph(song, silence=True, track=None):
    '''
    Construct the subgraph of the linegraph of the Markov chain, 
    dictated by the existence of the connections between edges in the data.
    '''
    
    LdG = nx.DiGraph()
    
    # Populate the graph without silences
    nodelist, key, frac = get_nodes(song)
    LdG.key = key
    LdG.frac = frac
    
    # Create the nodes of the Linegraph, i.e. the edges of the graph.
    edgelist = []
    for nodei, nodef in zip(nodelist[:-1],nodelist[1:]):
        if nodei and nodef:
            edgelist.append(nodei + 'x' + nodef)
    
    # Connect the contiguous edges from the data
    for i, edge in enumerate(edgelist[:-1]):
        if (edge, edgelist[i+1]) in LdG.edges:
            LdG.edges[edge, edgelist[i+1]]['weight'] += 1
        else:
            LdG.add_edge(edge, edgelist[i+1], weight=1)

    # Normalize the out-edge weights
    for node, degree in dict(LdG.out_degree()).items():
        
        sum_weights = np.sum([LdG.edges[edge[0], edge[1]]['weight'] for edge in LdG.out_edges(node)])
        
        for edge in LdG.out_edges(node):
            LdG.edges[edge[0], edge[1]]['weight'] /= sum_weights
            
    return LdG
    

