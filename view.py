#!/usr/bin/python
from gi.repository import Gtk



class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        main_box = Gtk.VBox()
        self.add(main_box)
        main_box.show()

        self._upper_box = Gtk.VBox()
        main_box.pack_start(self._upper_box, True, True, 0)
        self._upper_box.show()

        # FIXME: refactor to use model
        country_store = Gtk.ListStore(str)
        countries = ["Austria", "Brazil", "Belgium", "France", "Germany",
                     "Switzerland", "United Kingdom", "United States of America",
                     "Uruguay"]
        for country in countries:
            country_store.append([country])

        provider_store = Gtk.ListStore(str)
        provider_store.append([])

        plan_store = Gtk.ListStore(str)
        plan_store.append([])

        country_combo = Gtk.ComboBox()
        country_combo.set_model(country_store)
        country_combo.connect("changed", self._country_selected_cb)
        renderer_text = Gtk.CellRendererText()
        country_combo.pack_start(renderer_text, True)
        country_combo.add_attribute(renderer_text, "text", 0)
        # TODO: country_combo.set_active(country_store.guess_country_row())
        main_box.pack_start(country_combo, True, True, 0)

        provider_combo = Gtk.ComboBox()
        provider_combo.set_model(provider_store)
        provider_combo.connect("changed", self._provider_selected_cb)
        renderer_text = Gtk.CellRendererText()
        provider_combo.pack_start(renderer_text, True)
        main_box.pack_start(provider_combo, True, True, 0)

        plan_combo = Gtk.ComboBox()
        plan_combo.set_model(plan_store)
        plan_combo.connect("changed", self._plan_selected_cb)
        renderer_text = Gtk.CellRendererText()
        plan_combo.pack_start(renderer_text, True)
        main_box.pack_start(plan_combo, True, True, 0)

        # label = gtk.Label(_('Country:'))
        # label.set_alignment(1, 0.5)
        # label_group.add_widget(label)
        # box.pack_start(label, False)
        # label.show()
        # country_store = model.CountryListStore()
        # country_combo = gtk.ComboBox(country_store)
        # combo_group.add_widget(country_combo)
        # cell = gtk.CellRendererText()
        # cell.props.xalign = 0.5
        # country_combo.pack_start(cell)
        # country_combo.add_attribute(cell, 'text', 0)
        # country_combo.connect('changed', self.__country_selected_cb)
        # box.pack_start(country_combo, False)
        # country_combo.show()
        # self._upper_box.pack_start(box, False)
        # box.show()

        # box = gtk.HBox(spacing=style.DEFAULT_SPACING * 2)
        # label = gtk.Label(_('Provider:'))
        # label.set_alignment(1, 0.5)
        # label_group.add_widget(label)
        # box.pack_start(label, False)
        # label.show()
        # self._providers_combo = gtk.ComboBox()
        # combo_group.add_widget(self._providers_combo)
        # cell = gtk.CellRendererText()
        # cell.props.xalign = 0.5
        # self._providers_combo.pack_start(cell)
        # self._providers_combo.add_attribute(cell, 'text', 0)
        # self._providers_combo.connect('changed',
        #                               self.__provider_selected_cb)
        # box.pack_start(self._providers_combo, False)
        # self._providers_combo.show()
        # self._upper_box.pack_start(box, False)
        # box.show()

        # box = gtk.HBox(spacing=style.DEFAULT_SPACING*2)
        # label = gtk.Label(_('Plan:'))
        # label.set_alignment(1, 0.5)
        # label_group.add_widget(label)
        # box.pack_start(label, False)
        # label.show()
        # self._plan_combo = gtk.ComboBox()
        # combo_group.add_widget(self._plan_combo)
        # cell = gtk.CellRendererText()
        # cell.props.xalign = 0.5
        # self._plan_combo.pack_start(cell)
        # self._plan_combo.add_attribute(cell, 'text', 0)
        # self._plan_combo.connect('changed', self.__plan_selected_cb)
        # box.pack_start(self._plan_combo, False)
        # self._plan_combo.show()
        # self._upper_box.pack_start(box, False)
        # box.show()

        # country_combo.set_active(country_store.guess_country_row())

        self.button = Gtk.Button(label="Click Here")
        self.button.connect("clicked", self.on_button_clicked)
        main_box.pack_start(self.button, True, True, 0)

    def on_button_clicked(self, widget):
        print "Hello World"

    def _country_selected_cb(self, combo):
        print "Country changed"
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][0]
            print "Selected: country=%s" % country
            # TODO: Update provider model

    def _provider_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            provider = model[tree_iter]
        # TODO: Update plan model

    def _plan_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            plan = model[tree_iter]
        # TODO: Change detailed values


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
