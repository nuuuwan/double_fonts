from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def stack_english_sinhala(
    input_font_path, output_font_path, char_map, vertical_spacing_ratio=0.1
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

    # Iterate through the character map
    for english_char, sinhala_unicode in char_map.items():
        english_unicode = ord(english_char)

        if english_unicode in cmap and sinhala_unicode in cmap:
            english_glyph_name = cmap[english_unicode]
            sinhala_glyph_name = cmap[sinhala_unicode]

            # Create a new glyph
            pen = TTGlyphPen(None)

            # Get English glyph
            english_glyph = glyf[english_glyph_name]

            # Get Sinhala glyph
            sinhala_glyph = glyf[sinhala_glyph_name]

            # Check if both glyphs have contours
            if (
                hasattr(english_glyph, 'numberOfContours')
                and english_glyph.numberOfContours > 0
                and hasattr(sinhala_glyph, 'numberOfContours')
                and sinhala_glyph.numberOfContours > 0
            ):
                # Calculate scaling factor and vertical spacing
                english_height = english_glyph.yMax - english_glyph.yMin
                sinhala_height = sinhala_glyph.yMax - sinhala_glyph.yMin
                total_height = english_height + sinhala_height
                scale_factor = english_height / (
                    total_height * (1 + vertical_spacing_ratio)
                )
                vertical_spacing = (
                    english_height * vertical_spacing_ratio * scale_factor
                )

                # Add contours from the English glyph (scaled)
                for i, end_pt in enumerate(english_glyph.endPtsOfContours):
                    start = (
                        0
                        if i == 0
                        else english_glyph.endPtsOfContours[i - 1] + 1
                    )
                    for j in range(start, end_pt + 1):
                        x, y = english_glyph.coordinates[j]
                        if j == start:
                            pen.moveTo((x * scale_factor, y * scale_factor))
                        else:
                            pen.lineTo((x * scale_factor, y * scale_factor))
                    pen.closePath()

                # Add contours from the Sinhala glyph (scaled and moved up)
                for i, end_pt in enumerate(sinhala_glyph.endPtsOfContours):
                    start = (
                        0
                        if i == 0
                        else sinhala_glyph.endPtsOfContours[i - 1] + 1
                    )
                    for j in range(start, end_pt + 1):
                        x, y = sinhala_glyph.coordinates[j]
                        if j == start:
                            pen.moveTo(
                                (
                                    x * scale_factor,
                                    y * scale_factor
                                    + english_height * scale_factor
                                    + vertical_spacing,
                                )
                            )
                        else:
                            pen.lineTo(
                                (
                                    x * scale_factor,
                                    y * scale_factor
                                    + english_height * scale_factor
                                    + vertical_spacing,
                                )
                            )
                    pen.closePath()

                # Create the new glyph
                new_glyph = pen.glyph()

                # Update the glyph in the new font
                new_glyf[english_glyph_name] = new_glyph

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
        f"English-Sinhala Stacked Font", 1, 3, 1, 1033
    )  # Family name
    name.setName("Regular", 2, 3, 1, 1033)  # Subfamily name
    name.setName(
        f"English-Sinhala Stacked Font Regular", 4, 3, 1, 1033
    )  # Full name
    name.setName(
        f"EnglishSinhalaStackedFont-Regular", 6, 3, 1, 1033
    )  # PostScript name

    # Save the new font
    new_font.save(output_font_path)
    print(f"Stacked English-Sinhala font saved as {output_font_path}")


if __name__ == "__main__":
    import os

    # Example character mapping (English to Sinhala Unicode)
    char_map = {
        'b': 0x0DB6,  # බ
        'c': 0x0DA0,  # ච
        'd': 0x0DAF,  # ද
        'f': 0x0DC6,  # ෆ
        'g': 0x0D9C,  # ග
        'h': 0x0DC4,  # හ
        'j': 0x0DA2,  # ජ
        'k': 0x0D9A,  # ක
        'l': 0x0DBD,  # ල
        'm': 0x0DB8,  # ම
        'n': 0x0DB1,  # න
        'p': 0x0DB4,  # ප
        'q': 0x0D9A,  # ක (closest approximation)
        'r': 0x0DBB,  # ර
        's': 0x0DC3,  # ස
        't': 0x0DAD,  # ත
        'v': 0x0DC0,  # ව
        'w': 0x0DC0,  # ව (same as 'v' in Sinhala)
        'x': 0x0D9A,  # ක්ස (represented by ක for simplicity)
        'y': 0x0DBA,  # ය
        'z': 0x0DC3,  # ස (closest approximation)
    }

    new_char_map = {}
    for k, v in char_map.items():
        new_char_map[k] = v
        new_char_map[k.upper()] = v

    font1_path = os.path.join('fonts', 'Bhashitha-Sans.ttf')
    stack_english_sinhala(
        font1_path,
        "EnglishSinhalaStackedFont.ttf",
        new_char_map,
        vertical_spacing_ratio=0.1,
    )
