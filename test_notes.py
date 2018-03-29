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
            return Note(self.value - other)  # subtracting ints, -1 per semitone
        except TypeError:
            return self  # subtracting anything else has no effect
        

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


def name_to_num(note):
    """ Convert standard note name into a linear numeric value """
    value = 0
    name = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    accidental = {'b': -1, '#': 1}
    
    try:
        value += int(note[-1]) * 12
        value += name[note[0]]
        if len(note) == 3:
            value += accidental[note[1]]
    except KeyError:
        print("Invalid note: ", note)
        return None
    except ValueError:
        print("Invalid note: ", note)
        return None
    return value


def chord_to_num(chord):
    """ Input list of standard note names 
    Returns list of numerical note values"""
    nums = []
    for note in chord:
        num = name_to_num(note)
        if not num is None:
            nums.append(num)
    return nums


def num_to_fret(number, tuning=STD_TUNING):
    """ Convert numerical note value to list of all fretting options
    Returns list of tuples: (string, fret) """
    options = []
    if not type(number) is int:
        return options
    for string, value in enumerate(tuning):
        if number >= LOW_E + value:
            fret = number - (LOW_E + value)
            options.append((string, fret))
    return options


def chord_shape(values):
    """ Input list of numerical note values
    Returns list of tuples: (string, fret) 
    Should attempt to maximize playability"""
    
    # Can't play more than six notes at once
    if len(values) > 6:
        return None  # Or should it cull randomly to six?

    def use_string(string):
        ''' Eliminate all note options on a given string.'''
        for k, v in options.items():
            if v[0] == string:
                options[k].remove(v)
    
    notes = [Note(value) for value in values]
    shape = {}
    options = {}
    used_strings = set()
    lowest_fret = min(fret[1] for note in notes for fret in note.frets)
    
    for note in notes:
        options[note] = note.frets
        # Add any notes playable at lowest_fret to shape
        for fret in note.frets:
            if fret[1] == lowest_fret and not fret[0] in used_strings:
                shape[note] = fret
                # Remove other options for that note, and all other notes on that string
                del options[note]
                use_string(fret[0])
    
    while len(shape) < len(notes):
        for note, frets in options.copy().items():
            for fret in frets:
                # Prefer lower frets if possible
                if note in shape:
                    if fret[1] < shape[note][1]:
                        shape[note] = fret
                        use_string(fret[0])
                        del options[note]
                        break
                else:
                    shape[note] = fret
                    use_string(fret[0])
                    
            
    print(sorted(list(shape.values())))
    return sorted(list(shape.values()))


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
    
#    # Tests for future chord_shape()
#    # Test the low F, the only note with a single valid fingering option
#    assert chord_shape([-7]) == (0, 1)
#    
#    # Test a basic open E chord
    open_e_notes = [-8, -1, 4, 8, 11, 16]
    open_e_frets = [(0,0), (1,2), (2,2), (3,1), (4,0), (5,0)]
    assert chord_shape(open_e_notes) == open_e_frets
    
    
    