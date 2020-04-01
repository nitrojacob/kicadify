#!/usr/bin/env python3
import time, sys, os

myDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(myDir, "parsers"))

import ltspice, eeschema

components = {
    'nmos':['Device:Q_NMOS_GDS', 10, 10, 0],
    'pmos':['Device:Q_PMOS_GDS', 10, 10, 0],
    'voltage':['pspice:VSOURCE', 10, 10, 0],
    'ind':['Device:L', 10, 10, 0],
    'cap':['Device:C', 10, 10, 0],
    'res':['Device:R', 10, 10, 0],
    'Vcc':['power:VCC', 10, 10, 0],
    '0':['power:GND', 10, 10, 0],
    '*':['power:PWR_FLAG', 10, 10, 0]
}

orientConv = {
    (0, 0):   [1, 0,  0, -1],
    (90, 0):  [ 0, -1, -1, 0],
    (180, 0): [-1, 0, 0, 1],
    (270, 0): [0, 1, 1, 0],
    (0, 1):   [-1, 0, 0, -1],  
    (90, 1):  [0, -1, 1, 0],
    (180, 1): [1, 0, 0, 1],
    (270, 1): [0, 1, -1, 0],
}

def warn(msg):
    print("[WARN]LTSpice2KiCad:", msg)

def coor(x,y):
    return int(3.937 * x), int(3.937 * y)

def text(kt, gt, v, yoff):
    kt.text = v
    kt.x, kt.y = coor(gt.x, gt.y + yoff)
    kt.flags = '0000'

def emtpyField(x,y):
    f = eeschema.Field()
    f.text = ''
    f.orientation = 'H'
    f.x, f.y = coor(x, y)
    f.size = 50
    f.flags = '0001'    #hidden
    f.just = 'C'
    f.style = 'CNN'
    return f

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage\n%s ltspice.sch kicad.sch" % sys.argv[0])
        sys.exit(1)
    
    ts = int(time.time())
    
    components = ltspice.components
    
    gitems = ltspice.load(sys.argv[1])
    eitems = []
    
    ver = eeschema.Version()
    ver.version = 4
    eitems.append(ver)
    
    layers = eeschema.Layers()
    layers.nn = 26
    layers.mm = 0
    eitems.append(layers)
    
    page = eeschema.Page()
    page.format = 'A4'
    page.dimx = 11693
    page.dimy = 8268
    page.fields = {}
    eitems.append(page)
    
    for gi in gitems:
        if isinstance(gi, ltspice.Wire):
            wire = eeschema.Wire()
            wire.x1, wire.y1 = coor(gi.x1, gi.y1)
            wire.x2, wire.y2 = coor(gi.x2, gi.y2)
            wire.type = 'Wire'
            eitems.append(wire)
    
            con = eeschema.Connection()
            con.x, con.y = coor(gi.x1, gi.y1)
            eitems.append(con)
    
            con = eeschema.Connection()
            con.x, con.y = coor(gi.x2, gi.y2)
            eitems.append(con)
            if hasattr(gi, 'attributes'):
                for a in gi.attributes:
                    k, v = a.text.split('=')
                    if k == 'netname':
                        label = eeschema.Text()
                        label.type = 'Label'
                        label.shape = '~'
                        label.x, label.y = coor(a.x, a.y)
                        label.orientation = 0
                        label.size = 50
                        if v.startswith('\_') and v.endswith('\_') and len(v) > 3:
                            v = '~' + v[2:-2]
                        label.text = v
                        eitems.append(label)
                        
        if isinstance(gi, ltspice.Flag):
            if not gi.basename in components:
                warn('Changing Flag '+ gi.basename +' to *, as no mapping was found.')
                gi.basename = '*'
            if gi.basename in components:
                name, xoff, yoff, aoff = components[gi.basename]
                component = eeschema.Componnent()
                component.fields = []
                component.ref = '#PWR'
                for i in range(4):  #default fields
                    f = emtpyField(gi.x, gi.y)
                    component.fields.append(f)
                if hasattr(gi, 'attributes'):
                    for a in gi.attributes:
                        k, v = a.text.split('=')
                        if k == 'refdes':
                            component.ref = v
                            text(component.fields[0], gi, v)
                        if k == 'value':
                            text(component.fields[1], gi, v)
                        if k == 'footprint':
                            text(component.fields[2], gi, v)
                        if k == 'mpn':
                            f = emtpyField(gi.x, gi.y)
                            f.name = 'mpn'
                            text(f, a, v)
                            component.fields.append(f)
                        if k == 'manufacturer':
                            f = emtpyField(gi.x, gi.y)
                            f.name = 'manufacturer'
                            text(f, a, v)
                            component.fields.append(f)
                            
                component.name = name
                component.N = 1
                component.mm = 1
                component.ts = ts
                ts += 1
                component.x, component.y = coor(gi.x  + xoff, gi.y + yoff)
                component.orientation = orientConv[((gi.angle + aoff) % 360, 0)]
                eitems.append(component)
            else:
                warn('Skipping Flag - '+ gi.basename)
    
        if isinstance(gi, ltspice.Component):
            if gi.basename in components:
                name, xoff, yoff, aoff = components[gi.basename]
                if gi.mirror:
                    xoff = -xoff
                if gi.angle == 90:
                    xoff, yoff = -yoff, xoff
                if gi.angle == 180:
                    xoff, yoff = -xoff, -yoff
                if gi.angle == 270:
                    xoff, yoff = yoff, -xoff
                component = eeschema.Componnent()
                component.fields = []
                component.ref = 'X'
                for i in range(4):  #default fields
                    f =emtpyField(gi.x, gi.y)
                    component.fields.append(f)
                if hasattr(gi, 'attributes'):
                    for a in gi.attributes.keys():
                        v = gi.attributes[a]
                        if a == 'InstName':
                            component.ref = v
                            text(component.fields[0], gi, v, -20)
                        if a == 'Value':
                            text(component.fields[1], gi, v, 0)
                        if a == 'footprint':
                            text(component.fields[2], gi, v, 20)
                        if a == 'mpn':
                            f = emtpyField(gi.x, gi.y)
                            f.name = 'mpn'
                            text(f, gi, v, 40)
                            component.fields.append(f)
                        if a == 'manufacturer':
                            f = emtpyField(gi.x, gi.y)
                            f.name = 'manufacturer'
                            text(f, a, v, 60    )
                            component.fields.append(f)
                            
                component.name = name
                component.N = 1
                component.mm = 1
                component.ts = ts
                ts += 1
                component.x, component.y = coor(gi.x  + xoff, gi.y + yoff)
                component.orientation = orientConv[((gi.angle + aoff) % 360, gi.mirror)]
                eitems.append(component)
            else:
                warn('Skipping component - '+ gi.basename)
    
    eeschema.save(sys.argv[2], eitems)
