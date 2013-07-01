#!/usr/bin/env python
from gi.repository import Gtk

from modemconfiguration.view import MainWindow
from modemconfiguration import model


win = MainWindow(model)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
