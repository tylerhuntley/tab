from notes import Note, Chord

'''
64 chars/bar:
|----------------------------------------------------------------|
32 chars/bar:
|--------------------------------|--------------------------------|
16 chars/bar:
|----------------|----------------|----------------|----------------|
8 chars/bar:
|--------|--------|--------|--------|--------|--------|--------|--------|
'''

CHARS_PER_BAR = 32  # Probably want this to be dynamic
MIN_WIDTH = 8  # Minimum size for sparse or empty bars
MAX_WIDTH = 67  # 64 chars (2 * 32 chars/bar) + 3 barlines

# Note duration values
W = 1
H = 1/2
Q = 1/4
E = 1/8
S = 1/16
T = 1/32


class Bar():
    '''Manages construction of a single tab measure, and placement of
    numerical note symbols on the appropriate lines'''
    def __init__(self, width=CHARS_PER_BAR, notes=None):
        ''' notes must be a list of tuples: [(note, duration),]
        width is an integer, ideally a power of 2 (maybe mandatory)'''
        if notes:
            # Shortest note will get 4 spaces (#s and '-'s) to avoid crowding
            temp = int(4 / min(note[1] for note in notes))
            self.width = max(MIN_WIDTH, temp)  # 4/bar looks dumb
        else:
            self.width = width
        self.lines = [f'|{" " * self.width}|']*6

#        self.add_all(notes)  #TODO, pre-add notes

    def __repr__(self):
        return '\n'.join(self.lines)+'\n'

    def __eq__(self, other):
        return str(self) == str(other)

    def __len__(self):
        # All lines should have the same length as the first, right?
        return len(self.lines[0])

    def clear(self):
        self.lines = [f'|{" " * self.width}|']*6

    def is_full(self):
        ''' Bar is full once every ' ' has been replaced by a # or a '-' '''
        for c in str(self):
            if c == ' ':
                return False
        return True

    def add_frets(self, frets, duration):
        '''Receives a list of tuples: (string, fret)
        Duration should be that of the shortest note in the list
        Modifies self.lines in place and returns nothing'''

        # Add placeholder notes to fill up empty lines
        for i in range(6):
            if i not in [fret[0] for fret in frets]:
                frets.append((i, ''))

        for fret in frets:
            n = 5 - fret[0]  # String and line numbers are inverse
            line = ''

            # Copy line verbatim upto first space
            for c in self.lines[n]:
                if c == ' ':
                    break
                line += c
            else:  # No spaces, bar is full
                break

            # Add fret number and fill with dashes for its duration
            line += str(fret[1])
            spacing = int(self.width * duration) - len(str(fret[1]))
            for i in range(spacing):
                if len(line) < len(self.lines[n]) -1:  # Don't overfill
                    line += '-'

            # Refill the rest with spaces and end with a bar
            while len(line) < len(self.lines[n]) - 1:
                line += ' '
            line += '|'

            self.lines[n] = line

    def add_fret(self, fret, duration):
        ''' Wrapper for add_frets() to pass single frets as a chord/list'''
        self.add_frets([fret], duration)

    def add_run(self, notes, duration):
        ''' Adds notes sequentially with equal duration, as in a scale run'''
        for note in notes:
            self.add_fret(note, duration)

    def add(self, obj):
        ''' Adds Note() objects to the bar for their duration '''
        # Notes assume get_low_fret() is always best. Need to revisit that.
        if isinstance(obj, Note):
            self.add_fret(obj.get_low_fret(), obj.duration)
        # Chords rely on inbuilt shape property. Need to revisit that too.
        elif isinstance(obj, Chord):
            frets = [note.get_low_fret() for note in obj.notes]
            self.add_frets(frets, obj.duration)


class Staff():
    '''Manages concatenation of bars into a singular staffline'''
    def __init__(self, bar=None):
        self.lines = []
        self.bars = []
        if bar:
            self.add_bar(bar)

    def __len__(self):
        length = sum(len(bar) for bar in self.bars)
        length -= len(self.bars[1:])
        return length

    def __repr__(self):
        lines = []
        for bar in self.bars:
            for i, line in enumerate(bar.lines):
                try:
                    # line[1:] prevents duplicating vertical barlines
                    lines[i] += line[1:].replace(' ', '-')
                except IndexError:
                    lines.append(line.replace(' ', '-'))
        return '\n'.join(lines)+'\n'

    def add_bar(self, bar):
        self.bars.append(bar)


class Tab():
    '''Directs staff concatenation, manages line length/page display'''
    def __init__(self):
        self.last_bar = Bar()
        self.bars = [self.last_bar]
        self.staffs = [Staff(self.last_bar)]

    def __repr__(self):
        return '\n'.join(str(staff) for staff in self.staffs)+'\n'

    def add_bar(self, bar):
        '''Add bar to last staff, wrap to new staff if past MAX_WIDTH '''
        if len(self.staffs[-1]) >= MAX_WIDTH:
            self.staffs.append(Staff())
        self.staffs[-1].add_bar(bar)

    def add_frets(self, frets, duration):
        if self.last_bar.is_full():
            self.last_bar = Bar()
            self.add_bar(self.last_bar)
        self.last_bar.add_frets(frets, duration)

    def add_fret(self, fret, duration):
        self.add_frets([fret], duration)

    def add_run(self, frets, duration):
        for fret in frets:
            self.add_fret(fret, duration)


if __name__ == '__main__':
    pass
