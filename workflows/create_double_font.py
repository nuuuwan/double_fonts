from double_fonts import DoubleFont, Font


def main():
    font1 = Font(name="Arial")
    font2 = Font(name="Times New Roman")
    DoubleFont(font1, font2).build("Arial-Times.ttf")


if __name__ == "__main__":
    main()
