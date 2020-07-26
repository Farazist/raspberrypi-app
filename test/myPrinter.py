from escpos.printer import File, Usb
p = File(devfile='/dev/usb/lp2')
# p = Usb(0x067b,0x2305, in_ep=0x66, out_ep=0x01)
p.text("some text\n")
p.text("some text\n")
p.text("some text\n")
p.text("some text\n")
# p.text("تست\n")


# # import usb.core
# # import usb.util

# # # find the USB device
# # for device in usb.core.find(find_all=True):
# #     print(device)


# from escpos.printer import Usb, Network

# # printer = Network("")
# printer = Usb(idVendor=0x067b, idProduct=0x2305, timeout=0, in_ep=0x80, out_ep=0x01)
# # printer.open()
# # printer.set(codepage='pc864')
# # printer.profile.media['width']['pixels'] = 575
# # printer.image("images/logo-text-small.png", center=True)
# # printer.image("images/logo-text-small.png")
# # printer.set(align=u'center')
# printer.text("Far" + "\n\n")
# # printer.text(total_price + " Toman" + "\n")
# # printer.qr(total_price, size=8, center=True)
# # printer.qr(str(self.total_price), size=8)
# # printer.text(mobile_number + "\n")
# printer.text("farazist.ir" + "\n")
# # printer.text(datetime)
# p.cut()