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

    def get_low_fret(self, capo=0):
        '''Return fret with the lowest value still greater than capo'''
        for fret in self.frets[::-1]:  # Assumes frets are sorted by string
            if fret[1] >= capo:
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


class Hand():
    ''' Seeks to manage valid placement of fingers via the following axioms:
    - Open notes are always allowed, as long as the string is not in use.
    - No finger may occupy a lower fret than any lower-numbered finger.
    - Fingers may share a fret, if the higher finger is on a higher string.
    - Finger 0 may barre all strings above its target at the same fret.
    '''
    def __init__(self, initial=None):
        self.capo = 0
        self.barre = False
        self.open_strings = []
        self.fingers = [Finger() for i in range(4)]
        if initial:
            self.move(initial)

    @property
    def index(self):
        return self.fingers[0].fret  # Fret location of index finger

    @property
    def shape(self):
        shape = [(s, 0) for s in self.open_strings]  # Add open notes right away
        for f in self.fingers:
            if f.down:
                shape.append((f.string, f.fret))
        # Add each higher string at index finger's fret
        if self.barre:
            for string in range(self.fingers[0].string + 1, 6):
                # Don't add string being played by other fingers
                if string not in [pos[0] for pos in shape]:
                    shape.append((string, self.index))
        return sorted(shape)

    def move(self, new):
        ''' Move hand to new shape: a list of tuples (string, fret)
        Return an integer representing the difficulty of the transition'''
        difficulty = 0
        new = set(new)
        done = set()
        # Open strings are free
        self.open_strings = [note[0] for note in new if note[1] == 0]
        [done.add((i, 0)) for i in self.open_strings]

        # Place the index (i) finger (and slide whole hand with it)
        i_fret = min(note[1] for note in new if note[1] > 0)
        i_pos = sorted(note for note in new if note[1] == i_fret)[0]
        try: slide = i_fret - self.index
        except TypeError: slide = i_fret  # This is probably wrong
        difficulty += self.fingers[0].move(i_pos)
        done.add(i_pos)

        # Other fingers get free movement for the initial slide.
        for f in self.fingers[1:]:
            try: f.move((f.string, f.fret + slide))
            except TypeError: continue

        # Barre the index finger if necessary/possible
        barred = [note for note in new-done if note[1] == i_fret]
        if barred:
            self.barre = True
            [done.add(note) for note in barred]

        # Place the other fingers, at cost
        def place_finger(finger, prev_fret):
            nonlocal difficulty
            try:
                fret = min(note[1] for note in new-done if note[1] >= prev_fret)
                pos = sorted(note for note in new-done if note[1] == fret)[0]
                difficulty += finger.move(pos)
                done.add(pos)
            except (ValueError, IndexError): return prev_fret
            return fret

        prev_fret = i_fret
        for f in self.fingers[1:]:
            prev_fret = place_finger(f, prev_fret)

        return difficulty


class Finger():
    def __init__(self, string=None, fret=None):
        if string in range(6) and type(fret) is int and fret > 0:
            self.position = (string, fret)
            self.down = True
        else:
            self.lift()

    @property
    def string(self):
        if self.down: return self.position[0]

    @property
    def fret(self):
        if self.down: return self.position[1]

    def lift(self):
        self.position = None
        self.down = False

    def move(self, new):
        ''' Move to position new, a tuple: (string, fret)
        Or None, to lift finger off fretboard entirely
        Return an integer difficulty for the move, for choosing best option '''
        if new[1] == 0:  # Lifing a finger is easy
            self.lift()
            return 0
        elif not self.down:  # Placing a lifted finger is easy too
            self.down = True
            self.position = new
            return 0
        else:  # Moving placed fingers is hard
            difficulty = sum(abs(a - b) for a, b in zip(new, self.position))
            self.position = new
            return difficulty


if __name__ == '__main__':

    pass
