import itertools as it

LOW_E = -8
MIDDLE_C = 0
STD_TUNING = [0, 5, 10, 15, 19, 24]  # Intervals of each string in EADGBE tuning
DROP_D_TUNING = [-2, 5, 10, 15, 19, 24]

LETTERS = 'CDEFGAB'
VALUES = (0, 2, 4, 5, 7, 9, 11)
VALUE, NAME = {}, {}
for l, v in zip(LETTERS, VALUES):
    VALUE[l] = v
    NAME[v] = l
    
#VALUE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
#NAME = {0: 'C', 2:'D', 4: 'E', 5: 'F', 7: 'G', 9: 'A', 11: 'B'}
ACCIDENTAL = {'b': -1, '#': 1}


class Note():
    def __init__(self, pitch):
        ''' Accepts string format: {letter}{#/b}{octave}, e.g. C4, E#2, Ab4
        and numerical format: middle C/C4 = 0, +/- 1 per half-step '''
        if type(pitch) is int:
            self.value = pitch
            self.name = self.get_name()

        elif type(pitch) is str:
            self.name = pitch
            self.value = self.get_value()
            # Correct case of note name string
            self.name[-2].lower()
            self.name[0].upper()

        self.frets = self.get_frets()
        
    
    def __repr__(self):
        return f"Note('{self.name}') - Value: {self.value}"
    
    
    def __add__(self, other):
        try:    
            return Note(self.value + other)  # adding ints, +1 per semitone
        except TypeError:
            return self  # adding anything else has no effect
    

    def __sub__(self, other):
        try:
            return Note(self.value - other)  # subtracting ints yields a Note, -1 per semitone
        except TypeError:
            return self.value - other.value  # subtracting Notes yields an interval value
        else:
            return self  # otherwise no effect
    
    
    def get_next_fret(self, capo):
        '''Return fret with the lowest value still greater than capo'''
        for fret in self.frets[::-1]:  # Assumes frets are sorted by string
            if fret[1] > capo:
                return fret            
    

    def get_name(self):
        ''' Convert integer value to note name.'''
        accidental = None
        try:
            letter = NAME[self.value % 12]            
        # All accidentals are considered sharp, unless explicitly defined as flat
        except KeyError:
            letter = NAME[(self.value % 12) - 1]
            accidental = '#'
        octave = (self.value // 12) + 4  # Default C4 (middle C) to value 0
        
        if accidental:
            return f'{letter}{accidental}{octave}'
        else:
            return f'{letter}{octave}'
    
    
    def get_value(self):
        ''' Convert note name to integer value.'''
        value = 0        
        try:
            value += (int(self.name[-1]) - 4) * 12  # Default C4 to value 0
            value += VALUE[self.name[0].upper()]
            if len(self.name) == 3:
                value += ACCIDENTAL[self.name[1].lower()]
        except KeyError:
            print("Invalid note: ", self.name)
            return None
        except ValueError:
            print("Invalid note: ", self.name)
            return None
        return value
    
    def get_frets(self, tuning=STD_TUNING):
        ''' Return list of tuples of possible string and fret combinations'''
        frets = []
        for string, value in enumerate(tuning):
            if self.value >= LOW_E + value:
                fret = self.value - LOW_E - value
                frets.append((string, fret))
        return frets


class Chord():
    def __init__(self, note_list):
        self.notes = []
        self.shapes = []
        
        for note in set(note_list):
            if isinstance(note, Note):
                self.notes.append(note)
            else:
                self.notes.append(Note(note))
        
        # Generate all possible fingering combinations
        for shape in it.product(*[note.frets for note in self.notes]):
            # Eliminate those that play two or more notes on one string
            if len({i[0] for i in shape}) == len([i[0] for i in shape]):
                self.shapes.append(sorted(shape))
#        self.shapes.sort()


    @ property
    def shape(self):
        # Need  to implement a way to pick the best option from self.shapes
#        return self.shapes[0]
        sums = self.span_sum()
        lowest = min(sums.keys())
        return sums[lowest][0]


    def fret_sum(self):
        '''Sum the absolute fret values of each note in each shape
        Return a dict of total fret values mapped to lists of shapes'''
        result = {}
        for shape in self.shapes:
            total = sum(i[1] for i in shape)
            try:
                result[total].append(shape)
            except KeyError:
                result[total] = [shape]
        return result
    
    
    def span_sum(self):
        '''Sum the difference of each fret and the lowest fret in a shape
        Return a dict of total span mapped to lists of shapes'''
        result = {}
        for shape in self.shapes:
            capo =  min(i[1] for i in shape)
            total = sum(i[1] - capo for i in shape)
            try:
                result[total].append(shape)
            except KeyError:
                result[total] = [shape]
        return result


if __name__ == '__main__':
    
    # Tests for Note() methods
    e = Note(-8)
    assert e.name == 'E3'
    assert e.value == -8
    assert e.frets == [(0,0)]
    
    e2 = Note('E3')
    assert e2.value == -8
    assert e2.name == 'E3'
    assert e2.frets == [(0,0)]
    
#    # Test some basic open chords
    open_e_notes = [-8, -1, 4, 8, 11, 16]
    open_e_shape = [(0,0), (1,2), (2,2), (3,1), (4,0), (5,0)]
    open_e = Chord(open_e_notes)
    
    open_a_notes = [-8, -3, 4, 9, 13, 16]
    open_a_shape = [(0,0), (1,0), (2,2), (3,2), (4,2), (5,0)]
    open_a = Chord(open_a_notes)
    
    open_d_notes = [-3, 2, 9, 14, 18]
    open_d_shape = [(1,0), (2,0), (3,2), (4,3), (5,2)]
    open_d = Chord(open_d_notes)
    
    open_g_notes = [-5, -1, 2, 7, 11, 19]
    open_g_shape = [(0, 3), (1,2), (2,0), (3,0), (4,0), (5,3)]
    open_g = Chord(open_g_notes)
    
    open_c_notes = [0, 4, 7, 12, 16]
    open_c_shape = [(1,3), (2,2), (3,0), (4,1), (5,0)]
    open_c = Chord(open_c_notes)
    
    assert open_e.shape == open_e_shape
    assert open_a.shape == open_a_shape
    assert open_d.shape == open_d_shape
    assert open_g.shape == open_g_shape
    assert open_c.shape == open_c_shape
