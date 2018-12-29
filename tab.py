'''
64 chars/bar:
|----------------------------------------------------------------|
|----------------------------------------------------------------|
|----------------------------------------------------------------|
32 chars/bar:
|--------------------------------|--------------------------------|
|--------------------------------|--------------------------------|
|--------------------------------|--------------------------------|
16 chars/bar:
|----------------|----------------|----------------|----------------|
|----------------|----------------|----------------|----------------|
|----------------|----------------|----------------|----------------|
'''

CHARS_PER_BAR = 32  # Probably want this to be dynamic
MAX_WIDTH = 67  # 64 chars (2 * 32 chars) + 3 barlines

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
    def __init__(self):
        self.lines = [f'|{" " * CHARS_PER_BAR}|']*6

    def __repr__(self):
        return '\n'.join(self.lines)+'\n'

    def __eq__(self, other):
        return str(self) == str(other)

    def clear(self):
        self.lines = [f'|{" " * CHARS_PER_BAR}|']*6

    def is_full(self):
        ''' Bar is full once every ' ' has been replaced by a # or a '-' '''
        for c in str(self):
            if c == ' ':
                return False
        return True

    def add_chord(self, notes, duration):
        '''Receives a list of tuples: (string, fret)
        Duration should be that of the shortest note in the list
        Modifies self.lines in place and returns nothing'''

        # Add placeholder notes to fill up empty lines
        for i in range(6):
            if i not in [note[0] for note in notes]:
                notes.append((i, ''))

        for note in notes:
            n = 5 - note[0]  # String and line numbers are inverse
            line = ''

            # Copy line verbatim upto first space
            for c in self.lines[n]:
                if c == ' ':
                    break
                line += c
            else:  # No spaces, bar is full
                break

            # Add note number and fill with dashes for its duration
            line += str(note[1])
            spacing = int(CHARS_PER_BAR * duration) - len(str(note[1]))
            for i in range(spacing):
                if len(line) < len(self.lines[n]) -1:  # Don't overfill
                    line += '-'

            # Refill the rest with spaces and end with a bar
            while len(line) < len(self.lines[n]) - 1:
                line += ' '
            line += '|'

            self.lines[n] = line

    def add_note(self, note, duration):
        ''' Wrapper for add_chord() to pass single notes as a chord/list'''
        self.add_chord([note], duration)

    def add_run(self, notes, duration):
        ''' Adds notes sequentially with equal duration, as in a scale run'''
        for note in notes:
            self.add_note(note, duration)


class Staff():
    '''Manages concatenation of bars into a singular staffline'''
    def __init__(self, bar=None):
        self.lines = []
        self.bars = []
        if bar:
            self.add_bar(bar)

    def __len__(self):
        length = sum(len(bar.lines[0]) for bar in self.bars)
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

    def add_chord(self, chord, duration):
        if self.last_bar.is_full():
            self.last_bar = Bar()
            self.add_bar(self.last_bar)
        self.last_bar.add_chord(chord, duration)

    def add_note(self, note, duration):
        self.add_chord([note], duration)

    def add_run(self, notes, duration):
        for note in notes:
            self.add_note(note, duration)


if __name__ == '__main__':
    pass
