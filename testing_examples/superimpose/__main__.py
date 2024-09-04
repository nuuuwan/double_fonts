from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def superimpose_fonts(font1_path, font2_path, output_path):
    # Load the input fonts
    font1 = TTFont(font1_path)
    font2 = TTFont(font2_path)

    # Create a new font based on the first font
    new_font = TTFont(font1_path)

    # Get glyph sets
    glyf1 = font1['glyf']
    glyf2 = font2['glyf']
    new_glyf = new_font['glyf']

    # Iterate through glyphs present in both fonts
    common_glyphs = set(glyf1.keys()) & set(glyf2.keys())

    for glyph_name in common_glyphs:
        glyph1 = glyf1[glyph_name]
        glyph2 = glyf2[glyph_name]

        # Create a new glyph
        pen = TTGlyphPen(None)

        # Add contours from glyph1
        if glyph1.numberOfContours > 0:
            for i, end_pt in enumerate(glyph1.endPtsOfContours):
                start = 0 if i == 0 else glyph1.endPtsOfContours[i - 1] + 1
                for j in range(start, end_pt + 1):
                    x, y = glyph1.coordinates[j]
                    if j == start:
                        pen.moveTo((x, y))
                    else:
                        pen.lineTo((x, y))
                pen.closePath()

        # Add contours from glyph2
        if glyph2.numberOfContours > 0:
            for i, end_pt in enumerate(glyph2.endPtsOfContours):
                start = 0 if i == 0 else glyph2.endPtsOfContours[i - 1] + 1
                for j in range(start, end_pt + 1):
                    x, y = glyph2.coordinates[j]
                    if j == start:
                        pen.moveTo((x, y))
                    else:
                        pen.lineTo((x, y))
                pen.closePath()

        # Create the new glyph
        new_glyph = pen.glyph()

        # Update the glyph in the new font
        new_glyf[glyph_name] = new_glyph

    # Update horizontal metrics
    hmtx1 = font1['hmtx']
    hmtx2 = font2['hmtx']
    new_hmtx = new_font['hmtx']

    for glyph_name in common_glyphs:
        # Use the maximum advance width and minimum left side bearing
        advance1, lsb1 = hmtx1[glyph_name]
        advance2, lsb2 = hmtx2[glyph_name]
        new_hmtx[glyph_name] = (max(advance1, advance2), min(lsb1, lsb2))

    # Update name table
    name = new_font['name']
    name.setName(
        f"Superimposed {font1.getGlyphOrder()[0]} + {font2.getGlyphOrder()[0]}",
        1,
        3,
        1,
        1033,
    )  # Family name
    name.setName("Regular", 2, 3, 1, 1033)  # Subfamily name
    name.setName(
        f"Superimposed {font1.getGlyphOrder()[0]} + {font2.getGlyphOrder()[0]} Regular",
        4,
        3,
        1,
        1033,
    )  # Full name
    name.setName(
        f"Superimposed{font1.getGlyphOrder()[0]}{font2.getGlyphOrder()[0]}-Regular",
        6,
        3,
        1,
        1033,
    )  # PostScript name

    # Save the new font
    new_font.save(output_path)
    print(f"Superimposed font saved as {output_path}")


if __name__ == "__main__":
    import os

    superimpose_fonts(
        os.path.join('fonts', 'Noto_Sans', 'static', 'NotoSans-Medium.ttf'),
        os.path.join('fonts', 'Sevillana', 'Sevillana-Regular.ttf'),
        "SuperimposedFont.ttf",
    )
