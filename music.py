'''
This file concerns musical information in an abstract sense, as well as the
relationships between individual notes and the layout of a standard guitar.
'''

import itertools as it
from tab import Shape

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
ACCIDENTAL = {'b': -1, '#': 1}

MAX_FRET = 18
MAX_SPAN = 5


class Pitch():
    ''' A Pitch represents a particular musical tone. It contains
    information about their relationships to one another, as well as
    naming conventions and potential fretboard locations. '''
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

        self.shapes = self.get_shapes()

    def __repr__(self):
        return f"Note('{self.name}') - Value: {self.value}"

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value

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

    def __lt__(self, other):  # For sorting purposes
        return self.value < other.value

    def get_low_fret(self, capo=0):
        '''Return shape with the lowest fret value still greater than capo'''
        for shape in self.shapes[::-1]:  # Assumes shapes are sorted by string
            if shape.list_tuples()[0][1] >= capo:
                return shape

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

    def get_shapes(self, tuning=STD_TUNING):
        ''' Return a list of potential Shape objects for this Pitch '''
        shapes = []
        for string, value in enumerate(tuning):
            if self.value >= LOW_E + value:
                fret = self.value - LOW_E - value
                if fret <= MAX_FRET:  # Don't pass the end of the fretboard
                    shapes.append(Shape((string, fret)))
        return shapes


class Note(Pitch):
    ''' A Note is a Pitch plus an appropriate time duration value '''
    def __init__(self, pitch, duration=1/4):
        ''' Accepts one Pitch value parameter, and one optional duration '''
        super().__init__(pitch)
        self.duration = duration  # Default to quarter notes

    def __eq__(self, other):
        return self.value == other.value and self.duration == other.duration

    def __hash__(self):
        return self.value


class Chord():
    ''' A Chord is a set of concurrent Notes. Its duration is equal to that
    of its shortest note, since tab sacrifices timing info for readability '''
    def __init__(self, note_list, duration=1/4):
        ''' note_list is a list of Note objects or Note constructor arguments,
        with duration applied to each constructed Note'''
        self.notes = []
        self.shapes = []

        # Add notes to list, constructing them first if needed
        for note in set(note_list):
            if isinstance(note, Note):
                self.notes.append(note)
            else:
                self.notes.append(Note(note, duration))
        self.notes.sort()

        # Store shortest note duration as own
        self.duration = min(note.duration for note in self.notes)

        # Generate all possible fingering combinations
        for shapes in it.product(*[note.shapes for note in self.notes]):
            shape = Shape()
            for i in shapes:
                shape += i
            # Shape must hit every note, and not stretch too far
            if len(shape) == len(self.notes) and shape.span <= MAX_SPAN:
                self.shapes.append(shape)

    def __repr__(self):
        return str([note.name for note in sorted(self.notes)])

    def  __eq__(self, other):
        return self.notes == other.notes

    def __hash__(self):
        return tuple(self.notes)

    @ property
    def shape(self):
        ''' Minimizes Hand.strain to return the easiest shape of this chord'''
        from player import Hand  # Circular dependency
        best = None
        for shape in self.shapes:
            h = Hand(shape)
            try:
                if h.strain < best.strain:
                    best = h
            except AttributeError: best = h
        return best.shape


class Song():
    ''' A Song is an ordered list of Note/Chord objects with their
    respective durations, played in order to produce music '''
    def __init__(self, notes=None):
        self.notes = []
        if notes is not None:
            for note in notes:
                self.add(note)

    def __len__(self):
        return len(self.notes)

    def add(self, obj):
        if isinstance(obj, Note):
            self.notes.append(Chord([obj]))
        elif isinstance(obj, Chord):
            self.notes.append(obj)
        else:
            try: self.notes.append(Chord([Note(obj)]))
            except (TypeError, AttributeError): pass


if __name__ == '__main__':

    pass
