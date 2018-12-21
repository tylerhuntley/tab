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


    def add_notes(self, notes, duration):
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


class Staff():
    '''Manages concatenation of bars into a singular staffline'''
    def __init__(self, bar=None):
        self.lines = []
        self.bars = []
        if bar:
            self.add_bar(bar)


    def __repr__(self):
        temp = [line.replace(' ', '-') for line in self.lines]
        return '\n'.join(temp)+'\n'


    def add_bar(self, bar):
        self.bars.append(bar)  # Keep a running list of Bar() objects
        for i, line in enumerate(bar.lines):
            try:
                self.lines[i] += line[1:]  # Avoid duplicating '|' symbols
            except IndexError:
                self.lines.append(line)                          


class Tab():
    '''Directs staff concatenation, manages line length/page display'''
    def __init__(self):
        self.staffs = []


    def __repr__(self):
        return '\n'.join(str(staff) for staff in self.staffs)+'\n'


    def add_bar(self, bar):
        '''Add bar to last staff, wrap to new staff if past MAX_LENGTH'''
        if self.staffs == [] or (len(self.staffs[-1].lines[0]) >= MAX_WIDTH):
            self.staffs.append(Staff())
        self.staffs[-1].add_bar(bar)


if __name__ == '__main__':
    pass
