import os

from PIL import Image, ImageDraw, ImageFont


def create_text_image():
    # Parameters
    # text = "ඉක්මන් දුඹුරු හිවලෙකු කම්මැලි බල්ලා ට උඩින් පනියි"
    text = "விரைவான பழுப்பு நரி சோம்பேறி நாய் மீது குதிக்கிறது"
    # text = "The quick brown fox jumps over the lazy dog"
    # font_path = "TamilSinhalaStackedFont.ttf"  # Replace with the path to
    # your desired font file
    font_path = os.path.join('TamilSinhalaStackedFont.ttf')
    font_size = 48
    image_size = (1600, 900)  # Width, Height
    text_color = (0, 0, 0)
    bg_color = (255, 255, 255)

    # Create a new image with the specified background color
    image = Image.new('RGB', image_size, bg_color)

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Load the font
    font = ImageFont.truetype(font_path, font_size)

    # Get the size of the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate the position to center the text
    position = (
        (image_size[0] - text_width) / 2,
        (image_size[1] - text_height) / 2,
    )

    # Draw the text on the image
    draw.text(position, text, font=font, fill=text_color)

    # Save the image
    output_path = "test_image.png"
    image.save(output_path)
    print(f"Image saved as {output_path}")

    # Optionally, display the image
    image.show()


if __name__ == "__main__":
    create_text_image()
