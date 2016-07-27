#!/usr/bin/fontforge -script
import math
import fontforge
import psMat

em = 1024
width = 512
ascent = 880
descent = 234

bl = 0
br = width
bw = br - bl
bmh = (bl + br) / 2.0
bb = -descent
bt = ascent
bh = bt - bb
bmv = (bb + bt) / 2.0
swl2 = 38 / 2.0
swb2 = 112 / 2.0
dlgap2 = 80 / 2.0
dldisp = dlgap2 + 2 * swl2

xrefT = psMat.compose(psMat.translate(-2 * bmh, 0), psMat.scale(-1, 1))
yrefT = psMat.compose(psMat.translate(0, -2 * bmv), psMat.scale(1, -1))

def addchar(font, cp, contours):
    glyph = font.createChar(cp, 'uni{:04X}'.format(cp))
    pen = glyph.glyphPen()
    for c in contours:
        c.draw(pen)
    pen = None
    glyph.removeOverlap()
    glyph.simplify(1, ('forcelines',))
    glyph.round()
    glyph.correctDirection()
    glyph.canonicalStart()
    glyph.canonicalContours()
    glyph.width = width

def rect(left, bottom, right, top):
    c = fontforge.contour()
    c.moveTo(left, bottom)
    c.lineTo(left, top)
    c.lineTo(right, top)
    c.lineTo(right, bottom)
    c.closed = True
    return c

def frange(start, stop, step):
    while start < stop:
        yield start
        start += step


font = fontforge.font()
font.familyname = 'ReplaceParts'
font.fontname = font.familyname
font.fullname = font.familyname
font.weight = 'Regular'
font.em = em
font.ascent = ascent
font.descent = descent
font.os2_winascent = ascent
font.os2_winascent_add = 0
font.os2_windescent = descent
font.os2_windescent_add = 0
font.os2_typoascent = ascent
font.os2_typoascent_add = 0
font.os2_typodescent = -descent
font.os2_typodescent_add = 0
font.os2_typolinegap = 0
font.hhea_ascent = ascent
font.hhea_ascent_add = 0
font.hhea_descent = -descent
font.hhea_descent_add = 0
font.hhea_linegap = 0

# Box drawing characters
NONE   = 0
LIGHT  = 1
BOLD   = 2
DOUBLE = 3

def boxdrawing_sbound(l, r, o):
    if l == NONE and r == NONE:
        return 0
    elif l == DOUBLE and r == DOUBLE and o == NONE:
        return -dlgap2
    elif l == DOUBLE or r == DOUBLE:
        return dldisp
    elif l == BOLD or r == BOLD:
        return swb2
    else:
        return swl2

def boxdrawing_dbound(l, r):
    if l == NONE and r == NONE:
        return (0, 0)
    elif l == DOUBLE and r == DOUBLE:
        return (-dlgap2, -dlgap2)
    elif l == DOUBLE and r == NONE:
        return (-dlgap2, dldisp)
    elif l == NONE and r == DOUBLE:
        return (dldisp, -dlgap2)
    else:
        return (swl2, swl2)

def boxdrawing(left, top, right, bottom):
    contours = []

    if left == LIGHT or left == BOLD:
        bound = bmh + boxdrawing_sbound(top, bottom, right)
        if left == LIGHT:
            contours.append(rect(bl, bmv - swl2, bound, bmv + swl2))
        else:
            contours.append(rect(bl, bmv - swb2, bound, bmv + swb2))
    elif left == DOUBLE:
        bound1, bound2 = (bmh + x for x in boxdrawing_dbound(top, bottom))
        contours.append(rect(bl, bmv + dlgap2, bound1, bmv + dldisp))
        contours.append(rect(bl, bmv - dldisp, bound2, bmv - dlgap2))

    if top == LIGHT or top == BOLD:
        bound = bmv - boxdrawing_sbound(right, left, bottom)
        if top == LIGHT:
            contours.append(rect(bmh - swl2, bound, bmh + swl2, bt))
        else:
            contours.append(rect(bmh - swb2, bound, bmh + swb2, bt))
    elif top == DOUBLE:
        bound1, bound2 = (bmv - x for x in boxdrawing_dbound(right, left))
        contours.append(rect(bmh + dlgap2, bound1, bmh + dldisp, bt))
        contours.append(rect(bmh - dldisp, bound2, bmh - dlgap2, bt))

    if right == LIGHT or right == BOLD:
        bound = bmh - boxdrawing_sbound(bottom, top, left)
        if right == LIGHT:
            contours.append(rect(bound, bmv - swl2, br, bmv + swl2))
        else:
            contours.append(rect(bound, bmv - swb2, br, bmv + swb2))
    elif right == DOUBLE:
        bound1, bound2 = (bmh - x for x in boxdrawing_dbound(bottom, top))
        contours.append(rect(bound1, bmv - dldisp, br, bmv - dlgap2))
        contours.append(rect(bound2, bmv + dlgap2, br, bmv + dldisp))

    if bottom == LIGHT or bottom == BOLD:
        bound = bmv + boxdrawing_sbound(left, right, top)
        if bottom == LIGHT:
            contours.append(rect(bmh - swl2, bb, bmh + swl2, bound))
        else:
            contours.append(rect(bmh - swb2, bb, bmh + swb2, bound))
    elif bottom == DOUBLE:
        bound1, bound2 = (bmv + x for x in boxdrawing_dbound(left, right))
        contours.append(rect(bmh - dldisp, bb, bmh - dlgap2, bound1))
        contours.append(rect(bmh + dlgap2, bb, bmh + dldisp, bound2))

    return contours

def boxdrawing_hdash(number, weight):
    s = float(bw) / number
    dl = 0.75 * s
    sw2 = swl2 if weight == LIGHT else swb2
    return [rect(l, bmv - sw2, l + dl, bmv + sw2)
            for l in frange(bl + s / 8.0, br, s)]

def boxdrawing_vdash(number, weight):
    s = float(bh) / number
    dl = 0.75 * s
    sw2 = swl2 if weight == LIGHT else swb2
    return [rect(bmh - sw2, b, bmh + sw2, b + dl)
            for b in frange(bb + s / 8.0, bt, s)]

def boxdrawing_arc(xref=False, yref=False):
    K = 0.5522847498
    r = min(bw, bh) / 2.0
    Ci = K * (r - swl2) - r
    Co = K * (r + swl2) - r

    c = fontforge.contour()
    c.moveTo(bl, bmv + swl2)
    c.lineTo(bmh - r, bmv + swl2)
    c.cubicTo((bmh + Ci, bmv + swl2),
              (bmh - swl2, bmv - Ci),
              (bmh - swl2, bmv + r))
    c.lineTo(bmh - swl2, bt)
    c.lineTo(bmh + swl2, bt)
    c.lineTo(bmh + swl2, bmv + r)
    c.cubicTo((bmh + swl2, bmv - Co),
              (bmh + Co, bmv - swl2),
              (bmh - r, bmv - swl2))
    c.lineTo(bl, bmv - swl2)
    c.closed = True

    if xref:
        c.transform(xrefT)
    if yref:
        c.transform(yrefT)
    return [c]

def boxdrawing_diagonal(up=True, down=True):
    t = math.atan2(bh, bw)
    dx = swl2 / math.sin(t)
    dy = swl2 / math.cos(t)
    contours = []
    if up:
        c = fontforge.contour()
        c.moveTo(bl, bb)
        c.lineTo(bl, bb + dy)
        c.lineTo(br - dx, bt)
        c.lineTo(br, bt)
        c.lineTo(br, bt - dy)
        c.lineTo(bl + dx, bb)
        c.closed = True
        contours.append(c)
    if down:
        c = fontforge.contour()
        c.moveTo(bl, bt)
        c.lineTo(bl + dx, bt)
        c.lineTo(br, bb + dy)
        c.lineTo(br, bb)
        c.lineTo(br - dx, bb)
        c.lineTo(bl, bt - dy)
        c.closed = True
        contours.append(c)
    return contours

addchar(font, 0x2500, boxdrawing(LIGHT, NONE,  LIGHT, NONE))
addchar(font, 0x2501, boxdrawing(BOLD,  NONE,  BOLD,  NONE))
addchar(font, 0x2502, boxdrawing(NONE,  LIGHT, NONE,  LIGHT))
addchar(font, 0x2503, boxdrawing(NONE,  BOLD,  NONE,  BOLD))
addchar(font, 0x2504, boxdrawing_hdash(3, LIGHT))
addchar(font, 0x2505, boxdrawing_hdash(3, BOLD))
addchar(font, 0x2506, boxdrawing_vdash(3, LIGHT))
addchar(font, 0x2507, boxdrawing_vdash(3, BOLD))
addchar(font, 0x2508, boxdrawing_hdash(4, LIGHT))
addchar(font, 0x2509, boxdrawing_hdash(4, BOLD))
addchar(font, 0x250A, boxdrawing_vdash(4, LIGHT))
addchar(font, 0x250B, boxdrawing_vdash(4, BOLD))
addchar(font, 0x250C, boxdrawing(NONE,  NONE,  LIGHT, LIGHT))
addchar(font, 0x250D, boxdrawing(NONE,  NONE,  BOLD,  LIGHT))
addchar(font, 0x250E, boxdrawing(NONE,  NONE,  LIGHT, BOLD))
addchar(font, 0x250F, boxdrawing(NONE,  NONE,  BOLD,  BOLD))
addchar(font, 0x2510, boxdrawing(LIGHT, NONE,  NONE,  LIGHT))
addchar(font, 0x2511, boxdrawing(BOLD,  NONE,  NONE,  LIGHT))
addchar(font, 0x2512, boxdrawing(LIGHT, NONE,  NONE,  BOLD))
addchar(font, 0x2513, boxdrawing(BOLD,  NONE,  NONE,  BOLD))
addchar(font, 0x2514, boxdrawing(NONE,  LIGHT, LIGHT, NONE))
addchar(font, 0x2515, boxdrawing(NONE,  LIGHT, BOLD,  NONE))
addchar(font, 0x2516, boxdrawing(NONE,  BOLD,  LIGHT, NONE))
addchar(font, 0x2517, boxdrawing(NONE,  BOLD,  BOLD,  NONE))
addchar(font, 0x2518, boxdrawing(LIGHT, LIGHT, NONE,  NONE))
addchar(font, 0x2519, boxdrawing(BOLD,  LIGHT, NONE,  NONE))
addchar(font, 0x251A, boxdrawing(LIGHT, BOLD,  NONE,  NONE))
addchar(font, 0x251B, boxdrawing(BOLD,  BOLD,  NONE,  NONE))
addchar(font, 0x251C, boxdrawing(NONE,  LIGHT, LIGHT, LIGHT))
addchar(font, 0x251D, boxdrawing(NONE,  LIGHT, BOLD,  LIGHT))
addchar(font, 0x251E, boxdrawing(NONE,  BOLD,  LIGHT, LIGHT))
addchar(font, 0x251F, boxdrawing(NONE,  LIGHT, LIGHT, BOLD))
addchar(font, 0x2520, boxdrawing(NONE,  BOLD,  LIGHT, BOLD))
addchar(font, 0x2521, boxdrawing(NONE,  BOLD,  BOLD,  LIGHT))
addchar(font, 0x2522, boxdrawing(NONE,  LIGHT, BOLD,  BOLD))
addchar(font, 0x2523, boxdrawing(NONE,  BOLD,  BOLD,  BOLD))
addchar(font, 0x2524, boxdrawing(LIGHT, LIGHT, NONE,  LIGHT))
addchar(font, 0x2525, boxdrawing(BOLD,  LIGHT, NONE,  LIGHT))
addchar(font, 0x2526, boxdrawing(LIGHT, BOLD,  NONE,  LIGHT))
addchar(font, 0x2527, boxdrawing(LIGHT, LIGHT, NONE,  BOLD))
addchar(font, 0x2528, boxdrawing(LIGHT, BOLD,  NONE,  BOLD))
addchar(font, 0x2529, boxdrawing(BOLD,  BOLD,  NONE,  LIGHT))
addchar(font, 0x252A, boxdrawing(BOLD,  LIGHT, NONE,  BOLD))
addchar(font, 0x252B, boxdrawing(BOLD,  BOLD,  NONE,  BOLD))
addchar(font, 0x252C, boxdrawing(LIGHT, NONE,  LIGHT, LIGHT))
addchar(font, 0x252D, boxdrawing(BOLD,  NONE,  LIGHT, LIGHT))
addchar(font, 0x252E, boxdrawing(LIGHT, NONE,  BOLD,  LIGHT))
addchar(font, 0x252F, boxdrawing(BOLD,  NONE,  BOLD,  LIGHT))
addchar(font, 0x2530, boxdrawing(LIGHT, NONE,  LIGHT, BOLD))
addchar(font, 0x2531, boxdrawing(BOLD,  NONE,  LIGHT, BOLD))
addchar(font, 0x2532, boxdrawing(LIGHT, NONE,  BOLD,  BOLD))
addchar(font, 0x2533, boxdrawing(BOLD,  NONE,  BOLD,  BOLD))
addchar(font, 0x2534, boxdrawing(LIGHT, LIGHT, LIGHT, NONE))
addchar(font, 0x2535, boxdrawing(BOLD,  LIGHT, LIGHT, NONE))
addchar(font, 0x2536, boxdrawing(LIGHT, LIGHT, BOLD,  NONE))
addchar(font, 0x2537, boxdrawing(BOLD,  LIGHT, BOLD,  NONE))
addchar(font, 0x2538, boxdrawing(LIGHT, BOLD,  LIGHT, NONE))
addchar(font, 0x2539, boxdrawing(BOLD,  BOLD,  LIGHT, NONE))
addchar(font, 0x253A, boxdrawing(LIGHT, BOLD,  BOLD,  NONE))
addchar(font, 0x253B, boxdrawing(BOLD,  BOLD,  BOLD,  NONE))
addchar(font, 0x253C, boxdrawing(LIGHT, LIGHT, LIGHT, LIGHT))
addchar(font, 0x253D, boxdrawing(BOLD,  LIGHT, LIGHT, LIGHT))
addchar(font, 0x253E, boxdrawing(LIGHT, LIGHT, BOLD,  LIGHT))
addchar(font, 0x253F, boxdrawing(BOLD,  LIGHT, BOLD,  LIGHT))
addchar(font, 0x2540, boxdrawing(LIGHT, BOLD,  LIGHT, LIGHT))
addchar(font, 0x2541, boxdrawing(LIGHT, LIGHT, LIGHT, BOLD))
addchar(font, 0x2542, boxdrawing(LIGHT, BOLD,  LIGHT, BOLD))
addchar(font, 0x2543, boxdrawing(BOLD,  BOLD,  LIGHT, LIGHT))
addchar(font, 0x2544, boxdrawing(LIGHT, BOLD,  BOLD,  LIGHT))
addchar(font, 0x2545, boxdrawing(BOLD,  LIGHT, LIGHT, BOLD))
addchar(font, 0x2546, boxdrawing(LIGHT, LIGHT, BOLD,  BOLD))
addchar(font, 0x2547, boxdrawing(BOLD,  BOLD,  BOLD,  LIGHT))
addchar(font, 0x2548, boxdrawing(BOLD,  LIGHT, BOLD,  BOLD))
addchar(font, 0x2549, boxdrawing(BOLD,  BOLD,  LIGHT, BOLD))
addchar(font, 0x254A, boxdrawing(LIGHT, BOLD,  BOLD,  BOLD))
addchar(font, 0x254B, boxdrawing(BOLD,  BOLD,  BOLD,  BOLD))
addchar(font, 0x254C, boxdrawing_hdash(2, LIGHT))
addchar(font, 0x254D, boxdrawing_hdash(2, BOLD))
addchar(font, 0x254E, boxdrawing_vdash(2, LIGHT))
addchar(font, 0x254F, boxdrawing_vdash(2, BOLD))
addchar(font, 0x2550, boxdrawing(DOUBLE, NONE,   DOUBLE, NONE))
addchar(font, 0x2551, boxdrawing(NONE,   DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2552, boxdrawing(NONE,   NONE,   DOUBLE, LIGHT))
addchar(font, 0x2553, boxdrawing(NONE,   NONE,   LIGHT,  DOUBLE))
addchar(font, 0x2554, boxdrawing(NONE,   NONE,   DOUBLE, DOUBLE))
addchar(font, 0x2555, boxdrawing(DOUBLE, NONE,   NONE,   LIGHT))
addchar(font, 0x2556, boxdrawing(LIGHT,  NONE,   NONE,   DOUBLE))
addchar(font, 0x2557, boxdrawing(DOUBLE, NONE,   NONE,   DOUBLE))
addchar(font, 0x2558, boxdrawing(NONE,   LIGHT,  DOUBLE, NONE))
addchar(font, 0x2559, boxdrawing(NONE,   DOUBLE, LIGHT,  NONE))
addchar(font, 0x255A, boxdrawing(NONE,   DOUBLE, DOUBLE, NONE))
addchar(font, 0x255B, boxdrawing(DOUBLE, LIGHT,  NONE,   NONE))
addchar(font, 0x255C, boxdrawing(LIGHT,  DOUBLE, NONE,   NONE))
addchar(font, 0x255D, boxdrawing(DOUBLE, DOUBLE, NONE,   NONE))
addchar(font, 0x255E, boxdrawing(NONE,   LIGHT,  DOUBLE, LIGHT))
addchar(font, 0x255F, boxdrawing(NONE,   DOUBLE, LIGHT,  DOUBLE))
addchar(font, 0x2560, boxdrawing(NONE,   DOUBLE, DOUBLE, DOUBLE))
addchar(font, 0x2561, boxdrawing(DOUBLE, LIGHT,  NONE,   LIGHT))
addchar(font, 0x2562, boxdrawing(LIGHT,  DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2563, boxdrawing(DOUBLE, DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2564, boxdrawing(DOUBLE, NONE,   DOUBLE, LIGHT))
addchar(font, 0x2565, boxdrawing(LIGHT,  NONE,   LIGHT,  DOUBLE))
addchar(font, 0x2566, boxdrawing(DOUBLE, NONE,   DOUBLE, DOUBLE))
addchar(font, 0x2567, boxdrawing(DOUBLE, LIGHT,  DOUBLE, NONE))
addchar(font, 0x2568, boxdrawing(LIGHT,  DOUBLE, LIGHT,  NONE))
addchar(font, 0x2569, boxdrawing(DOUBLE, DOUBLE, DOUBLE, NONE))
addchar(font, 0x256A, boxdrawing(DOUBLE, LIGHT,  DOUBLE, LIGHT))
addchar(font, 0x256B, boxdrawing(LIGHT,  DOUBLE, LIGHT,  DOUBLE))
addchar(font, 0x256C, boxdrawing(DOUBLE, DOUBLE, DOUBLE, DOUBLE))
addchar(font, 0x256D, boxdrawing_arc(True,  True))
addchar(font, 0x256E, boxdrawing_arc(False, True))
addchar(font, 0x256F, boxdrawing_arc(False, False))
addchar(font, 0x2570, boxdrawing_arc(True,  False))
addchar(font, 0x2571, boxdrawing_diagonal(True,  False))
addchar(font, 0x2572, boxdrawing_diagonal(False, True))
addchar(font, 0x2573, boxdrawing_diagonal(True,  True))
addchar(font, 0x2574, boxdrawing(LIGHT, NONE,  NONE,  NONE))
addchar(font, 0x2575, boxdrawing(NONE,  LIGHT, NONE,  NONE))
addchar(font, 0x2576, boxdrawing(NONE,  NONE,  LIGHT, NONE))
addchar(font, 0x2577, boxdrawing(NONE,  NONE,  NONE,  LIGHT))
addchar(font, 0x2578, boxdrawing(BOLD,  NONE,  NONE,  NONE))
addchar(font, 0x2579, boxdrawing(NONE,  BOLD,  NONE,  NONE))
addchar(font, 0x257A, boxdrawing(NONE,  NONE,  BOLD,  NONE))
addchar(font, 0x257B, boxdrawing(NONE,  NONE,  NONE,  BOLD))
addchar(font, 0x257C, boxdrawing(LIGHT, NONE,  BOLD,  NONE))
addchar(font, 0x257D, boxdrawing(NONE,  LIGHT, NONE,  BOLD))
addchar(font, 0x257E, boxdrawing(BOLD,  NONE,  LIGHT, NONE))
addchar(font, 0x257F, boxdrawing(NONE,  BOLD,  NONE,  LIGHT))

# Block Elements
def block_shade(darkness):
    vs = bh / 8.0
    hs = bw / 4.0
    if darkness == 'light':
        m1 = (1, 0, 0, 0)
        m2 = (0, 0, 1, 0)
    elif darkness == 'medium':
        m1 = (1, 0, 0, 1)
        m2 = (1, 0, 0, 1)
    else:
        m1 = (0, 1, 1, 1)
        m2 = (1, 1, 0, 1)

    contours = []
    for l, m in [(bl, m1), (bl + 2 * hs, m2)]:
        for b in frange(bb, bt, 2 * vs):
            if m[0]:
                contours.append(rect(l, b + vs, l + hs, b + 2 * vs))
            if m[1]:
                contours.append(rect(l + hs, b + vs, l + 2 * hs, b + 2 * vs))
            if m[2]:
                contours.append(rect(l, b, l + hs, b + vs))
            if m[3]:
                contours.append(rect(l + hs, b, l + 2 * hs, b + vs))
    return contours

def block_quadrant(ul, ur, ll, lr):
    contours = []
    if ul:
        contours.append(rect(bl, bmv, bmh, bt))
    if ur:
        contours.append(rect(bmh, bmv, br, bt))
    if ll:
        contours.append(rect(bl, bb, bmh, bmv))
    if lr:
        contours.append(rect(bmh, bb, br, bmv))
    return contours

addchar(font, 0x2580, [rect(bl, bmv, br, bt)])
addchar(font, 0x2581, [rect(bl, bb, br, bb + bh * 1.0/8.0)])
addchar(font, 0x2582, [rect(bl, bb, br, bb + bh * 2.0/8.0)])
addchar(font, 0x2583, [rect(bl, bb, br, bb + bh * 3.0/8.0)])
addchar(font, 0x2584, [rect(bl, bb, br, bb + bh * 4.0/8.0)])
addchar(font, 0x2585, [rect(bl, bb, br, bb + bh * 5.0/8.0)])
addchar(font, 0x2586, [rect(bl, bb, br, bb + bh * 6.0/8.0)])
addchar(font, 0x2587, [rect(bl, bb, br, bb + bh * 7.0/8.0)])
addchar(font, 0x2588, [rect(bl, bb, br, bb + bh * 8.0/8.0)])
addchar(font, 0x2589, [rect(bl, bb, bl + bw * 7.0/8.0, bt)])
addchar(font, 0x258A, [rect(bl, bb, bl + bw * 6.0/8.0, bt)])
addchar(font, 0x258B, [rect(bl, bb, bl + bw * 5.0/8.0, bt)])
addchar(font, 0x258C, [rect(bl, bb, bl + bw * 4.0/8.0, bt)])
addchar(font, 0x258D, [rect(bl, bb, bl + bw * 3.0/8.0, bt)])
addchar(font, 0x258E, [rect(bl, bb, bl + bw * 2.0/8.0, bt)])
addchar(font, 0x258F, [rect(bl, bb, bl + bw * 1.0/8.0, bt)])
addchar(font, 0x2590, [rect(bmh, bb, br, bt)])
addchar(font, 0x2591, block_shade('light'))
addchar(font, 0x2592, block_shade('medium'))
addchar(font, 0x2593, block_shade('dark'))
addchar(font, 0x2594, [rect(bl, bt - bh * 1.0/8.0, br, bt)])
addchar(font, 0x2595, [rect(br - bw * 1.0/8.0, bb, br, bt)])
addchar(font, 0x2596, block_quadrant(False, False, True,  False))
addchar(font, 0x2597, block_quadrant(False, False, False, True))
addchar(font, 0x2598, block_quadrant(True,  False, False, False))
addchar(font, 0x2599, block_quadrant(True,  False, True,  True))
addchar(font, 0x259A, block_quadrant(True,  False, False, True))
addchar(font, 0x259B, block_quadrant(True,  True,  True,  False))
addchar(font, 0x259C, block_quadrant(True,  True,  False, True))
addchar(font, 0x259D, block_quadrant(False, True,  False, False))
addchar(font, 0x259E, block_quadrant(False, True,  True,  False))
addchar(font, 0x259F, block_quadrant(False, True,  True,  True))

# Geometric Shapes
def geometric_triangle(rotation=0, black=True):
    sw = 46
    xm = 37
    b = bl + (bh - bw + 2 * xm) / 2.0
    t = b + (bw - 2 * xm) * math.sin(math.pi / 3)
    contours = []

    c = fontforge.contour()
    c.moveTo(bl + xm, b)
    c.lineTo(bmh, t)
    c.lineTo(br - xm, b)
    c.closed = True
    contours.append(c)

    if not black:
        xm += sw * math.sqrt(3)
        c = fontforge.contour()
        c.moveTo(bl + xm, b + sw)
        c.lineTo(br - xm, b + sw)
        c.lineTo(bmh, t - 2 * sw)
        c.closed = True
        contours.append(c)

    if rotation:
        cy = (b + t) / 2.0
        rotT = psMat.compose(psMat.translate(-bmh, -cy),
               psMat.compose(psMat.rotate(rotation),
                             psMat.translate(bmh, cy)))
        for c in contours:
            c.transform(rotT)
    return contours

addchar(font, 0x25B4, geometric_triangle(0, True))
addchar(font, 0x25B5, geometric_triangle(0, False))
addchar(font, 0x25B8, geometric_triangle(-math.pi / 2, True))
addchar(font, 0x25B9, geometric_triangle(-math.pi / 2, False))
addchar(font, 0x25BE, geometric_triangle(math.pi, True))
addchar(font, 0x25BF, geometric_triangle(math.pi, False))
addchar(font, 0x25C2, geometric_triangle(math.pi / 2, True))
addchar(font, 0x25C3, geometric_triangle(math.pi / 2, False))

# Braille Patterns
def braille_pattern(number):
    vs = bh / 8.0
    hs = bw / 4.0
    ls = list(frange(bl + hs / 2.0, br, 2 * hs))
    bs = list(frange(bb + vs / 2.0, bt, 2 * vs))
    contours = []

    if number & 1:
        contours.append(rect(ls[0], bs[3], ls[0] + hs, bs[3] + vs))
    if number & 2:
        contours.append(rect(ls[0], bs[2], ls[0] + hs, bs[2] + vs))
    if number & 4:
        contours.append(rect(ls[0], bs[1], ls[0] + hs, bs[1] + vs))
    if number & 8:
        contours.append(rect(ls[1], bs[3], ls[1] + hs, bs[3] + vs))
    if number & 16:
        contours.append(rect(ls[1], bs[2], ls[1] + hs, bs[2] + vs))
    if number & 32:
        contours.append(rect(ls[1], bs[1], ls[1] + hs, bs[1] + vs))
    if number & 64:
        contours.append(rect(ls[0], bs[0], ls[0] + hs, bs[0] + vs))
    if number & 128:
        contours.append(rect(ls[1], bs[0], ls[1] + hs, bs[0] + vs))
    return contours

for n in range(256):
    addchar(font, 0x2800 + n, braille_pattern(n))

# Powerline Symbols
def powerline_triangle(xref=False):
    c = fontforge.contour()
    c.moveTo(bl, bt)
    c.lineTo(br, bmv)
    c.lineTo(bl, bb)
    c.closed = True
    if xref:
        c.transform(xrefT)
    return [c]

def powerline_angle(xref=False):
    t = math.atan2(bmv - bb, bw)
    dx = swl2 / math.sin(t)
    dy = swl2 / math.cos(t)

    c = fontforge.contour()
    c.moveTo(bl, bt)
    c.lineTo(bl + dx, bt)
    c.lineTo(br, bmv + dy)
    c.lineTo(br, bmv - dy)
    c.lineTo(bl + dx, bb)
    c.lineTo(bl, bb)
    c.lineTo(bl, bb + dy)
    c.lineTo(br - dx, bmv)
    c.lineTo(bl, bt - dy)
    c.closed = True
    if xref:
        c.transform(xrefT)
    return [c]

addchar(font, 0xE0B0, powerline_triangle(False))
addchar(font, 0xE0B1, powerline_angle(False))
addchar(font, 0xE0B2, powerline_triangle(True))
addchar(font, 0xE0B3, powerline_angle(True))

font.generate('ReplaceParts.ttf', '', ('opentype', 'PfEd-lookups', 'TeX-table'))
