from notes import Note, Chord, Shape

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
        ''' Bar is full one it has at least 1 bar's worth of note duration '''
        return round(sum(t for _, t in self.notes), 3) >= 1

    def time_left(self):
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
    def __init__(self, width=MIN_WIDTH):
        self.width = width
        self.last_bar = Bar(width=self.width)
        self.bars = [self.last_bar]
        self.staffs = [Staff(self.last_bar)]
        self.notes = []

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


class Song():
    ''' A Song is an ordered list of Note/Chord objects with their
    respective durations, played in order to produce music '''
    def __init__(self):
        self.notes= []

    def add(self, obj):
        if isinstance(obj, (Note, Chord)):
            self.notes.append(obj)
        else:
            try: self.notes.append(Note(obj))
            except (TypeError, AttributeError): pass


class Guitarist():
    ''' The Guitarist is responsible for reading a Song, and producing
    an Arrangement by guiding a Hand along the easiest route through
    the possible shapes of the musical objects it contains. '''
    def __init__(self, song=None):
        if song:
            self.play(song)

    def play(self, song):
        ''' This is a shortest path algorithm, using possible shapes as
        path nodes, and a combination of Hand.strain and Hand.move
        difficulty as its path lengths. Particular algorithm TBD. '''
        pass


if __name__ == '__main__':
    pass
