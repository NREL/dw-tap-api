# -*- coding: utf-8 -*-

import h5pyd

f = h5pyd.File(domain="/nrel/wtk-us.h5",
               endpoint="https://tap-hsds.ace.nrel.gov",
               username=None,
               password=None,
               api_key=None,
               bucket="nrel-pds-hsds",
               mode='r')
