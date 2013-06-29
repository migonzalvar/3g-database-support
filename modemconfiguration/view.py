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

from .model import ServiceProviderDatabaseError


def list_filler(gtk_list, iterable, unpacker=lambda x: (x.name, x)):
    gtk_list.clear()
    for i in iterable:
        gtk_list.append(unpacker(i))
    return gtk_list


def make_combo_with_label(store, label_text=''):
    label_group = make_combo_with_label.__dict__.setdefault(
        'label_group',
        Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
    )
    combo_group = make_combo_with_label.__dict__.setdefault(
        'combo_group',
        Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
    )

    label = Gtk.Label(label_text)
    label_group.add_widget(label)

    combo = Gtk.ComboBox()
    combo_group.add_widget(combo)
    combo.set_model(store)
    renderer_text = Gtk.CellRendererText()
    combo.pack_start(renderer_text, True)
    combo.add_attribute(renderer_text, "text", 0)

    box = Gtk.HBox()
    box.pack_start(label, True, True, 0)
    box.pack_start(combo, True, True, 0)
    box.show()
    return box, combo


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

        box, self.country_combo = make_combo_with_label(country_store,
                                                        _('Country'))
        main_box.pack_start(box, True, True, 0)

        box, self.provider_combo = make_combo_with_label(provider_store,
                                                         _('Provider'))
        main_box.pack_start(box, True, True, 0)

        box, self.plan_combo = make_combo_with_label(plan_store, _('Plan'))
        main_box.pack_start(box, True, True, 0)

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
