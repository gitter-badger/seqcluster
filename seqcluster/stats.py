import os
import pysam
import logging
import json
from libs.tool import parse_ma_file
from libs.sam2bed import makeBED
from collections import defaultdict, Counter

logger = logging.getLogger('stats')


def stats(args):
    """Create stats from the analysis
    """
    logger.info("Reading sequeces")
    data = parse_ma_file(args.ma)
    logger.info("Get sequences from sam")
    is_align = _read_sam(args.sam)
    is_json = _read_json(args.json)
    res = _summarise_sam(data, is_align, is_json)
    _write_suma(res, os.path.join(args.out, "stats_align.dat"))
    logger.info("Done")


def _read_sam(sam):
    is_align = set()
    with pysam.Samfile(sam, "rb") as samfile:
        for a in samfile.fetch():
            a = makeBED(a)
            if a:
                is_align.add(a.name)
    return is_align


def _read_json(fn_json):
    """read json information"""
    is_json = set()
    with open(fn_json) as handle:
        data = json.load(handle)
        for item in data[0].values():
            seqs_name = map(lambda (x): x.keys(), item['seqs'])
            [is_json.add(name[0]) for name in seqs_name]
    return is_json


def _summarise_sam(counts, is_align, is_json):
    summary_align = defaultdict(Counter)
    summary_json = defaultdict(Counter)
    for s, o in counts.iteritems():
        l = len(o.seq)
        if s in is_align:
            summary_align[l].update(o.freq)
        if s in is_json:
            summary_json[l].update(o.freq)
    return [summary_align, summary_json]


def _write_suma(d, fn):
    with open(fn, 'w') as handle:
        for l, counts in d[0].iteritems():
            for e, freq in counts.iteritems():
                handle.write("%s %s %s align\n" % (l, e, freq))
        for l, counts in d[1].iteritems():
            for e, freq in counts.iteritems():
                handle.write("%s %s %s json\n" % (l, e, freq))