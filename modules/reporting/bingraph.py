# Copyright (C) 2019 DoomedRaven
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.


import os
import logging
from lib.cuckoo.common.config import Config
from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.constants import CUCKOO_ROOT

try:
    from lib.cuckoo.common.graphs.binGraph.binGraph import generate_graphs as bingraph_gen
    HAVE_BINGRAPH = True
except ImportError:
    HAVE_BINGRAPH = False

log = logging.getLogger(__name__)
reporting_conf = Config("reporting")

bingraph_args_dict = {
  'recurse': False,
  '__dummy': False,
  'prefix': None,
  'json': False,
  'graphtitle': None,
  'showplt': False,
  'format': 'svg',
  'figsize': (12, 4),
  'dpi': 100,
  'blob': False,
  'verbose': False,
  'graphtype': 'ent',
  'chunks': 750,
  'ibytes': [{
    'name': '0s',
    'bytes': [0],
    'colour': (0.0, 1.0, 0.0, 1.0)
  }],
  'entcolour': '#ff00ff'
}


class BinGraph(Report):
    "Generate bingraphs"

    def run(self, results):
        if HAVE_BINGRAPH and reporting_conf.bingraph.enabled:
            bingraph_path = os.path.join(self.analysis_path, "bingraph")
            if not os.path.exists(bingraph_path):
                os.makedirs(bingraph_path)
            try:
                if not os.listdir(bingraph_path):
                    bingraph_args_dict.update({
                        "prefix": results["target"]["file"]["sha256"],
                        "files": [self.file_path],
                        "save_dir": bingraph_path,
                    })
                    bingraph_gen(bingraph_args_dict)
            except Exception as e:
                log.info(e)

            for key in ("dropped", "procdump", "CAPE"):
                for block in results.get(key, []) or []:
                    if block["size"] != 0 and block["type"].startswith("PE32") and \
                            not os.path.exists(os.path.join(bingraph_path, "{}-ent.svg".format(block["sha256"]))):
                        bingraph_args_dict.update({
                            "prefix": block["sha256"],
                            "files": [block["path"]],
                            "save_dir": bingraph_path,
                        })
                        bingraph_gen(bingraph_args_dict)
