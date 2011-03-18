'''
Created on Mar 18, 2011

@author: Yadavito
'''
def unfillLayout(layoutName):
    '''Empty layout from widgets (should be reinit'd, if in another layout)'''
    def deleteItems(layout): 
        if layout is not None: 
            while layout.count(): 
                item = layout.takeAt(0) 
                widget = item.widget() 
                if widget is not None: 
                    widget.deleteLater() 
                else: 
                    deleteItems(item.layout()) 
    deleteItems(layoutName) 