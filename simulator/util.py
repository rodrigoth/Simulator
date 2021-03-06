#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Rodrigo Teles Hermeto

import logging
import sys

logging.basicConfig(filename='experiment.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s : %(message)s')
sh.setFormatter(formatter)
logging.getLogger().addHandler(sh)


def print_log(asn, text, header=False):
    # if header:
    #     logging.info("********************* {} *********************".format(text))
    # else:
    #     logging.info("({}) {}".format(asn,text))
    # logging.info("")
    return
