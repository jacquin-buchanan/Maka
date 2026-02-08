from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout)

from maka.util.Preferences import preferences as prefs
import maka.util.TextUtils as TextUtils


class ObservationDialog(QDialog):
    

    def __init__(self, parent, obs, docFormat):
        
        super(ObservationDialog, self).__init__(parent=parent)
        
        self._obs = obs
        self._docFormat = docFormat
        
        name = self._obs.__class__.__name__
        self.setWindowTitle(name)
        
        box = QVBoxLayout()
        
        formLayout = self._createFormLayout()
        box.addLayout(formLayout)
        
#         self._statusBar = QStatusBar()
#         self._statusBar.setSizeGripEnabled(False)
#         box.addWidget(self._statusBar)
#         self._statusBar.showMessage('Hello, Harold!')
        
        buttonBox = self._createButtonBox()
        box.addWidget(buttonBox)
        
        self.setLayout(box)
        
        
    def sizeHint(self):
        width = prefs.get('observationDialog.width', 400)
        return QSize(width, 0)
    
    
    def _createFormLayout(self):
        
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        obsFormat = self._docFormat.getObservationFormat(self._obs.__class__.__name__)
        fields = dict((f.name, f) for f in self._obs.FIELDS)
        self._editors = {}
        
        for fieldName in obsFormat.fieldOrder:
            
            field = fields[fieldName]
            
            label = self._getFieldLabel(field)
            
            fieldFormat = obsFormat.getFieldFormat(fieldName)
            value = getattr(self._obs, fieldName)
            text = fieldFormat.format(value, editing=True)
            
            editor = _FieldValueEditor(self, fieldFormat)
            editor.setText(text)
            editor.setToolTip(self._getFieldToolTip(field, fieldFormat))
            
            layout.addRow(label, editor)
            
            self._editors[fieldName] = editor
            
        return layout
    
    
    def _getFieldLabel(self, field):
        parts = TextUtils.splitCamelCaseString(field.name)
        return ' '.join(p.capitalize() for p in parts) + ':'
    
    
    def _getFieldToolTip(self, field, fieldFormat):
        
        # Included information:
        # 
        # * format hint (like "ddd:mm:ss", "hh:mm:ss") from field format or field value type name
        #   (like "string" or "decimal") from field if format hint is not available
        # * units description (like "degrees below zenith") from field (if available)
        # * range description (like "in [0, 180]", or "in [0, 6]") from field (if available)
        # 
        # How about <format or type> [<units>,] [in <range>]?
        # 
        # Examples:
        # 
        #   mm/dd/yy
        #   hh:mm:ss
        #   string
        #   integer
        #   decimal
        #   integer greater than 0
        #   integer greater than or equal to 0
        #   integer in [0, 6] (menu for this?)
        #   string in {Pod, Vessel} (menu for this?)
        #   ddd:mm:ss in [0, 180]
        #   decimal meters, greater than or equal to 0
        #   integer degrees, in [0, 359]
        #   decimal minutes, in [0, 60)
        #   ddd:mm:ss degrees below zenith, in [0, 180]
        #   ddd:mm:ss degrees clockwise from magnetic north, in [0, 360)
        
        hint = fieldFormat.hint if fieldFormat.hint is not None else field.typeName
        units = ' ' + field.units if field.units is not None else ''
        range = ' ' + field.range if field.range is not None else ''
        sep = ',' if len(units) != 0 and len(range) != 0 else ''
        return hint + units + sep + range
    
        
    def _createButtonBox(self):
        
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self._okButton = box.button(QDialogButtonBox.Ok)
        
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        
        return box
    
    
    def _updateOkButtonState(self):
        
        enabled = True
        for editor in self._editors.values():
            if not editor._valueOk:
                enabled = False
                break
            
        self._okButton.setEnabled(enabled)
        
        
    def getChanges(self):
        
        obsFormat = self._docFormat.getObservationFormat(self._obs.__class__.__name__)
        
        changes = {}
        
        for fieldName, editor in self._editors.items():
            
            oldValue = getattr(self._obs, fieldName)
            
            fieldFormat = obsFormat.getFieldFormat(fieldName)
            newValue = fieldFormat.parse(editor.text(), editing=True)
            
            if newValue != oldValue:
                changes[fieldName] = newValue
                
        return changes
                
            
_OK_STYLE_SHEET = 'QLineEdit {background-color: white}'
_ERROR_STYLE_SHEET = 'QLineEdit {background-color: rgb(255, 220, 220)}'


class _FieldValueEditor(QLineEdit):
    
    
    def __init__(self, parent, fieldFormat):
        
        super(_FieldValueEditor, self).__init__(parent=parent)
        
        self._fieldFormat = fieldFormat
        self._valueOk = True
        
        self._updateStyleSheet()
        
        self.textChanged.connect(self._textChanged)
        
        
    def _updateStyleSheet(self):
        self.setStyleSheet(_OK_STYLE_SHEET if self._valueOk else _ERROR_STYLE_SHEET)
        
        
    def _textChanged(self, text):
        
        try:
            self._fieldFormat.parse(text, editing=True)
        except ValueError:
            ok = False
        else:
            ok = True
            
        if ok != self._valueOk:
            self._valueOk = ok
            self._updateStyleSheet()
            self.parent()._updateOkButtonState()
    