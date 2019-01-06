'''
This file concerns transcription of particular arrangements of musical notes
into the tablature format commonly used in the guitar community.

64 chars/bar:
|----------------------------------------------------------------|
32 chars/bar:
|--------------------------------|--------------------------------|
16 chars/bar:
|----------------|----------------|----------------|----------------|
8 chars/bar:
|--------|--------|--------|--------|--------|--------|--------|--------|
'''

MIN_WIDTH = 8  # Minimum size for sparse or empty bars
MAX_WIDTH = 67  # 64 chars (2 * 32 chars/bar) + 3 barlines


class Bar():
    '''Manages construction of a single tab measure, and placement of
    numerical note symbols on the appropriate lines'''
    def __init__(self, notes=None, width=MIN_WIDTH):
        ''' notes is a list of tuples: [(values, duration),...], where
        values is a tuple of integer fret values, or None for a rest
        duration is a float, 1 being a whole note, 0.25 a quarter, etc.
        width is an integer, ideally a power of 2 (maybe mandatory)'''
        if notes is None: self.notes = []
        else: self.notes = notes
        self.width = width

    def __repr__(self):
        # Shortest note will get 4 spaces (#s and '-'s) to avoid crowding
        try: temp = int(4 / min([t for _, t in self.notes]))
        except ValueError: temp = 0
        width = max(self.width, temp)
        lines = ['|']*6
        total = 0
        for shape, duration in self.notes:
            chord = shape.list_frets()
            # Ignore notes beyond one full bar
            if total >= 1:
                break
            total += duration
            length = duration * width
            for string, fret in enumerate(chord):
                if fret is None: fret = '-'
                padding = int(length - len(str(fret)))
                # Reverse string order, add a #, and pad with '-' to length
                lines[5-string] += str(fret) + '-' * padding
        # Pad to width if not full
        for i in range(len(lines)):
            lines[i] += '-' * int(width + 1 - len(lines[i]))
        # Trim to width if overfull
        temp = [line[:width+1]+'|' for line in lines]
        return '\n'.join(temp)+'\n'

    def __eq__(self, other):
        return str(self) == str(other)

    def __len__(self):
        return len(self.lines[0])

    @property
    def lines(self):
        return str(self).split('\n')[:-1]  # Ignore trailing '\n'

    def clear(self):
        self.notes = []

    def is_full(self):
        ''' Bar is full once it has at least 1 bar's worth of note duration '''
        return round(sum(t for _, t in self.notes), 3) >= 1

    def time_left(self):
        ''' A float fraction of whole notes to add until the bar is full'''
        return 1 - sum(t for _, t in self.notes)

    def add_shape(self, shape, duration):
        ''' shape should be a Shape object
        It may be a fret-list e.g. open D would be [None, 0, 0, 2, 3, 2]
        Duration is a float, where 1.0 is a whole note, 0.25 a quarter, etc.'''
        if isinstance(shape, Shape):
            self.notes.append((shape, duration))
        else:
            self.notes.append((Shape(shape), duration))


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
            for i, line in enumerate(str(bar).split('\n')):
                try:
                    # line[1:] prevents duplicating vertical barlines
                    lines[i] += line[1:].replace(' ', '-')
                except IndexError:
                    lines.append(line.replace(' ', '-'))
        return '\n'.join(lines)

    def add_bar(self, bar):
        self.bars.append(bar)


class Arrangement():
    ''' An Arrangement is similar to a Song, but consists of specific
    fingering patterns, with durations, for transcription to tablature
    by managing staff concatenation and line length/page display'''
    def __init__(self, notes=None, width=MIN_WIDTH):
        self.width = width
        self.last_bar = Bar(width=self.width)
        self.bars = [self.last_bar]
        self.staffs = [Staff(self.last_bar)]
        self.notes = []
        if notes is not None:
            for note in notes:
                self.add_shape(*note)

    def __repr__(self):
        return '\n'.join(str(staff) for staff in self.staffs)+'\n'

    def __eq__(self, other):
        return str(self) == str(other)

    def add_bar(self, bar):
        '''Add bar to last staff, wrap to new staff if past MAX_WIDTH '''
        if len(self.staffs[-1]) >= MAX_WIDTH:
            self.staffs.append(Staff())
        self.staffs[-1].add_bar(bar)

    def add_shape(self, shape, duration):
        ''' shape is a Shape object, duration is a float, e.g. 1, 0.25, 1/8'''
        # Start a new bar if last one is already full
        if self.last_bar.is_full():
            self.last_bar = Bar(width=self.width)
            self.add_bar(self.last_bar)
        diff = duration - self.last_bar.time_left()
        self.last_bar.add_shape(shape, duration)
        # Add remaining duration to a new bar if note is too long
        if diff > 0:
            self.last_bar = Bar(width=self.width)
            self.last_bar.add_shape(Shape(), diff)
            self.add_bar(self.last_bar)
        self.notes.append((shape, duration))

    def add_run(self, shapes, duration):
        for shape in shapes:
            self.add_shape(shape, duration)


class Shape():
    ''' Intended to simplify communication of fretboard coordinates'''
    def __init__(self, shape=None):
        '''Converts and stores shape as a fret-list by default'''
        self.shape = [None] * 6
        if shape is None: return
        elif isinstance(shape, Shape):
            self.shape = shape.shape
        elif all((type(i) is int or i is None for i in shape)):
            # Fret-list, e.g. open D: [None, 0, 0, 2, 3, 2]
            if len(shape) == 6:
                self.shape = list(shape)
            # Single tuple: (string, fret)
            elif len(shape) == 2 and not any((i is None for i in shape)):
                self.shape = [None]*6
                self.shape[shape[0]] = shape[1]
        # List of tuples: [(string, fret), ...]
        elif type(shape) is list and all((type(i) is tuple for i in shape)):
            self.shape = [None]*6
            for string, fret in shape:
                self.shape[string] = fret

    def __repr__(self):
        return str(self.shape)

    def __eq__(self, other):
        try:
            return self.shape == other.shape
        except AttributeError:
            return self.shape == Shape(other).shape
        return False

    def __len__(self):
        return len([i for i in self.shape if i is not None])

    def __add__(self, other):
        ''' Combine two shapes, using the higher value for each string '''
        temp = []
        for a, b in zip(self.shape, other.shape):
            if a is None and b is None:
                temp.append(None)
            elif a is None:
                temp.append(b)
            elif b is None:
                temp.append(a)
            else:
                temp.append(max(a, b))
        return Shape(temp)

    @property
    def span(self):
        ''' Returns integer distance between highest/lowest non-open frets'''
        temp = [i[1] for i in self.list_tuples() if i[1] > 0]
        try: return max(temp) - min(temp)
        except ValueError: return 0

    def list_frets(self):
        ''' Returns a fret-list, e.g. [None, 0, 0, 2, 3, 2]'''
        return self.shape

    def list_tuples(self):
        ''' Returns a list of tuples: [(string, fret), ...]'''
        return [(s, f) for s, f in enumerate(self.shape) if f is not None]


if __name__ == '__main__':

    pass
