# -*- coding: utf-8 -*-
'''muScale without console'''
__author__ = 'Yadavito'

import muscale
import ctypes
import utils.const as cn

if __name__ == '__main__':
    # id: company.product.subproduct.version
    app_id = cn._separator.join([cn._company, cn._product, cn._subproduct, cn._version])
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    muscale.main()