import os,re,pysam
import mappy as mp
from statistics import mean
from tempfile import NamedTemporaryFile

ALIGNFILTER=0x900

class SimpleRecord:
    def __init__(self,name,seq,qual,flag):
        self.query_name     = name
        self.query_sequence = seq
        self.rq             = self._getQual(qual)
        self.flag           = flag
    def _getQual(self,phred):
        return mean([1-10**(-q/10) for q in phred])
    def get_tag(self,tag):
        return self.rq

def extractRegion(inBAM,reference,region=None,ctg=None,start=None,stop=None,flanksize=100):
    ref = pysam.FastaFile(reference)
    bam = pysam.AlignmentFile(inBAM)
    if region:
        try:
            ctg,start,stop = getCoordinates(region)
        except AttributeError as e:
            #catch when the region format doesn't match
            raise Extract_Exception(f'Invalid region format {region}. Correct \'[chr]:[start]-[stop]\'') from None
    elif ctg==None or start==None or stop==None:
            #catch when missing coord and no region passed
            raise Extract_Exception('Must pass either valid region string or all of ctg,start,stop')

    aligner,tmp = getFlankAligner(ref,ctg,start-1,stop,flanksize=flanksize) 
    
    try:
        for rec in bam.fetch(ctg,start,stop):
            if (rec.flag & ALIGNFILTER):
                continue
            rStart,rStop,subseq = extractRepeat(rec.query_sequence,aligner)
            if rStart and rStop:
                name = f'{rec.query_name}/{rStart}_{rStop}'
                qual = rec.query_qualities[rStart:rStop]
                yield SimpleRecord(name,subseq,qual,rec.flag)
    finally:
        os.remove(tmp.name)

def getCoordinates(regionString):
    ctg,start,stop = re.search('(.*):(\d+)-(\d+)',regionString).groups()
    return ctg.strip(),int(start),int(stop)

def getFlanks(ref,ctg,start,stop,flanksize=100,Lflank=None,Rflank=None):
    '''Extract flanking sequence from BED regions, given a pysam.FastaFile with .fai'''
    Lsize    = Lflank if Lflank else flanksize
    Rsize    = Rflank if Rflank else flanksize
    sequence = ref.fetch(ctg,start-Lsize,stop+Rsize)
    return [sequence[:Lsize],sequence[-Rsize:]]

def getFlankAligner(ref,ctg,start,stop,**kwargs):
    tmpRef = NamedTemporaryFile(mode='w',delete=False)
    for side,seq in zip(['L','R'],getFlanks(ref,ctg,start,stop,**kwargs)):
        tmpRef.write('>{n}\n{s}\n'.format(n='_'.join([str(ctg),side]),s=seq))
    tmpRef.close()
    aligner = mp.Aligner(tmpRef.name,preset='sr')
    return aligner,tmpRef

def getSubSeq(seq,aln):
    pos = sorted([getattr(a,att) for a in aln for att in ['q_st','q_en']])[1:-1]
    return pos + [seq[slice(*pos)]]

def extractRepeat(sequence,aligner):
    aln = list(aligner.map(sequence))
    naln = len(aln)
    if naln == 2:
        start,stop,seq = getSubSeq(sequence,aln)
        #seq = getSubSeq(sequence,aln)
        if aln[0].strand == -1:
            seq = rc(seq)
    else:
        seq = 'One Sided' if naln==1 else 'Poor/no Alignment'
        start,stop = None,None
    return start,stop,seq

_RC_MAP = dict(zip('-ACGNTacgt','-TGCNAtgca'))

def rc(seq):
    '''revcomp'''
    return "".join([_RC_MAP[c] for c in seq[::-1]])

class Extract_Exception(Exception):
    pass
