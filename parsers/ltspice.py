#Python Library to parse ltspice's .asc schematic files.

def warn(msg):
    print("[WARN]LTSpice:", msg)

class Version:
    def parse(self, attributes, lines):
        self.version = int(attributes[0])
    def save(self):
        return [' '.join(['Version', str(self.version)])]
        
class Sheet:
    def parse(self, attributes, lines):
        self.attributes = attributes
    def save(self):
        return [' '.join(['SHEET', str(self.attributes)])]

class Wire:
    def parse(self, attributes, lines):
        self.x1 = int(attributes[0])
        self.y1 = int(attributes[1])
        self.x2 = int(attributes[2])
        self.y2 = int(attributes[3])
    def save(self):
        return [' '.join('WIRE', str(self.x1), str(self.y1), str(self.x2), int(self.y2))]

class Flag:
    def parse(self, attributes, lines):
        self.x = int(attributes[0])
        self.y = int(attributes[1])
        self.basename = attributes[2]
        self.angle = 0
        self.mirror = 0
    def save(self):
        return [' '.join('FLAG', str(self.x), str(self.y), self.name)]

class Component:
    def parse(self, attributes, lines):
        self.basename = attributes[0]
        self.x    = int(attributes[1])
        self.y    = int(attributes[2])
        self.angle = int(attributes[3][1:])
        self.mirror = 1 if (attributes[3][0] == 'M') else 0
        self.attributes = {}
        self.window = []
        
        while True:
            line = lines.pop(0)
            attrs = line.split(' ')
            if attrs[0] in objTypes.keys():
                lines.insert(0, line)
                break
            elif attrs[0] == 'SYMATTR':
                self.attributes[attrs[1]] = ' '.join(attrs[2:])
            elif attrs[0] == 'WINDOW':
                self.window.append(' '.join(attrs[1:]))
            else:
                warn("LTSpice: Unknown attribute to SYMBOL - " + attrs[0])
    def save(self):
        r =  [' '.join('SYMBOL', self.basename, str(self.x), str(self.y), self.orientation)]
        for window in self.window:
            r.append(' '.join('WINDOW', window))
        for symattr in self.attr.keys():
            r.append(' '.join('SYMATTR', symattr, self.attributes[symattr]))
        return r

class Text:
    def parse(self, attributes, lines):
        self.x = int(attributes[0])
        self.y = int(attributes[1])
        self.alignment = attributes[2]
        self.siz = int(attributes[3])
        self.text = ' '.join(attributes[4:])
        
    def save(self):
        r =  [' '.join([
            'TEXT',
            str(self.x),
            str(self.y),
            str(self.alignment),
            str(self.siz),
            self.text])]
        return r


objTypes = {
    'Version': Version,
    'SHEET': Sheet,
    'WIRE': Wire,
    'FLAG': Flag,
    'SYMBOL': Component,
    'TEXT': Text,
}

def loadItems(lines, end = None):
    items = []
    while lines:
        line = lines.pop(0)
        if not line:
            continue
        attributes = line.split(' ')
        t = attributes[0]
        cl = None
        if t in objTypes.keys():
            cl = objTypes[t]
        else:
            raise(Exception('unknown type ' + t))
        i = cl()
        i.parse(attributes[1:], lines)
        items.append(i)

    return items

def saveItems(items):
    lines = []
    for i in items:
        lines += i.save()
        if hasattr(i, 'embedded'):
            lines += ['['] + saveItems(i.embedded) + [']']
        if hasattr(i, 'attributes'):
            lines += ['{'] + saveItems(i.attributes) + ['}']
    return lines

def load(path):
    with open(path, errors='ignore') as f:
        lines = f.read().split('\n')
        return loadItems(lines)

def save(path, items):
    lines = saveItems(items)
    with open(path,'w') as f:
        f.write('\n'.join(lines))
