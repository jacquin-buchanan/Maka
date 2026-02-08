'''
This program demonstrates a problem I've encountered with the PySide
QListWidget class, using PySide 1.2.1, Qt 4.8.5, and Mac OS X 10.8.5.

To see the problem:

1. Run the program.
2. Scroll down the list.
3. Click on a list item to select it.
4. Press the "Delete" button.

When the item is deleted, the list scrolls to the top. I believe that it
should not scroll to the top.

The problem appears to have something to do with setting the selection
mode of the list to QAbstractItemView.ContiguousSelection. If one
instead sets the selection mode to QAbstractItemView.SingleSelection,
the problem does not occur.

Harold Mills
11 February 2014
'''


import sys

from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QListWidget, QMainWindow,
    QPushButton, QVBoxLayout, QWidget)
 
 
class TestWindow(QMainWindow):
    
    
    def __init__(self):
        
        super(TestWindow, self).__init__()
        
        self.setWindowTitle('PySide QListWidget Problem')
        
        self._list = QListWidget(self)
        self._list.insertItems(0, [str(i + 1) for i in range(50)])
        
        # This line seems to be the problem. Change "Contiguous" to "Single"
        # and item deletion does not cause the list to scroll to the top.
        self._list.setSelectionMode(QAbstractItemView.ContiguousSelection)
        
        button = QPushButton('Delete', self)
        button.clicked.connect(self._on_button_clicked)
        
        box = QVBoxLayout()
        box.addWidget(self._list)
        box.addWidget(button)
        
        widget = QWidget()
        widget.setLayout(box)
        
        self.setCentralWidget(widget)


    def _on_button_clicked(self):
        l = self._list
        for item in l.selectedItems():
            l.takeItem(l.row(item))
        
        
def _main():
    
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    window.raise_()
    
    app.exec()
    
    sys.exit()


if __name__ == '__main__':
    _main()
