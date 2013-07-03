# -*- encoding: utf-8 -*-
# Copyright (C) 2010 Andrés Ambrois
# Copyright (C) 2012 Ajay Garg
# Copyright (C) 2013 Miguel González
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from .model import ServiceProviderDatabaseError

class Color(object):

    def __init__(self, color, alpha=1.0):
        self._r, self._g, self._b = self._html_to_rgb(color)
        self._a = alpha

    def get_gdk_color(self):
        return Gdk.Color(int(self._r * 65535), int(self._g * 65535),
                         int(self._b * 65535))

    def _html_to_rgb(self, html_color):
        """ #RRGGBB -> (r, g, b) tuple (in float format) """

        html_color = html_color.strip()
        if html_color[0] == '#':
            html_color = html_color[1:]
        if len(html_color) != 6:
            raise ValueError('input #%s is not in #RRGGBB format' % html_color)

        r, g, b = html_color[:2], html_color[2:4], html_color[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        r, g, b = (r / 255.0, g / 255.0, b / 255.0)

        return (r, g, b)


class style:
    DEFAULT_SPACING = 15
    COLOR_SELECTION_GREY = Color('#A6A6A6')

def list_filler(gtk_list, iterable, unpacker=lambda x: (x.name, x)):
    gtk_list.clear()
    for i in iterable:
        gtk_list.append(unpacker(i))
    return gtk_list


class SectionView(Gtk.VBox):
    pass


class ModemConfiguration(SectionView):
    def __init__(self, model):
        SectionView.__init__(self)

        self._model = model

        main_box = Gtk.VBox()
        self.add(main_box)
        main_box.show()

        country_store = Gtk.ListStore(str, object)
        country_store.append([])

        provider_store = Gtk.ListStore(str, object)
        provider_store.append([])

        plan_store = Gtk.ListStore(str)
        plan_store.append([])

        self._label_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self._combo_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)

        box, self.country_combo = self._make_combo_with_label(country_store,
                                                              _('Country:'))
        main_box.pack_start(box, False, False, 0)
        box.show()

        box, self.provider_combo = self._make_combo_with_label(provider_store,
                                                               _('Provider:'))
        main_box.pack_start(box, False, False, 0)
        box.show()

        box, self.plan_combo = self._make_combo_with_label(plan_store,
                                                           _('Plan:'))
        main_box.pack_start(box, False, False, 0)
        box.show()

        separator = Gtk.HSeparator()
        self.add(separator)
        separator.show()

        try:
            self.db_manager = self._model.ServiceProvidersDatabase()
        except ServiceProviderDatabaseError:
            self.db_manager = None
        else:
            countries = self.db_manager.get_countries()
            list_filler(country_store, countries)
            providers = self.db_manager.get_providers()
            plans = self.db_manager.get_plans()
            provider_store = list_filler(Gtk.ListStore(str, object), providers)
            plan_store = list_filler(Gtk.ListStore(str, object), plans)
            current_country = self.db_manager.get_country()
            current_provider = self.db_manager.get_provider()
            current_plan = self.db_manager.get_plan()
            self.country_combo.set_model(country_store)
            self.country_combo.set_active(current_country.idx)
            self.provider_combo.set_model(provider_store)
            self.provider_combo.set_active(current_provider.idx)
            self.plan_combo.set_model(plan_store)
            self.plan_combo.set_active(current_plan.idx)

        self.country_combo.connect("changed", self._country_selected_cb)
        self.provider_combo.connect("changed", self._provider_selected_cb)
        self.plan_combo.connect("changed", self._plan_selected_cb)

    def _make_combo_with_label(self, store, label_text=''):
        label = Gtk.Label(label_text)
        self._label_group.add_widget(label)

        combo = Gtk.ComboBox()
        self._combo_group.add_widget(combo)
        combo.set_model(store)
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("max-width-chars", 25)
        renderer_text.set_property("width-chars", 25)
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 0)

        box = Gtk.HBox()
        box.pack_start(label, False, True, 0)
        label.show()
        box.pack_start(combo, False, True, 0)
        combo.show()
        return box, combo


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

    def _plan_selected_cb(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            plan = model[tree_iter][1]
            self.db_manager.set_plan(plan.idx)
            self.db_manager.save()


class MainWindow(Gtk.Window):
    def __init__(self, model):
        Gtk.Window.__init__(self, title="Main window")
        section = ModemConfiguration(model)
        self.add(section)
