#!/usr/bin/fontforge -script
import sys
import os
import fontforge
import psMat

def copy_glyphs(srcfont, dstfont):
    for glyph in list(srcfont.selection.byGlyphs):
        srcfont.selection.select(glyph.glyphname)
        srcfont.copy()
        dstfont.createChar(glyph.unicode, glyph.glyphname)
        dstfont.selection.select(glyph.glyphname)
        dstfont.paste()

fontname = ('MiG Mono', 'MiG Mono Regular', 'mig-mono-regular', 'Regular')
os2_panose = (2, 11, 5, 9, 2, 2, 3, 2, 2, 7)
migfile = 'mig-mono-regular.ttf'
mgenfile = 'source/mgenplus-1m-regular.ttf'
incfile = 'source/Inconsolata-Regular.ttf'
octfile = 'source/octicons.ttf'
rpfile = 'ReplaceParts.ttf'

for arg in sys.argv[1:]:
    if arg == '--bold':
        fontname = ('MiG Mono', 'MiG Mono Bold', 'mig-mono-bold', 'Bold')
        migfile = 'mig-mono-bold.ttf'
        os2_panose = (2, 11, 8, 9, 2, 2, 3, 2, 2, 7)
        mgenfile = 'source/mgenplus-1m-bold.ttf'
        incfile = 'source/Inconsolata-Bold.ttf'
for srcfile in (mgenfile, incfile, octfile, rpfile):
    if not os.path.exists(srcfile):
        print(srcfile, 'not found', file=sys.stderr)
        sys.exit(1)


fontforge.setPrefs('ClearInstrsBigChanges', 0)
fontforge.setPrefs('CopyTTFInstrs', 1)
fontforge.setPrefs('CoverageFormatsAllowed', 1)

fMig = fontforge.font()
fMig.familyname = fontname[0]
fMig.fullname = fontname[1]
fMig.fontname = fontname[2]
fMig.weight = fontname[3]
fMig.version = '1.000.20160727'
fMig.copyright = """\
[MiG Mono]
Copyright (c) 2016 cions (gh.cions@gmail.com)

[Inconsolata]
Copyright (c) 2006-2012 Raph Levien (firstname.lastname@gmail.com)
Copyright (c) 2011-2012 Cyreal (cyreal.org)

[Mgen+]
Copyright (c) 2014-2015 MM (http://jikasei.me/)

[Source Han Sans]
Copyright (c) 2014, 2015 Adobe Systems Incorporated (http://www.adobe.com/), with Reserved Font Name 'Source'.

[M+ OUTLINE FONTS]
Copyright(c) 2015 M+ FONTS PROJECT

[Octicons]
Copyright (c) 2012-2016 Github, Inc.
"""
fMig.sfnt_names = (('English (US)', 'SubFamily', fontname[3]),
                   ('English (US)', 'Copyright', fMig.copyright),
                   ('English (US)', 'License', open('LICENSE').read()),
                   ('English (US)', 'License URL', 'http://scripts.sil.org/OFL'))

fMig.ascent = 840
fMig.descent = 184
fMig.em = fMig.ascent + fMig.descent
fMig.os2_winascent = 880
fMig.os2_winascent_add = 0
fMig.os2_windescent = 234
fMig.os2_windescent_add = 0
fMig.os2_typoascent = fMig.ascent
fMig.os2_typoascent_add = 0
fMig.os2_typodescent = -fMig.descent
fMig.os2_typodescent_add = 0
fMig.os2_typolinegap = 90
fMig.hhea_ascent = fMig.os2_winascent
fMig.hhea_ascent_add = 0
fMig.hhea_descent = -fMig.os2_windescent
fMig.hhea_descent_add = 0
fMig.hhea_linegap = 0

fMig.os2_panose = os2_panose
fMig.os2_unicoderanges = (-536870145, 2051538411, 18, 0)
fMig.os2_codepages = (1074921887, -539557888)

fMig.hasvmetrics = True
fMig.head_optimized_for_cleartype = True

# Merge Mgen+
fMgen = fontforge.open(mgenfile)

fMgen.selection.all()
copy_glyphs(fMgen, fMig)

fMig.sfnt_names += tuple(x for x in fMgen.sfnt_names
    if x[1] in ('Trademark', 'Designer', 'Descriptor'))

fMig.importLookups(fMgen, fMgen.gsub_lookups)
fMig.importLookups(fMgen, fMgen.gpos_lookups)

fMgen.close()

fMig.selection.all()
for glyph in fMig.selection.byGlyphs:
    width = glyph.width
    glyph.transform(
        psMat.compose(psMat.translate(-width / 2.0, 0),
        psMat.compose(psMat.scale(0.95, 0.95),
                      psMat.translate(width / 2.0, 0))))
    glyph.width = width

fMig.selection.select(('unicode',), 0xFF5E)
fMig.transform(psMat.translate(0, 190))

# Merge Inconsolata
fInc = fontforge.open(incfile)

fInc.em = fMig.em

fInc.selection.select(('unicode', 'ranges'), 0x20, 0x7E)
copy_glyphs(fInc, fMig)

fInc.close()

fMig.selection.select(('unicode',), '(', ')', '{', '}')
fMig.transform(psMat.translate(0, 90))

fMig.selection.select(('unicode',), '[', ']')
fMig.transform(psMat.translate(0, 15))

fMig.selection.select(('unicode',), '~')
fMig.transform(psMat.translate(0, 120))

# Merge Octicions
fOct = fontforge.open(octfile)

fOct.em = fMig.em

preserve_size = [
    0xF03D, 0xF03E, 0xF03F, 0xF040, 0xF044, 0xF052, 0xF053, 0xF05A, 0xF05B,
    0xF05D, 0xF05E, 0xF05F, 0xF070, 0xF071, 0xF078, 0xF081, 0xF085, 0xF09A,
    0xF09F, 0xF0A0, 0xF0A1, 0xF0CA, 0xF103, 0xF104
]

for glyph in fOct.glyphs():
    if glyph.unicode not in preserve_size:
        glyph.transform(psMat.scale(0.8, 0.8))
    bbox = glyph.boundingBox()
    xcenter = (bbox[0] + bbox[2]) / 2.0
    glyph.transform(psMat.translate(512 - xcenter, 0))
    glyph.width = 1024
    glyph.glyphname = 'octicons_' + glyph.glyphname

fOct.selection.select(('unicode', 'ranges'), 0xF000, 0xF8FF)
copy_glyphs(fOct, fMig)

fOct.close()

# Merge ReplaceParts
fRp = fontforge.open(rpfile)

fRp.selection.all()
copy_glyphs(fRp, fMig)

fRp.close()

# Post Process
fMig.selection.all()
fMig.round()
fMig.addExtrema()
fMig.correctDirection()
fMig.canonicalStart()
fMig.canonicalContours()

for glyph in fMig.selection.byGlyphs:
    glyph.manualHints = False
    glyph.ttinstrs = ()
    glyph.dhints = ()
    glyph.hhints = ()
    glyph.vhints = ()
fMig.autoHint()
fMig.autoInstr()

fMig.os2_capheight = fMig['X'].boundingBox()[3]
fMig.os2_xheight = fMig['x'].boundingBox()[3]

# Generate MiG Mono
fMig.generate(migfile, '', ('opentype', 'PfEd-lookups', 'TeX-table'))
