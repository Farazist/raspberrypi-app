import argparse
from escpos.printer import Usb

parser = argparse.ArgumentParser(description=" ")

parser.add_argument('total_price', metavar='total_price',
                    help='')
parser.add_argument('-mobile_number', '--mobile_number', metavar='mobile_number',
                    help='')
parser.add_argument('-datetime', '--datetime', metavar='datetime',
                    help='')

d = parser.get_default

def main(total_price, mobile_number, datetime):
    try:            
        printer = Usb(idVendor=0x0416, idProduct=0x5011, timeout=0, in_ep=0x81, out_ep=0x03)
        printer.profile.media['width']['pixels'] = 575
        printer.image("images/logo-text-small.png", center=True)
        # printer.image("images/logo-text-small.png")
        printer.set(align=u'center')
        printer.text("Farazist" + "\n")
        printer.text(total_price + " Toman" + "\n")
        printer.qr(total_price, size=8, center=True)
        # printer.qr(str(self.total_price), size=8)
        printer.text(mobile_number + "\n")
        printer.text("farazist.ir" + "\n")
        printer.text(datetime)
        printer.cut()
        print("print receipt")
    except Exception as e:
        print("error:", e)

if __name__ == "__main__":
    main(**vars(parser.parse_args()))