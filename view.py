#!/usr/bin/python
from gi.repository import Gtk


class Plan(list):
    @property
    def apn(self):
        return "www.example.com"

class Provider(object):
    def __init__(self, name):
        self.name = name

    @property
    def plans(self):
        plan_store = Gtk.ListStore(str, object)
        for plan in plans[self.name]:
            plan_store.append([plan, Plan(plan)])
        return plan_store

class Country(object):
    def __init__(self, name):
        self.name = name

    @property
    def providers(self):
        provider_store = Gtk.ListStore(str, object)
        for provider in providers[self.name]:
            provider_store.append([provider, Provider(provider)])
        return provider_store

plans = {
    'Aaa': ['morning', 'afternoon'],
    'Bbb': ['S', 'XL'],
    'Zzz': ['base', 'red'],
    'Yyy': ['combo', 'multi'],
    '123': ['prepaid', 'postpaid'],
    '987': ['basic', 'premium'],
}

providers = {
    "Austria": ["Aaa", "Bbb"],
    "Brazil": ["Zzz", "Yyy"],
    "Belgium": ["123", "987"],
}

countries = [
    Country("Austria"),
    Country("Brazil"),
    Country("Belgium"),
]

class CountryListStore(Gtk.ListStore):
    def __init__(self, *args, **kwargs):
        Gtk.ListStore.__init__(self, str, object)
        for country in countries:
            self.append([country.name, country])


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
        country_store = CountryListStore()

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

        self.provider_combo = Gtk.ComboBox()
        self.provider_combo.set_model(provider_store)
        self.provider_combo.connect("changed", self._provider_selected_cb)
        renderer_text = Gtk.CellRendererText()
        self.provider_combo.pack_start(renderer_text, True)
        self.provider_combo.add_attribute(renderer_text, "text", 0)
        main_box.pack_start(self.provider_combo, True, True, 0)

        self.plan_combo = Gtk.ComboBox()
        self.plan_combo.set_model(plan_store)
        self.plan_combo.connect("changed", self._plan_selected_cb)
        renderer_text = Gtk.CellRendererText()
        self.plan_combo.pack_start(renderer_text, True)
        self.plan_combo.add_attribute(renderer_text, "text", 0)
        main_box.pack_start(self.plan_combo, True, True, 0)

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
            country = model[tree_iter][1]
            self.provider_combo.set_model(country.providers)
            self.provider_combo.set_active(0)
            print "Selected: country=%s" % country.name
            # TODO: Update provider model and plan

    def _provider_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            provider = model[tree_iter][1]
            self.plan_combo.set_model(provider.plans)
            self.plan_combo.set_active(0)
            print "Selected: provider=%s" % provider.name
        # TODO: Update plan model

    def _plan_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            plan = model[tree_iter][1]
            print "Selected: apn=%s" % plan.apn
        # TODO: Populate entries except PIN


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
