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
MAX_WIDTH = 67  # 64 chars (2 * 32 chars) + 3 bars

class Bar():
    '''Manages construction of a single tab measure, and placement of
    numerical note symbols on the appropriate lines'''
    def __init__(self):
        self.lines = [f'|{"-" * CHARS_PER_BAR}|']*6    
    
    
    def add_note(self, note):
        '''Receives a tuple: (string, fret)
        Modifies self.lines in place and returns nothing'''
        # Must also account for duration somehow, so next note doesn't follow 
        # too close, and starting time, so this one isn't placed too far up
        

    def display(self):    
        for line in self.lines:
            print(line)
            
    
class Staff():
    '''Manages concatenation of bars into a singular staffline'''
    def __init__(self, bar=None):
        self.lines = []
        self.bars = []
        if bar:
            self.bars.append(bar)
            for bar in self.bars:
                self.add_bar(bar)
        else:
            self.bars = []
    
    
    def add_bar(self, bar):
        self.bars.append(bar)
        
        for i, line in enumerate(bar.lines):
            try:
                self.lines[i] += line[1:]  # Avoid duplicating '|' symbols
            except IndexError:
                self.lines.append(line)
                
            
    def display(self):
        for line in self.lines:
            print(line)            
            
            
if __name__ == '__main__':
    bar = Bar()
    staff = Staff()
    for i in range(4):
        print(f'Staff bars: {i}')
        staff.display()
        staff.add_bar(bar)
        print()        
