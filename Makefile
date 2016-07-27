.PHONY: all clean

TARGETS = mig-mono-regular.ttf mig-mono-bold.ttf UTF-8-MIG.gz

all: $(TARGETS)

clean:
	rm -f $(TARGETS) ReplaceParts.ttf

ReplaceParts.ttf:
	fontforge -script replaceparts_generator.py

mig-mono-regular.ttf: ReplaceParts.ttf
	fontforge -script mig_mono_generator.py

mig-mono-bold.ttf: ReplaceParts.ttf
	fontforge -script mig_mono_generator.py --bold

UTF-8-MIG.gz: mig-mono-regular.ttf
	zcat source/UTF-8.gz | sed '/^END CHARMAP/q' > UTF-8-MIG
	python charmap_width.py >> UTF-8-MIG
	gzip UTF-8-MIG
