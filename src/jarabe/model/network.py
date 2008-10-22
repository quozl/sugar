# Copyright (C) 2008 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import dbus

from sugar import dispatch

NM_SETTINGS_PATH = '/org/freedesktop/NetworkManagerSettings'
NM_SETTINGS_IFACE = 'org.freedesktop.NetworkManagerSettings'
NM_CONNECTION_IFACE = 'org.freedesktop.NetworkManagerSettings.Connection'
NM_SECRETS_IFACE = 'org.freedesktop.NetworkManagerSettings.Connection.Secrets'

_nm_settings = None

class NMSettings(dbus.service.Object):
    connections = []

    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SystemBus(), NM_SETTINGS_PATH)
        connections = []

    @dbus.service.method(dbus_interface=NM_SETTINGS_IFACE,
                         in_signature='', out_signature='ao')
    def ListConnections(self):
        return self.connections

    @dbus.service.signal(NM_SETTINGS_IFACE, signature='o')
    def NewConnection(self, connection_path):
        pass

    def add_connection(self, conn):
        self.connections.append(conn.object_path)
        self.NewConnection(conn.object_path)

class NMSettingsConnection(dbus.service.Object):
    _counter = 0

    def __init__(self, settings, secrets):
        path = NM_SETTINGS_PATH + '/' + self._counter
        self._counter += 1

        dbus.service.Object.__init__(self, dbus.SystemBus(), path)

        self.secrets_request = dispatch.Signal()

        self._settings = settings
        self._secrets = secrets

    @dbus.service.method(dbus_interface=NM_CONNECTION_IFACE,
                         in_signature='', out_signature='a{sa{sv}}')
    def GetSettings(self):
        return self._settings

    @dbus.service.method(dbus_interface=NM_SECRETS_IFACE,
                         in_signature='sasb', out_signature='a{sa{sv}}')
    def GetSecrets(self, setting_name, hints, request_new):
        if request_new or self._secrets is None:
            self.secrets_request.send(self)

        return self._secrets

def add_connection(settings, secrets=None):
    global _nm_settings
    if _nm_settings is None:
        _nm_settings = NMSettings()

    conn = NMSettingsConnection()
    _nm_settings.add_connection(conn)

def load_connections():
    pass