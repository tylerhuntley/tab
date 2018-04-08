import itertools as it
import unittest

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


class Pitch():
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
            return self.__class__(self.value + other)  # adding ints, +1 per semitone
        except TypeError:
            return self  # adding anything else has no effect
    

    def __sub__(self, other):
        try:
            return self.__class__(self.value - other)  # subtracting ints, -1 per semitone
        except TypeError:
            return self.value - other.value  # subtraction yields an interval value
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


class Note(Pitch):
    durations = {'W': 1, 'H': 1/2, 'Q': 1/4, 'E': 1/8, 'S': 1/16, 'T': 1/32}
    def __init__(self, *args, t='Q', **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = self.durations[t]  # Default to quarter notes

    def set_duration(self, t):
        try:
            self.duration = self.durations[t]
        except IndexError:
            print("Invalid duration: {W|H|Q|E|S|T}. Default to quarter note ('Q')")
            self.duration = 1/4


class Chord():
    def __init__(self, note_list):
        self.notes = []
        self.shapes = []
        
        # Add notes to list, constructing them first if needed
        for note in set(note_list):
            if isinstance(note, Note):
                self.notes.append(note)
            else:
                self.notes.append(Note(note))

        # Store shortest note duration as own
        self.duration = min(note.duration for note in self.notes)
        
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


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.e1 = Note(-8)
        self.e2 = Note('E3')

    def test_names(self):
        self.assertEqual(self.e1.name, 'E3')
        self.assertEqual(self.e2.name, 'E3')

    def test_values(self):
        self.assertEqual(self.e1.value, -8)
        self.assertEqual(self.e2.value, -8)

    def test_frets(self):
        self.assertEqual(self.e1.frets, [(0, 0)])
        self.assertEqual(self.e2.frets, [(0, 0)])


class TestOpenChords(unittest.TestCase):
    def setUp(self):
        self.e = Chord([-8, -1, 4, 8, 11, 16])
        self.a = Chord([-8, -3, 4, 9, 13, 16])
        self.d = Chord([-3, 2, 9, 14, 18])
        self.g = Chord([-5, -1, 2, 7, 11, 19])
        self.c = Chord([0, 4, 7, 12, 16])
        self.chords = [self.e, self.a, self.d, self.g, self.c]

        self.e_shape = [(0,0), (1,2), (2,2), (3,1), (4,0), (5,0)]
        self.a_shape = [(0,0), (1,0), (2,2), (3,2), (4,2), (5,0)]
        self.d_shape = [(1,0), (2,0), (3,2), (4,3), (5,2)]
        self.g_shape = [(0, 3), (1,2), (2,0), (3,0), (4,0), (5,3)]
        self.c_shape = [(1,3), (2,2), (3,0), (4,1), (5,0)]
        self.shapes = [self.e_shape, self.a_shape, self.d_shape,
                       self.g_shape, self.c_shape]

    def test_shapes(self):
        for chord, shape in zip(self.chords, self.shapes):
            with self.subTest(i=chord):
                self.assertEqual(chord.shape, shape)


if __name__ == '__main__':
    
    unittest.main()
