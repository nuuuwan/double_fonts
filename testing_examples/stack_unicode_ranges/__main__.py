from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def stack_unicode_ranges(
    input_font_path, output_font_path, offset, vertical_spacing_ratio=0.1
):
    # Load the input font
    font = TTFont(input_font_path)

    # Create a new font based on the input font
    new_font = TTFont(input_font_path)

    # Get glyph set
    glyf = font['glyf']
    new_glyf = new_font['glyf']
    cmap = font.getBestCmap()

    # Get the glyph order
    glyph_order = font.getGlyphOrder()

    # Iterate through all characters in the font
    for unicode_value, glyph_name in cmap.items():
        # Check if the offset character exists
        offset_unicode = unicode_value + offset

        if offset_unicode in cmap:
            offset_glyph_name = cmap[offset_unicode]
            # Create a new glyph
            pen = TTGlyphPen(None)

            # Get original glyph
            glyph = glyf[glyph_name]

            # Get offset glyph
            offset_glyph = glyf[offset_glyph_name]

            # Check if both glyphs have contours
            if (
                hasattr(glyph, 'numberOfContours')
                and glyph.numberOfContours > 0
                and hasattr(offset_glyph, 'numberOfContours')
                and offset_glyph.numberOfContours > 0
            ):
                # Calculate scaling factor and vertical spacing
                glyph_height = glyph.yMax - glyph.yMin
                offset_glyph_height = offset_glyph.yMax - offset_glyph.yMin
                total_height = glyph_height + offset_glyph_height
                scale_factor = glyph_height / (
                    total_height * (1 + vertical_spacing_ratio)
                )
                vertical_spacing = (
                    glyph_height * vertical_spacing_ratio * scale_factor
                )

                # Add contours from the original glyph (scaled)
                for i, end_pt in enumerate(glyph.endPtsOfContours):
                    start = 0 if i == 0 else glyph.endPtsOfContours[i - 1] + 1
                    for j in range(start, end_pt + 1):
                        x, y = glyph.coordinates[j]
                        if j == start:
                            pen.moveTo((x * scale_factor, y * scale_factor))
                        else:
                            pen.lineTo((x * scale_factor, y * scale_factor))
                    pen.closePath()

                # Add contours from the offset glyph (scaled and moved up)
                for i, end_pt in enumerate(offset_glyph.endPtsOfContours):
                    start = (
                        0
                        if i == 0
                        else offset_glyph.endPtsOfContours[i - 1] + 1
                    )
                    for j in range(start, end_pt + 1):
                        x, y = offset_glyph.coordinates[j]
                        if j == start:
                            pen.moveTo(
                                (
                                    x * scale_factor,
                                    y * scale_factor
                                    + glyph_height * scale_factor
                                    + vertical_spacing,
                                )
                            )
                        else:
                            pen.lineTo(
                                (
                                    x * scale_factor,
                                    y * scale_factor
                                    + glyph_height * scale_factor
                                    + vertical_spacing,
                                )
                            )
                    pen.closePath()

                # Create the new glyph
                new_glyph = pen.glyph()

                # Update the glyph in the new font
                new_glyf[glyph_name] = new_glyph

    # Update horizontal metrics
    hmtx = font['hmtx']
    new_hmtx = new_font['hmtx']

    for i, glyph_name in enumerate(glyph_order):
        if glyph_name in new_glyf:
            # If the glyph was modified, use its metrics
            advance, lsb = hmtx[glyph_name]
            new_hmtx[glyph_name] = (advance, lsb)
        else:
            # If the glyph wasn't modified, copy the original metrics
            new_hmtx[glyph_name] = hmtx[glyph_name]

    # Update name table
    name = new_font['name']
    name.setName(
        f"Stacked {font.getGlyphOrder()[0]} (Offset {offset})", 1, 3, 1, 1033
    )  # Family name
    name.setName("Regular", 2, 3, 1, 1033)  # Subfamily name
    name.setName(
        f"Stacked {font.getGlyphOrder()[0]} (Offset {offset}) Regular",
        4,
        3,
        1,
        1033,
    )  # Full name
    name.setName(
        f"Stacked{font.getGlyphOrder()[0]}Offset{offset}-Regular",
        6,
        3,
        1,
        1033,
    )  # PostScript name

    # Save the new font
    new_font.save(output_font_path)
    print(f"Stacked font saved as {output_font_path}")


if __name__ == "__main__":
    import os

    font1_path = os.path.join('fonts', 'Bhashitha-Sans.ttf')
    stack_unicode_ranges(
        font1_path,
        "UnicodeStackedFont.ttf",
        offset=3450,
        vertical_spacing_ratio=0.1,
    )
