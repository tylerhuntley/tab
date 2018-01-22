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
            self.name = self.get_name(self.value)

        elif type(pitch) is str:
            self.name = pitch
            self.value = self.get_value(self.name.upper())

        self.frets = self.get_frets()
        

    def get_name(self, value):
        ''' Convert integer value to note name.'''
        accidental = None
        try:
            letter = NAME[value % 12]
        except KeyError:
            letter = NAME[(value % 12) - 1]
            accidental = '#'
        octave = (value // 12) + 4  # Default C4 (middle C) to value 0
        
        if accidental:
            return f'{letter}{accidental}{octave}'
        else:
            return f'{letter}{octave}'
    
    
    def get_value(self, note):
        ''' Convert note name to integer value.'''
        value = 0        
        try:
            value += (int(note[-1]) - 4) * 12  # Default C4 to value 0
            value += VALUE[note[0]]
            if len(note) == 3:
                value += ACCIDENTAL[note[1]]
        except KeyError:
            print("Invalid note: ", note)
            return None
        except ValueError:
            print("Invalid note: ", note)
            return None
        return value
    
    def get_frets(self, tuning=STD_TUNING):
        ''' Return list of tuples of possible string and fret combinations'''
        frets = []
        for string, value in enumerate(tuning):
            if self.value >= LOW_E + value:
                fret = self.value - LOW_E + value
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


def chord_fingering(chord):
    """ Input list of numerical note values
    Returns list of tuples: (string, fret) """
    
    
    