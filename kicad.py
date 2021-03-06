from parsekicad import load, distance, save, S, nm

class StringField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items[0])
    def toS(parent, name):
        return S(name, [parent.__getattribute__(name)])

class ClassField:
    def __init__(self, c):
        self.c = c
    def loadS(self, s, parent):
        obj = self.c()
        obj.loadS(s)
        parent.__setattr__(s.name, obj)
    def toS(self, parent, name):
        return parent.__getattribute__(name).toS(name)

class ArrayField:
    def __init__(self, c, name):
        self.c = c
        self.name = name
    def loadS(self, s, parent):
        obj = self.c()
        obj.loadS(s)
        parent.__getattribute__(self.name).append(obj)
    def toS(self, parent, name):
        items = []
        for i in parent.__getattribute__(self.name):
            try:
                items.append(i.toS(name))
            except AttributeError as e:
                raise Exception(e) #attrbute error would be ignored by caller
        return items

class LayersField:
    def loadS(s, parent):
        parent.layers = [Layer(int(l.name), l.items[0], l.items[1]) for l in s.items]
    def toS(parent, name):
        return S(name, [S(str(l.num), [l.name, l.t]) for l in parent.layers])

class NetsField:
    def loadS(s, parent):
        parent.nets[int(s.items[0])] = s.items[1]
    def toS(parent, name):
        r = []
        for k,v in parent.nets.items():
            r.append(S(name, [str(k), v]))
        return r

class DistanceField:
    def loadS(s, parent):
        parent.__setattr__(s.name, distance(s.items[0]))
    def toS(parent, name):
        return S(name, [nm(parent.__getattribute__(name))])

class IntField:
    def loadS(s, parent):
        parent.__setattr__(s.name, int(s.items[0]))
    def toS(parent, name):
        return S(name, [str(parent.__getattribute__(name))])
class SizeField:
    def loadS(s, parent):
        parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1])))
    def toS(parent, name):
        f = parent.__getattribute__(name)
        return S(name, [nm(f[0]), nm(f[1])])
class BoolField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items[0] in ['yes', 'true'])
    def toS(parent, name):
        return S(name, ['true' if parent.__getattribute__(name) else 'false'])
class YesNoField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items[0] in ['yes', 'true'])
    def toS(parent, name):
        return S(name, ['yes' if parent.__getattribute__(name) else 'no'])
class HexField:
    def loadS(s, parent):
        parent.__setattr__(s.name, int(s.items[0], 16))
    def toS(parent, name):
        return S(name, [hex(parent.__getattribute__(name))[2:].upper()])
class NetArrayField:
    def loadS(s, parent):
        parent.nets.append(s.items[0])
    def toS(parent, name):
        return [S(name, [n]) for n in parent.nets]
class NetField:
    def loadS(s, parent):
        parent.net = (int(s.items[0]), s.items[1])
    def toS(parent, name):
        return S(name, [str(parent.net[0]), parent.net[1]])
class PosField:
    def loadS(s, parent):
        if len(s.items) == 3:
            parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1]), float(s.items[2])))
        else:
            parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1])))
    def toS(parent, name):
        f = parent.__getattribute__(name)
        if len(f) == 3:
            return S(name, [nm(f[0]), nm(f[1]), str(f[2])])
        else:
            return S(name, [nm(f[0]), nm(f[1])])
class FontField:
    def loadS(s, parent):
        parent.italic = False
        for c in s.items:
            if c == 'italic':
                parent.italic = True
            elif c.name == 'size':
                SizeField.loadS(c, parent)
            elif c.name == 'thickness':
                DistanceField.loadS(c, parent)
            else:
                raise Exception('unknown field ' + c.name)
    def toS(parent, name):
        i = [SizeField.toS(parent, 'size'), DistanceField.toS(parent,'thickness')]
        if parent.italic:
            i.append('italic')
        return S(name, i)

class LayerSelectionField:
    def loadS(s, parent):
        l1, l2 = s.items[0].split('_')
        parent.lselect1 = int(l1[2:], 16)
        parent.lselect2 = int(l2, 16)
    def toS(parent, name):
        return S(name, [hex(parent.lselect1) + '_' + hex(parent.lselect2)[2:]])
class FlagField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items)
    def toS(parent, name):
        return S(name, parent.__getattribute__(name))
class Pos3DField:
    def loadS(s, parent):
        pos = s.items[0]
        if pos.name != 'xyz':
            raise Exception('unknown coordinates ' + pos.name)
        parent.__setattr__(s.name, (distance(pos.items[0]), distance(pos.items[1]), distance(pos.items[2])))
    def toS(parent, name):
        f = parent.__getattribute__(name)
        return S(name, [S('xyz', [nm(f[0]), nm(f[1]), nm(f[2])])])
class FloatField:
    def loadS(s, parent):
        parent.__setattr__(s.name, float(s.items[0]))
    def toS(parent, name):
        return S(name, [str(parent.__getattribute__(name))])
class HatchField:
    def loadS(s, parent):
        parent.hatchtype = s.items[0]
        parent.hatchsize = distance(s.items[1])
    def toS(parent, name):
        return S(name, [parent.hatchtype, nm(parent.hatchsize)])
class ConnectField:
    def loadS(s, parent):
        if s.items[0] in ['no', 'yes', 'thru_hole_only']:
            parent.connect = s.items[0]
            clr = s.items[1]
        else:
            parent.connect = 'thermal'
            clr = s.items[0]
        if clr.name != 'clearance':
            raise Exception('expected clearance')
        parent.clearance = distance(clr.items[0])
    def toS(parent, name):
        i = [ parent.connect ] if parent.connect != 'thermal' else []
        return S(name, i + [S('clearance', [nm(parent.clearance)])])
class KeepoutsField:
    def loadS(s, parent):
        parent.keepouts = set()
        for i in s.items:
            if i.items[0] != 'not_allowed':
                raise Exception('unknown keyword '  + i.items[0])
            parent.keepouts.add(i.name)
    def toS(parent, name):
        return S(name, [ S(k, ['not_allowed']) for k in parent.keepouts])
class PointsField:
    def loadS(s, parent):
        parent.pts = []
        if s.items[0].name != 'pts':
            raise Exception('expect points')
        for c in s.items[0].items:
            if c.name != 'xy':
                raise Exception('expect coordinates')
            parent.pts.append((distance(c.items[0]), distance(c.items[1])))
    def toS(parent, name):
        return S(name, [ S('pts', [ S('xy', [nm(p[0]), nm(p[1])]) for p in parent.pts]) ])

class Loadable:
    def loadS(self,s):
        self.loadFields(s.items)
    def toS(self, name):
        return S(name, self.fieldsToS())
    def loadFields(self, items):
        for i in items:
            self.fields[i.name].loadS(i, self)
    def fieldsToS(self):
        r = []
        for name,field in self.fields.items():
            try:
                s = field.toS(self, name)
                if isinstance(s, S):
                    r.append(s)
                else:
                    r += s  #can return array
            except AttributeError:  #blank fields are skipped
                pass
        return r


class General(Loadable):
    fields = {
            'thickness' : DistanceField,
            'drawings' : IntField,
            'tracks' : IntField,
            'zones' : IntField,
            'modules' : IntField,
            'nets' : IntField
            }

class Layer:
    def __init__(self, num, name, t):
        self.num = num
        self.name = name
        self.t = t

class PlotParams(Loadable):
    fields = {
        'layerselection' : LayerSelectionField,
        'usegerberextensions' : BoolField,
        'usegerberattributes' : BoolField,
        'usegerberadvancedattributes' : BoolField,
        'creategerberjobfile' : BoolField,
        'excludeedgelayer' : BoolField,
        'linewidth' : DistanceField,
        'plotframeref' : BoolField,
        'viasonmask' : BoolField,
        'mode' : IntField,
        'useauxorigin' : BoolField,
        'hpglpennumber' : IntField,
        'hpglpenspeed' : IntField,
        'hpglpendiameter' : DistanceField,
        'psnegative' : BoolField,
        'psa4output' : BoolField,
        'plotreference' : BoolField,
        'plotvalue' : BoolField,
        'plotinvisibletext' : BoolField,
        'padsonsilk' : BoolField,
        'subtractmaskfromsilk' : BoolField,
        'outputformat' : IntField,
        'drillshape' : IntField,
        'mirror' : BoolField,
        'scaleselection' : IntField,
        'outputdirectory' : StringField
        }

class Setup(Loadable):
    fields = {
            'last_trace_width' : DistanceField,
            'trace_clearance' : DistanceField,
            'zone_clearance' : DistanceField,
            'zone_45_only' : YesNoField,
            'trace_min' : DistanceField,
            'segment_width' : DistanceField,
            'edge_width' : DistanceField,
            'via_size' : DistanceField,
            'via_drill' : DistanceField,
            'via_min_size' : DistanceField,
            'via_min_drill' : DistanceField,
            'uvia_size' : DistanceField,
            'uvia_drill' : DistanceField,
            'uvias_allowed' : YesNoField,
            'uvia_min_size' : DistanceField,
            'uvia_min_drill' : DistanceField,
            'pcb_text_width' : DistanceField,
            'pcb_text_size' : SizeField,
            'mod_edge_width' : DistanceField,
            'mod_text_size' : SizeField,
            'mod_text_width' : DistanceField,
            'pad_size' : SizeField,
            'pad_drill' : DistanceField,
            'pad_to_mask_clearance' : DistanceField,
            'aux_axis_origin' : SizeField,
            'grid_origin' : SizeField,
            'visible_elements' : HexField,
            'pcbplotparams' : ClassField(PlotParams)
            }


class NetClass(Loadable):
    fields = {
            'clearance' : DistanceField,
            'trace_width' : DistanceField,
            'via_dia' : DistanceField,
            'via_drill' : DistanceField,
            'uvia_dia' : DistanceField,
            'uvia_drill' : DistanceField,
            'add_net' : NetArrayField
            }
    def __init__(self):
        self.nets = []
    def loadS(self, s):
        self.name = s.items[0]
        self.descr = s.items[1]
        self.loadFields(s.items[2:])
    def toS(self, name):
        return S(name, [self.name, self.descr] + self.fieldsToS())

class Effects(Loadable):
    fields = {
            'font' : FontField,
            'justify' : FlagField
            }


class Text(Loadable):
    fields = {
            'at' : PosField,
            'layer' : StringField,
            'effects' : ClassField(Effects)
            }
    def loadS(self, s):
        if s.name == 'fp_text':
            self.t = s.items[0]
            i = 1
        else:
            self.t = None
            i = 0
        self.text = s.items[i]
        self.loadFields(s.items[i+1:])
    def toS(self, name):
        if self.t:
            return S(name, [self.t, self.text] + self.fieldsToS())
        else:
            return S(name, [self.text] + self.fieldsToS())


class Line(Loadable):
    fields = {
            'start' : PosField,
            'end' : PosField,
            'layer' : StringField,
            'width' : DistanceField,
            }

class Segment(Loadable):
    fields = {
            'start' : PosField,
            'end' : PosField,
            'width' : DistanceField,
            'layer' : StringField,
            'net' : StringField,
            'tstamp' : HexField
            }

class Arc(Loadable):
    fields = {
            'start' : PosField,
            'end' : PosField,
            'angle' : FloatField,
            'layer' : StringField,
            'width' : DistanceField
            }

class Circle(Loadable):
    fields = {
            'center' : PosField,
            'end' : PosField,
            'layer' : StringField,
            'width' : DistanceField
            }

class Pad(Loadable):
    fields = {
            'at' : PosField,
            'size' : SizeField,
            'drill' : DistanceField,
            'layers' : FlagField,
            'net' : NetField,
            }
    def loadS(self, s):
        self.name = s.items[0]
        self.t = s.items[1]
        self.shape = s.items[2]
        self.loadFields(s.items[3:])
    def toS(self, name):
        return S(name, [self.name, self.t, self.shape] + self.fieldsToS())

class Via(Loadable):
    fields = {
            'at' : PosField,
            'size' : DistanceField,
            'drill' : DistanceField,
            'layers' : FlagField,
            'net' : IntField
            }

class Model(Loadable):
    fields = {
            'at' : Pos3DField,
            'scale' : Pos3DField,
            'rotate' : Pos3DField
            }
    def loadS(self, s):
        self.path = s.items[0]
        self.loadFields(s.items[1:])
    def toS(self, name):
        return S(name, [self.path] + self.fieldsToS())

class Module(Loadable):
    fields = {
            'layer' : StringField,
            'tedit' : HexField,
            'tstamp' : HexField,
            'at' : PosField,
            'descr' : StringField,
            'tags' : StringField,
            'attr' : StringField,
            'path' : StringField,
            'fp_text' : ArrayField(Text, 'texts'),
            'fp_line' : ArrayField(Line, 'lines'),
            'fp_circle' : ArrayField(Circle, 'circles'),
            'fp_arc' : ArrayField(Arc, 'arcs'),
            'pad' : ArrayField(Pad, 'pads'),
            'model' : ClassField(Model),
            }

    def __init__(self):
        self.texts = []
        self.lines = []
        self.pads = []
        self.circles = []
        self.arcs = []
    def loadS(self, s):
        self.name = s.items[0]
        self.loadFields(s.items[1:])
    def toS(self, name):
        return S(name, [self.name] + self.fieldsToS())

class Fill(Loadable):
    fields = {
                'arc_segments': IntField,
                'thermal_gap': DistanceField,
                'thermal_bridge_width': DistanceField,
                'smoothing': StringField,
                'radius': DistanceField
            }

class Zone(Loadable):
    fields = {
            'net': IntField,
            'net_name': StringField,
            'layer' : StringField,
            'tstamp' : HexField,
            'hatch' : HatchField,
            'timestamp': HexField,
            'connect_pads' : ConnectField,
            'min_thickness' : DistanceField,
            'keepout' : KeepoutsField,
            'fill' : ClassField(Fill),
            'polygon' : PointsField
            }
    pts = []

class Kicad(Loadable):
    fields = {
            'version' : StringField,
            'host' : FlagField,
            'general' : ClassField(General),
            'version' : StringField,
            'page' : StringField,
            'layers' : LayersField,
            'setup' : ClassField(Setup),
            'net':  NetsField,
            'net_class': ArrayField(NetClass, 'classes'),
            'module': ArrayField(Module, 'modules'),
            'gr_arc': ArrayField(Arc, 'arcs'),
            'gr_circle': ArrayField(Circle, 'circles'),
            'gr_text': ArrayField(Text, 'texts'),
            'gr_line': ArrayField(Line, 'lines'),
            'segment': ArrayField(Segment, 'segments'),
            'via': ArrayField(Via, 'vias'),
            'zone': ArrayField(Zone, 'zones')
    }
    def __init__(self):
        self.nets = {}
        self.classes = []
        self.modules = []
        self.circles = []
        self.arcs = []
        self.lines = []
        self.texts = []
        self.vias = []
        self.zones = []
        self.segments = []
    def toS(self):
        return S('kicad_pcb', self.fieldsToS())
    def loadS(self, s):
        if s.name != 'kicad_pcb':
            raise Exception('Unknown format')
        self.loadFields(s.items)
    def load(self, path):
        s = load(path)
        self.loadS(s)
    def save(self, path):
        s = self.toS()
        save(path, s)
