from escpos.printer import Usb

from typing import Optional
import configparser

CHAR_WIDTH = 42

class RecieptPrinter:
    def __init__(self, dry):
        self.dry = dry
        if not self.dry:
            self.p = Usb(0x04b8, 0x0202)
        else:
            self.p = None

    def set_with_default(
        self,
        align: Optional[str] = "left",
        font: Optional[str] = "a",
        bold: Optional[bool] = False,
        underline: Optional[int] = 0,
        width: Optional[int] = 1,
        height: Optional[int] = 1,
        density: Optional[int] = 9,
        invert: Optional[bool] = False,
        smooth: Optional[bool] = False,
        flip: Optional[bool] = False,
        double_width: Optional[bool] = False,
        double_height: Optional[bool] = False,
        custom_size: Optional[bool] = False,
    ):
        if not self.dry:
            self.p.set_with_default(align, font, bold, underline, width, height,
                  density, invert, smooth, flip,
                  double_width, double_height, custom_size)

    def set(
        self,
        align: Optional[str] = None,
        font: Optional[str] = None,
        bold: Optional[bool] = None,
        underline: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        density: Optional[int] = None,
        invert: Optional[bool] = None,
        smooth: Optional[bool] = None,
        flip: Optional[bool] = None,
        normal_textsize: Optional[bool] = None,
        double_width: Optional[bool] = None,
        double_height: Optional[bool] = None,
        custom_size: Optional[bool] = None,
    ):
        if not self.dry:
            self.p.set(align, font, bold, underline, width, height,
                  density, invert, smooth, flip, normal_textsize,
                  double_width, double_height, custom_size)
    

    def text(self, string, wrap=False):
        if not wrap and len(string) > CHAR_WIDTH:
            string = string[:CHAR_WIDTH]
        if not self.dry:
            self.p.text(f"{string}\n")
        print(string)

    def cut(self):
        if not self.dry:
            self.p.cut()
        print("Cutting...")
