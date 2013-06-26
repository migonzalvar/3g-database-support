from gi.repository import Gtk


from .model import ServiceProviderDatabaseError


def list_filler(gtk_list, iterable, unpacker=lambda x: (x.name, x)):
    gtk_list.clear()
    for i in iterable:
        gtk_list.append(unpacker(i))
    return gtk_list


class MyWindow(Gtk.Window):

    def __init__(self, model):
        Gtk.Window.__init__(self, title="Hello World")

        self._model = model

        main_box = Gtk.VBox()
        self.add(main_box)
        main_box.show()

        self._upper_box = Gtk.VBox()
        main_box.pack_start(self._upper_box, True, True, 0)
        self._upper_box.show()

        country_store = Gtk.ListStore(str, object)
        country_store.append([])

        provider_store = Gtk.ListStore(str, object)
        provider_store.append([])

        plan_store = Gtk.ListStore(str)
        plan_store.append([])

        self.country_combo = Gtk.ComboBox()
        self.country_combo.set_model(country_store)
        self.country_combo.connect("changed", self._country_selected_cb)
        renderer_text = Gtk.CellRendererText()
        self.country_combo.pack_start(renderer_text, True)
        self.country_combo.add_attribute(renderer_text, "text", 0)
        main_box.pack_start(self.country_combo, True, True, 0)

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

        try:
            self.db_manager = self._model.ServiceProvidersDatabase()
        except ServiceProviderDatabaseError:
            self.db_manager = None
        else:
            countries = self.db_manager.get_countries()
            list_filler(country_store, countries)
            current_country = self.db_manager.get_country()
            self.country_combo.set_model(country_store)
            self.country_combo.set_active(current_country.idx)

    def _country_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][1]
            self.db_manager.set_country(country.idx)
            providers = self.db_manager.get_providers()
            store = list_filler(Gtk.ListStore(str, object), providers)
            current = self.db_manager.get_provider()
            self.provider_combo.set_model(store)
            self.provider_combo.set_active(current.idx)
            print "Selected: country=%s" % country.name

    def _provider_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            provider = model[tree_iter][1]
            self.db_manager.set_provider(provider.idx)
            plans = self.db_manager.get_plans()
            store = list_filler(Gtk.ListStore(str, object), plans)
            current = self.db_manager.get_plan()
            self.plan_combo.set_model(store)
            self.plan_combo.set_active(current.idx)
            print "Selected: provider=%s" % provider.name

    def _plan_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            plan = model[tree_iter][1]
            print "Selected: apn=%s" % plan.name
            print "Settings: %s" % plan.__dict__
