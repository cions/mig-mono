#!/usr/bin/python
import fontforge
from itertools import groupby
from gi.repository import GLib

fMig = fontforge.open('mig-mono-regular.ttf')

widths = list(sorted(set(g.width for g in fMig.glyphs() if g.unicode > 0)))
assert len(widths) == 2, widths

def tohex(cp):
    if cp < 0x10000:
        return '<U{:04X}>'.format(cp)
    else:
        return '<U{:08X}>'.format(cp)

def generator():
    n = 0
    for cp in range(0, 0x110000):
        try:
            ch = chr(cp)
            ch.encode('utf-8')
        except UnicodeEncodeError:
            continue
        if not GLib.unichar_isdefined(ch):
            continue
        elif GLib.unichar_iszerowidth(ch):
            yield (cp - n, tohex(cp), 0)
        elif GLib.unichar_iswide(ch):
            yield (cp - n, tohex(cp), 2)
        else:
            try:
                if fMig[cp].width == widths[1]:
                    yield (cp - n, tohex(cp), 2)
                else:
                    continue
            except:
                continue
        n += 1

print()
print("% Character width according to MiG Mono fonts")
print("WIDTH")
for k, it in groupby(generator(), lambda x: (x[0], x[2])):
    ls = list(it)
    if len(ls) == 1:
        print("{} {}".format(ls[0][1], k[1]))
    else:
        print("{}...{} {}".format(ls[0][1], ls[-1][1], k[1]))
print("END WIDTH")

fMig.close()
