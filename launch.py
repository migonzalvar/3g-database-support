from gi.repository import Gtk

from modemconfiguration.view import MyWindow
from modemconfiguration import model


win = MyWindow(model)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
