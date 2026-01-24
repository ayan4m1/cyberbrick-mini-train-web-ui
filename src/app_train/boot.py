# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2026 ayan4m1 <andrew@bulletlogic.com>
# Portions Copyright (c) 2025 MakerWorld
#
# This file is executed on every boot (including wake-boot from deepsleep)

import bbl_product
import sys

_PRODUCT_NAME = "Mini Train"
_PRODUCT_VERSION = "01.00.00.04"

bbl_product.set_app_name(_PRODUCT_NAME)
bbl_product.set_app_version(_PRODUCT_VERSION)
del bbl_product
del _PRODUCT_NAME
del _PRODUCT_VERSION

sys.path.append('/app')
import uasyncio
import http_main

uasyncio.run(http_main.main())