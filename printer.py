import argparse
from escpos.printer import File


parser = argparse.ArgumentParser(description=" ")
parser.add_argument('total_price', metavar='total_price', help='')
parser.add_argument('-owner_mobile_number', '--owner_mobile_number', metavar='owner_mobile_number', help='')
parser.add_argument('-owner_id', '--owner_id', metavar='owner_id', help='')
parser.add_argument('-user_id', '--user_id', metavar='user_id', help='')
parser.add_argument('-datetime', '--datetime', metavar='datetime', help='')


def main(total_price, owner_mobile_number, owner_id, user_id, datetime):
    try:            
        printer = File(devfile='/dev/usb/lp0')
        printer.profile.media['width']['pixels'] = 575
        printer.image("images/logo-text-small.png", center=True)
        # printer.image("images/logo-text-small.png")
        printer.set(align=u'center')
        printer.text("\n")
        printer.text('Your ID: ' + str(user_id) + "\n")
        printer.text(total_price + " Toman" + "\n")
        printer.qr(total_price, size=12, center=True)
        # printer.qr(str(self.total_price), size=8)
        printer.text('Support: ' + owner_mobile_number + "\n")
        printer.text('ID: ' + str(owner_id) + "\n")
        printer.text("farazist.ir" + "\n")
        printer.text(datetime)
        printer.cut()
        print("print receipt")
    except Exception as e:
        print("error:", e)

if __name__ == "__main__":
    main(**vars(parser.parse_args()))