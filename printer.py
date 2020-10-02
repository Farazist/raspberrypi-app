import argparse
from escpos.printer import File


parser = argparse.ArgumentParser(description=" ")
parser.add_argument('total_price', metavar='total_price', help='')
parser.add_argument('-datetime', '--datetime', metavar='datetime', help='')


def main(total_price, datetime):
    try:            
        printer = File(devfile='/dev/usb/lp0')
        printer.profile.media['width']['pixels'] = 575
        printer.image("images/logo-text-small.png", center=True)
        # printer.image("images/logo-text-small.png")
        printer.set(align=u'center')
        printer.text("\n")
        # printer.text('Your ID: ' + str(user_id) + "\n")
        printer.text(total_price + " Toman" + "\n")
        # printer.qr(total_price, size=12, center=True)
        # printer.text('Support: ' + owner_mobile_number + "\n")
        # printer.text('ID: ' + str(owner_id) + "\n")
        printer.text("farazist.ir" + "\n")
        printer.text(datetime)
        printer.cut()
        print("print receipt")
    except Exception as e:
        print("error:", e)

if __name__ == "__main__":
    main(**vars(parser.parse_args()))