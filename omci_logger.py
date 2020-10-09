# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# vOMCI logger
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" This module gives access to the OMCI Logger
"""
import logging
import os
import sys
from typing import Optional


class OmciLogger:
    def __init__(self, name: Optional[str] = None, level=logging.DEBUG):
        if name is None:
            prog_basename = os.path.basename(sys.argv[0])
            (name, _) = os.path.splitext(prog_basename)
        else:
            name = name.replace('omci_', '')
        logger = logging.getLogger(name)
        logging.basicConfig(level=level)

    @staticmethod
    def getLogger(name: str) -> logging.Logger:
        return logging.getLogger(name.replace('omci_', ''))

