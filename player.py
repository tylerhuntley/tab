'''
This file concerns the selection of concrete, playable fretboard patterns from
abstract collections of musical notes.
'''

import itertools as it
import tab, music


class Hand():
    ''' Seeks to manage valid placement of Fingers via the following axioms:
    - Open notes are always allowed, as long as the string is not in use.
    - No finger may occupy a lower fret than any lower-numbered finger.
    - Fingers may share a fret, if the higher finger is on a higher string.
    - Finger 0 may barre all strings above its target at the same fret. '''
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
        ''' Outputs a tab-compatible list of tuples: [(string, fret)]
        describing the locations of its Fingers in a given fingering shape'''
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
        return music.Shape(shape)

    @property
    def strain(self):
        ''' Strain represents the inherent difficulty of a given shape.
        Strain increases by 1 for every unit a finger strays from "home"
        Frets' home is x, x+1, x+2, and x+3 by finger, with index at x
        Strings' home is either string adjacent to the previous finger's
        Barres add 1 per extra string fretted, regardless of distance
        Frets above 12 add 1 extra strain per fret per finger '''
        strain = 0
        # Shape strain
        for a, b in zip(self.fingers[:-1], self.fingers[1:]):
            try:
                strain += abs(b.fret - (a.fret+1))
                strain += max((abs(b.string - a.string) - 1), 0)
            except TypeError: continue
        # Barre strain
        tuples = self.shape.list_tuples()
        if self.barre:
            strain += len([n for n in tuples if n[1] == self.index]) - 1
        # High note strain
        for f in self.fingers:
            if f.down and f.fret > 12:
                strain += f.fret - 12
        return strain

    def move(self, shape):
        ''' Move to a new position represented by a Shape object, shape
        Return an integer representing the difficulty of the transition'''
        difficulty = 0
        if isinstance(shape, music.Shape):
            new = set(shape.list_tuples())
        else:
            new = set(shape)
        done = set()

        # Open strings are free
        self.open_strings = [note[0] for note in new if note[1] == 0]
        [done.add((i, 0)) for i in self.open_strings]
        if done == new: return difficulty

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
        # Don't barre if open notes are needed above index finger
        blocked = [n for n in done if n[1] < i_fret and n[0] > i_pos[0]]
        if barred and not blocked:
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
    ''' A Finger is controlled by a Hand, but handles simpler fretboard
    maneuvers on its own, calculating relative difficulty of movement '''
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


class Guitarist():
    ''' The Guitarist is responsible for reading a Song, and producing
    an Arrangement by guiding a Hand along the easiest route through
    the possible shapes of the musical objects it contains. '''
    def __init__(self, song=None):
        self.arr = tab.Arrangement()
        if song:
            self.song = song
            self.path = self.read(song)
            try:
                durations = (n.duration for n in self.song.notes)
                temp = [(a,b) for a,b in zip(self.path, durations)]
            except TypeError:
                temp = None
            self.arr = tab.Arrangement(notes=temp)

    def read(self, song, DELTA=3):
        ''' This gradually pieces a song together via play(),
        to mitigate exponential complexity.'''
        path = []
        # Play first three notes, and select best starting shape
        passage = music.Song(song.notes[:DELTA])
        shape = self.play(passage)
        path.append(shape[0])
        # Repeat in three-note sections, building off previous results
        for i in range(1, len(song)-DELTA):
            passage = music.Song([path[-1], *song.notes[i:i+DELTA+1]])
            shape = self.play(passage)
            try: path.append(shape[0])
            except TypeError: continue  # Ignore notes out of range
        # Add final notes
        for i in shape[1:]:
            path.append(i)
        return path

    def play(self, song):
        ''' This is a shortest path algorithm, using possible shapes as
        path nodes, and a combination of Hand.strain and Hand.move
        difficulty as its path lengths. '''
        if len(song.notes) == 1:
            return [song.notes[0].shape]
        best_score = None
        best_path = None
        paths = [note.shapes for note in song.notes]
        for path in it.product(*paths):
            score = 0
            h = Hand()
            for shape in path:
                score += h.move(shape)
                score += h.strain
            try:
                if score < best_score:
                    best_score = score
                    best_path = path
            except TypeError:
                best_score = score
                best_path = path
        return best_path


if __name__ == '__main__':

    pass
