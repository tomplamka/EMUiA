# -*- coding: utf-8 -*-
"""
/***************************************************************************
 emuia
                                 A QGIS plugin
 emuia
                              -------------------
        begin                : 2015-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Tomasz Hak
        email                : tomplamka@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import getpass
import psycopg2
from datetime import *
import sys
import os
import pdb
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from emuia_dialog import emuiaDialog
import os.path


class emuia:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'emuia_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = emuiaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&emuia')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'emuia')
        self.toolbar.setObjectName(u'emuia')
        
        self.dlg.nazwaAdresataLineEdit.clear()
        self.dlg.imieLineEdit.clear()
        self.dlg.nazwiskoLineEdit.clear()
        self.dlg.ulicaLineEdit.clear()
        self.dlg.numerBudynkuLineEdit.clear()
        self.dlg.numerLokaluLineEdit.clear()
        self.dlg.miejscowoscLineEdit.clear()
        self.dlg.kodLineEdit.clear()
        self.dlg.telefonLineEdit.clear()
        self.dlg.emailLineEdit.clear()
        
        #self.dlg.dataZlozeniaWnioskuLineEdit.clear()
        self.dlg.miejscowoscWnLineEdit.clear()
        self.dlg.ulicaWnLineEdit.clear()
        
        self.dlg.obrebComboBox.addItem(u'Knurów')
        self.dlg.obrebComboBox.addItem(u'Krywałd')
        self.dlg.obrebComboBox.addItem(u'Szczygłowice')
        
        self.dlg.numerDzialkiLineEdit.clear()
        
        self.dlg.statusBudowyComboBox.addItem(u'istniejacy')
        self.dlg.statusBudowyComboBox.addItem(u'prognozowany')
        self.dlg.statusBudowyComboBox.addItem(u'wtrakcieBudowy')
        
        self.dlg.zalKopiaMapyLineEdit.clear()
        self.dlg.zalMPZPLineEdit.clear()


        self.dlg.btnRejestruj.clicked.connect(self.wniosek)
        self.dlg.btnClearForm.clicked.connect(self.clearForm)
        
        #wczytuje ścieżkę do pliku załącznika
        self.dlg.btnSaveZal1.clicked.connect(self.select_output_file1)
        self.dlg.btnSaveZal2.clicked.connect(self.select_output_file2)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('emuia', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/emuia/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EMUiA'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&emuia'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def select_output_file1(self):
        username = getpass.getuser()
        username = str(username)
        zal1Dir = r'C:\Users'
        zalEndDir = '\Desktop'
        path = os.path.join(zal1Dir, username + zalEndDir)
        filenameZal1 = QFileDialog.getOpenFileName(self.dlg, "Wybierz plik ",path, '*.pdf')
        self.dlg.zalKopiaMapyLineEdit.setText(filenameZal1)
        
    def select_output_file2(self):
        username = getpass.getuser()
        username = str(username)
        zal2Dir = r'C:\Users'
        zalEndDir = '\Desktop'
        path = os.path.join(zal2Dir, username + zalEndDir)
        filenameZal2 = QFileDialog.getOpenFileName(self.dlg, "Wybierz plik ",path, '*.pdf')
        self.dlg.zalMPZPLineEdit.setText(filenameZal2)
        
    def wniosek(self):
        
        
        #Dane wnioskodawcy
        newlineNameAdr = self.dlg.nazwaAdresataLineEdit.text()
        newlineImie_2 = self.dlg.imieLineEdit.text()        
        newlineNazwisko_2 = self.dlg.nazwiskoLineEdit.text()
        newlineUlica = self.dlg.ulicaLineEdit.text()
        newlineNrBud = self.dlg.numerBudynkuLineEdit.text()
        nrLok = self.dlg.numerLokaluLineEdit.text()
        newlineMiejscowosc = self.dlg.miejscowoscLineEdit.text()
        newlineKod = self.dlg.kodLineEdit.text()
        telefon = self.dlg.telefonLineEdit.text()
        email = self.dlg.emailLineEdit.text()
        
        #Dane dotyczące położenia nieruchomości
        dataDatePicker = self.dlg.dataWnioskuLineEdit.text()
        day,month,year = dataDatePicker.split('-')
        newlineDataWniosku = (datetime(int(year),int(month),int(day)))
        
        miejscowoscWn = self.dlg.miejscowoscWnLineEdit.text()
        ulicaWn = self.dlg.ulicaWnLineEdit.text()        
        newcbRejon = self.dlg.obrebComboBox.currentText()
        newlineNumDzialek = self.dlg.numerDzialkiLineEdit.text()
        newcbStatus = self.dlg.statusBudowyComboBox.currentText()
        
        zal1 = self.dlg.zalKopiaMapyLineEdit.text()
        zal2 = self.dlg.zalMPZPLineEdit.text()
        
        
        #newlineRodzDok = self.dlg.rodzajDokComboBox.currentText()
        #newlineCelDok = self.dlg.celWydaniaDokumentuLineEdit.text()
        #newlineOplata = self.dlg.oplataLineEdit.text()
        #newlinePobOplSkarb = self.dlg.pobranaOplataSkarowaLineEdit.text()
        #newlineNumDzialek = self.dlg.numeryDzialekLineEdit.text()
        #newlineDokPlan = self.dlg.dokumentyPlanistyczneLineEdit.text()
        
        #newlineZalWniosek = self.dlg.zalDoWnioskuLineEdit.text()
        #output_file = open(newlineZalWniosek, 'w')
        
        dataRejestracji = datetime.now()
        username = getpass.getuser()
        username = str(username)
         
        
        con = None

        try:
             
            con = psycopg2.connect(database='netgis_knurow', user='netgis_knurow', password='n4feqeTR', host='178.216.202.213')
            cur = con.cursor()
            
            #cur.execute("select Id from rejestr order by id desc limit 1")
            #con.commit()
            #dataId = cur.fetchone()[0]
            #newlineId = (dataId + 1)
            
            #rok
            rok = datetime.now().year
            
            #numer kolejnej sprawy
            #cur.execute("select datenow from emuia order by datenow desc limit 1")
            #con.commit()
            #datenowVal = cur.fetchone()[0]
            #datenowVal = str(datenowVal)
            #year, month, day = datenowVal.split('-')
            #if (year < rok):
            #    nrSpr = 0
            #else:
            #    cur.execute("select idznspr from emuia order by idznspr desc limit 1")
            #    con.commit()
            #    idZnSpr = cur.fetchone()[0]
            #    nrSpr = idZnSpr + 1
            #newlineZnakSpr = 'UA.6727.1.' + str(nrSpr) + '.' + str(rok)
            
            #znak sprawy
            #if (newlineRodzDok == u'Wypis' or newlineRodzDok == u'Wyrys'):
            #    newlineZnakSpr = 'UA.6727.1.' + str(nrSpr) + '.' + str(rok)
            #elif (newlineRodzDok == u'Zaświadczenie'):
            #    newlineZnakSpr = 'UA.6727.3.' + str(nrSpr) + '.' + str(rok)
            
            if all([not newlineImie_2, not newlineNazwisko_2, not newlineUlica, not newlineNrBud, not newlineMiejscowosc, not newlineKod, not newlineDataWniosku, not miejscowoscWn, not ulicaWn, not newcbRejon, not newlineNumDzialek, not newcbStatus]):
                iface.messageBar().pushMessage('Puste pole', u'Proszę wypełnić wszystkie pola formularza', level=QgsMessageBar.CRITICAL, duration=10)
            else:
            
                query = "INSERT INTO emuia (nameadr, imie, nazwisko, ulica, nrbud, nrlok, miejscowosc, kod, phone, email, datawniosku, miejscowoscwn, ulicawn, rejon, numdzialki, statusbud, dokplan, zalwniosek, datenow, username) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                data = (newlineNameAdr, newlineImie_2, newlineNazwisko_2, newlineUlica, newlineNrBud, nrLok, newlineMiejscowosc, newlineKod, telefon, email, newlineDataWniosku, miejscowoscWn, ulicaWn, newcbRejon, newlineNumDzialek, newcbStatus, zal1, zal2, dataRejestracji, username)

                cur.execute(query, data)
                con.commit()

                
                iface.messageBar().pushMessage('Sukces', u'Dane zostały zapisane', level=QgsMessageBar.SUCCESS, duration=5)

        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()

            iface.messageBar().pushMessage(u'Błąd', u'Problem z połączeniem do bazy', level=QgsMessageBar.CRITICAL, duration=5)
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()
                
            else:
                iface.messageBar().pushMessage(u'Błąd', u'Dane nie zostały zapisane', level=QgsMessageBar.CRITICAL, duration=5)
        
    def clearForm(self):
        self.dlg.nazwaAdresataLineEdit.clear()
        self.dlg.imieLineEdit.clear()
        self.dlg.nazwiskoLineEdit.clear()
        self.dlg.ulicaLineEdit.clear()
        self.dlg.numerBudynkuLineEdit.clear()
        self.dlg.numerLokaluLineEdit.clear()
        self.dlg.miejscowoscLineEdit.clear()
        self.dlg.kodLineEdit.clear()
        self.dlg.telefonLineEdit.clear()
        self.dlg.emailLineEdit.clear()
        
        self.dlg.miejscowoscWnLineEdit.clear()
        self.dlg.ulicaWnLineEdit.clear()    
        self.dlg.numerDzialkiLineEdit.clear()
        
        self.dlg.zalKopiaMapyLineEdit.clear()
        self.dlg.zalMPZPLineEdit.clear()


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
