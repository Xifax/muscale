# -*- coding: utf-8 -*-
'''muScale without console'''
__author__ = 'Yadavito'

# own #
import muscale
import utils.const as cn

# internal #
import ctypes, platform

if __name__ == '__main__':
    if platform.release() is '7':
        # id: company.product.subproduct.version
        app_id = cn._separator.join([cn._company, cn._product, cn._subproduct, cn._version])
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    muscale.main()