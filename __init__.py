# -*- coding: utf-8 -*-
"""
/***************************************************************************
 emuia
                                 A QGIS plugin
 emuia
                             -------------------
        begin                : 2015-10-06
        copyright            : (C) 2015 by Tomasz Hak
        email                : tomplamka@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load emuia class from file emuia.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .emuia import emuia
    return emuia(iface)
