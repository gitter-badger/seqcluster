"""Implementation of open source tools to predict small RNA functions"""
from os import path as op
from bcbio.distributed import transaction
import os
import shutil

import utils
import logger as mylog
from read import get_loci_fasta, make_temp_directory
from do import run


logger = mylog.getLogger(__name__)


def make_predictions(clus_obj, out_dir, args):
    """
    Iterates through cluster precursors to predict sRNA types
    """
    ref = os.path.abspath(args.reference)
    utils.safe_dirs(out_dir)
    for nc in clus_obj[0]:
        c = clus_obj[0][nc]
        loci = c['loci']
        out_fa = "cluster_" + nc
        if loci[0][3] - loci[0][2] < 500:
            with make_temp_directory() as tmpdir:
                os.chdir(tmpdir)
                get_loci_fasta({loci[0][0]: [loci[0][0:5]]}, out_fa, ref)
                summary_file, str_file = _run_tRNA_scan(out_fa)
                # c['predictions']['tRNA'] = _read_tRNA_scan(summary_file)
                score = _read_tRNA_scan(summary_file)
                logger.debug(score)
                # shutil.move(summary_file, op.join(out_dir, summary_file))
                # shutil.move(str_file, op.join(out_dir, str_file))
        else:
            c['errors'].add("precursor too long")
        clus_obj[0][nc] = c

    return clus_obj


def _read_tRNA_scan(summary_file):
    """
    Parse output from tRNA_Scan
    """
    score = 0
    if os.path.getsize(summary_file) == 0:
        return 0
    with open(summary_file) as in_handle:
        header = in_handle.next().strip().split()
        for line in in_handle:
            if not line.startswith("--"):
                pre = line.strip().split()
                score = pre[-1]
    return score


def _run_tRNA_scan(fasta_file):
    """
    Run tRNA-scan-SE to predict tRNA
    """
    out_file = fasta_file + "_trnascan"
    se_file = fasta_file + "_second_str"
    cmd = "tRNAscan-SE -q -o {out_file} -f {se_file} {fasta_file}"
    run(cmd.format(**locals()))
    return out_file, se_file
