from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def stack_tamil_sinhala(
    tamil_font_path,
    sinhala_font_path,
    output_font_path,
    char_map,
    vertical_spacing_ratio=0.1,
):
    # Load the Tamil and Sinhala fonts
    tamil_font = TTFont(tamil_font_path)
    sinhala_font = TTFont(sinhala_font_path)

    # Create a new font based on the Tamil font
    new_font = TTFont(tamil_font_path)

    # Get glyph sets
    tamil_glyf = tamil_font['glyf']
    sinhala_glyf = sinhala_font['glyf']
    new_glyf = new_font['glyf']

    tamil_cmap = tamil_font.getBestCmap()
    sinhala_cmap = sinhala_font.getBestCmap()

    # Get the glyph order from the Tamil font
    glyph_order = tamil_font.getGlyphOrder()

    # Dictionary to store new glyph metrics
    new_glyph_metrics = {}

    # Iterate through the character map
    for tamil_char, sinhala_unicode in char_map.items():
        # Handle single and multi-character strings
        if len(tamil_char) == 1:
            tamil_unicode = ord(tamil_char)
        else:
            # For multi-character strings, check if they are in cmap
            tamil_unicode = None
            for char in tamil_char:
                if ord(char) in tamil_cmap:
                    tamil_unicode = ord(char)
                    break

        if (
            tamil_unicode is not None
            and tamil_unicode in tamil_cmap
            and sinhala_unicode in sinhala_cmap
        ):
            tamil_glyph_name = tamil_cmap[tamil_unicode]
            sinhala_glyph_name = sinhala_cmap[sinhala_unicode]

            # Create a new glyph
            pen = TTGlyphPen(None)

            # Get Tamil glyph
            tamil_glyph = tamil_glyf[tamil_glyph_name]

            # Get Sinhala glyph
            sinhala_glyph = sinhala_glyf[sinhala_glyph_name]

            # Check if both glyphs have contours
            if (
                hasattr(tamil_glyph, 'numberOfContours')
                and tamil_glyph.numberOfContours > 0
                and hasattr(sinhala_glyph, 'numberOfContours')
                and sinhala_glyph.numberOfContours > 0
            ):
                # Calculate scaling factor and vertical spacing
                tamil_height = tamil_glyph.yMax - tamil_glyph.yMin
                sinhala_height = sinhala_glyph.yMax - sinhala_glyph.yMin
                total_height = tamil_height + (
                    sinhala_height * 0.7
                )  # Adjust for smaller Sinhala
                scale_factor = tamil_height / (
                    total_height * (1 + vertical_spacing_ratio)
                )
                sinhala_scale_factor = (
                    scale_factor * 0.7
                )  # 70% of the original scale factor

                vertical_spacing = (
                    tamil_height * vertical_spacing_ratio * scale_factor
                )

                # Calculate horizontal offsets for center alignment
                tamil_width = tamil_glyph.xMax - tamil_glyph.xMin
                sinhala_width = sinhala_glyph.xMax - sinhala_glyph.xMin
                max_width = max(
                    tamil_width * scale_factor,
                    sinhala_width * sinhala_scale_factor,
                )
                tamil_offset = (max_width - tamil_width * scale_factor) / 2
                sinhala_offset = (
                    max_width - sinhala_width * sinhala_scale_factor
                ) / 2

                # Add contours from the Tamil glyph (scaled and centered)
                for i, end_pt in enumerate(tamil_glyph.endPtsOfContours):
                    start = (
                        0
                        if i == 0
                        else tamil_glyph.endPtsOfContours[i - 1] + 1
                    )
                    for j in range(start, end_pt + 1):
                        x, y = tamil_glyph.coordinates[j]
                        if j == start:
                            pen.moveTo(
                                (
                                    x * scale_factor + tamil_offset,
                                    y * scale_factor,
                                )
                            )
                        else:
                            pen.lineTo(
                                (
                                    x * scale_factor + tamil_offset,
                                    y * scale_factor,
                                )
                            )
                    pen.closePath()

                # Add contours from the Sinhala glyph (scaled smaller, moved
                # up, and centered)
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
                                    x * sinhala_scale_factor + sinhala_offset,
                                    y * sinhala_scale_factor
                                    + tamil_height * scale_factor
                                    + vertical_spacing
                                    + (
                                        sinhala_height
                                        * (
                                            scale_factor
                                            - sinhala_scale_factor
                                        )
                                        / 2
                                    ),
                                )
                            )
                        else:
                            pen.lineTo(
                                (
                                    x * sinhala_scale_factor + sinhala_offset,
                                    y * sinhala_scale_factor
                                    + tamil_height * scale_factor
                                    + vertical_spacing
                                    + (
                                        sinhala_height
                                        * (
                                            scale_factor
                                            - sinhala_scale_factor
                                        )
                                        / 2
                                    ),
                                )
                            )
                    pen.closePath()

                # Create the new glyph
                new_glyph = pen.glyph()

                # Calculate xMin and xMax from the new glyph's coordinates
                x_coords = [pt[0] for pt in pen.points if pt]
                y_coords = [pt[1] for pt in pen.points if pt]
                if x_coords and y_coords:
                    xMin = min(x_coords)
                    xMax = max(x_coords)
                    yMin = min(y_coords)
                    yMax = max(y_coords)
                else:
                    # Fallback to original glyph metrics if no coordinates
                    xMin = tamil_glyph.xMin
                    xMax = tamil_glyph.xMax
                    yMin = tamil_glyph.yMin
                    yMax = tamil_glyph.yMax

                # Store the new glyph metrics
                new_glyph_metrics[tamil_glyph_name] = {
                    'xMin': xMin,
                    'xMax': xMax,
                    'yMin': yMin,
                    'yMax': yMax,
                }

                # Update the glyph in the new font
                new_glyf[tamil_glyph_name] = new_glyph

    # Update horizontal metrics
    tamil_hmtx = tamil_font['hmtx']
    new_hmtx = new_font['hmtx']
    for glyph_name in glyph_order:
        if glyph_name in new_glyph_metrics:
            # If the glyph was modified, use its new metrics
            advance, _ = tamil_hmtx[glyph_name]
            metrics = new_glyph_metrics[glyph_name]
            new_hmtx[glyph_name] = (
                max(advance, metrics['xMax']),
                metrics['xMin'],
            )
        else:
            # If the glyph wasn't modified, copy the original metrics
            new_hmtx[glyph_name] = tamil_hmtx[glyph_name]

    # Update name table
    name = new_font['name']
    name.setName(f"Tamil-Sinhala Stacked Font", 1, 3, 1, 1033)  # Family name
    name.setName("Regular", 2, 3, 1, 1033)  # Subfamily name
    name.setName(
        f"Tamil-Sinhala Stacked Font Regular", 4, 3, 1, 1033
    )  # Full name
    name.setName(
        f"TamilSinhalaStackedFont-Regular", 6, 3, 1, 1033
    )  # PostScript name

    # Save the new font
    new_font.save(output_font_path)
    print(f"Stacked Tamil-Sinhala font saved as {output_font_path}")


if __name__ == "__main__":
    import os

    # Example character mapping (Tamil to Sinhala Unicode)
    char_map = {
        # Consonants
        'க': 0x0D9A,  # Sinhala ක
        'ங': 0x0D9E,  # Sinhala ඞ
        'ச': 0x0DA0,  # Sinhala ච
        'ஜ': 0x0DA2,  # Sinhala ජ
        'ஞ': 0x0DA4,  # Sinhala ඤ
        'ட': 0x0DA7,  # Sinhala ට
        'ண': 0x0DAB,  # Sinhala ණ
        'த': 0x0DAC,  # Sinhala ත
        'ந': 0x0DB1,  # Sinhala න
        'ன': 0x0DB1,  # Sinhala න (closest approximation)
        'ப': 0x0DB4,  # Sinhala ප
        'ம': 0x0DB8,  # Sinhala ම
        'ய': 0x0DBA,  # Sinhala ය
        'ர': 0x0DBB,  # Sinhala ර
        'ற': 0x0DBB,  # Sinhala ර (closest approximation)
        'ல': 0x0DBD,  # Sinhala ල
        'ள': 0x0DC5,  # Sinhala ළ
        'ழ': 0x0DBD,  # Sinhala ල (closest approximation)
        'வ': 0x0DC0,  # Sinhala ව
        'ஶ': 0x0DC1,  # Sinhala ශ
        'ஷ': 0x0DC2,  # Sinhala ෂ
        'ஸ': 0x0DC3,  # Sinhala ස
        'ஹ': 0x0DC4,  # Sinhala හ
        # Vowels
        'அ': 0x0D85,  # Sinhala අ
        'ஆ': 0x0D86,  # Sinhala ආ
        'இ': 0x0D89,  # Sinhala ඉ
        'ஈ': 0x0D8A,  # Sinhala ඊ
        'உ': 0x0D8B,  # Sinhala උ
        'ஊ': 0x0D8C,  # Sinhala ඌ
        'எ': 0x0D91,  # Sinhala එ
        'ஏ': 0x0D92,  # Sinhala ඒ
        'ஐ': 0x0D93,  # Sinhala ඓ
        'ஒ': 0x0D94,  # Sinhala ඔ
        'ஓ': 0x0D95,  # Sinhala ඕ
        'ஔ': 0x0D96,  # Sinhala ඖ
        # Vowel Markers
        'ா': 0x0DCF,  # Sinhala ා
        'ி': 0x0DD2,  # Sinhala ි
        'ீ': 0x0DD3,  # Sinhala ී
        'ு': 0x0DD4,  # Sinhala ු
        'ூ': 0x0DD6,  # Sinhala ූ
        'ெ': 0x0DD9,  # Sinhala ෙ
        'ே': 0x0DDA,  # Sinhala ේ
        'ை': 0x0DDB,  # Sinhala ෛ
        'ொ': 0x0DDC,  # Sinhala ො
        'ோ': 0x0DDD,  # Sinhala ෝ
        'ௌ': 0x0DDE,  # Sinhala ෞ
        # Special Characters
        'ஃ': 0x0D83,  # Sinhala ඃ (closest approximation)
        '்': 0x0DCA,  # Sinhala ් (virama)
        # Grantha Characters
        'க்ஷ': 0x0D9A,  # Sinhala ක (closest approximation)
        'ஸ்ரீ': 0x0DC1 + 0x0DCA + 0x0DBB + 0x0DD3,  # Sinhala ශ්රී
        # Numerals
        '௧': 0x0DE7,  # Sinhala ෧
        '௨': 0x0DE8,  # Sinhala ෨
        '௩': 0x0DE9,  # Sinhala ෩
        '௪': 0x0DEA,  # Sinhala ෪
        '௫': 0x0DEB,  # Sinhala ෫
        '௬': 0x0DEC,  # Sinhala ෬
        '௭': 0x0DED,  # Sinhala ෭
        '௮': 0x0DEE,  # Sinhala ෮
        '௯': 0x0DEF,  # Sinhala ෯
        '௰': 0x0DF0,  # Sinhala ෰ (closest approximation)
        '௱': 0x0DF1,  # Sinhala ෱ (closest approximation)
        '௲': 0x0DF2,  # Sinhala ෲ (closest approximation)
        # Other Symbols
        '௳': 0x0DF3,  # Sinhala ෳ (closest approximation)
        '௴': 0x0DF4,  # Sinhala ෴
        '௵': 0x0DF4,  # Sinhala ෴ (closest approximation)
        '௶': 0x0DF4,  # Sinhala ෴ (closest approximation)
        '௷': 0x0DF4,  # Sinhala ෴ (closest approximation)
        '௸': 0x0DF4,  # Sinhala ෴ (closest approximation)
        '௹': 0x0DF4,  # Sinhala ෴ (closest approximation)
        '௺': 0x0DF4,  # Sinhala ෴ (closest approximation)
        # More
        'லி': 'ළි',
        'கு': 'කු',
    }

    tamil_font_path = os.path.join(
        'fonts', 'Noto_Sans_Tamil', 'static', 'NotoSansTamil-Regular.ttf'
    )
    sinhala_font_path = os.path.join(
        'fonts', 'Noto_Sans_Sinhala', 'static', 'NotoSansSinhala-Regular.ttf'
    )
    stack_tamil_sinhala(
        tamil_font_path,
        sinhala_font_path,
        "TamilSinhalaStackedFont.ttf",
        char_map,
        vertical_spacing_ratio=0.0,
    )
