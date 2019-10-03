#! ~/anaconda3/bin/python

import os,sys

from src.model.kmer   import *
from src.model.models import MODELS
from src.utils.bam import addHPtag
from src.utils.extract import Extract_Exception

DEFAULTMODEL    = 'dbscan'
DEFAULTKMER     = 11
DEFAULTNORM     = 'l1'
DEFAULTMINREADS = 5
DEFAULTCOMP     = 2
DEFAULTEPS      = 0.0
DEFAULTSIMP     = 0.0
DEFAULTPREFIX   = './clustered'
CLUSTNAME       = 'cluster{0}_numreads{1}'.format #args: int,int


def main(parser):
    args = parser.parse_args()
    if args.normalize == 'none':
        args.normalize = None

    #load dataframe with samples(row) by kmer counts (cols)
    data = loadKmers(args.inBAM,args.minQV,args.kmer,
                     collapse   =args.hpCollapse,
                     region     =args.region,
                     minimizer  =args.minimizer,
                     ignoreEnds =args.ignoreEnds,
                     whitelist  =args.whitelist,
                     flanks     =args.flanks,
                     simpson    =args.simpson,
                     norm       =args.normalize,
                     components =args.components,
                     agg        =args.agg,
                     extractRef =args.reference)

    if args.testPlot:
        #plot kdist and exit
        from src.figures.kdist import plotEPS
        print("Plotting distance to m-neighbors")
        f = plotEPS(data,args.minReads,args.normalize)
        f.savefig(f'{args.prefix}.eps_estimator.png')
        return data
    
    #Clustering
    cluster     = MODELS[args.model](args)
    print(f'Clustering {len(data)} reads with {args.model}\n{printParams(cluster)}')
    result      = cluster.fit(data)
    clusterIdx  = result.labels_

    #TODO
    #cluster size and warning if too much noise as frac of total

    #write cluster file
    with open(f'{args.prefix}.clusters.txt', 'w') as namefile:
        grouped = data.groupby(clusterIdx)
        cnts    = sorted([len(idx) for c,idx in grouped.groups.items() if c!=-1],reverse=True)
        print(f'Writing clusters with nreads {",".join(map(str,cnts))}')
        if -1 in grouped.groups:
            print(f'{len(grouped.groups[-1])} reads identified as noise')
        for cluster,reads in grouped:
            nreads = len(reads)
            name = f'Noise_numreads{nreads}' if cluster==-1 else CLUSTNAME(cluster,nreads)
            namefile.write(f'>{name}\n')
            namefile.write('\n'.join(reads.index) + '\n')
    
    if not args.noBam:
        print("Adding HP tag to bam")
        clusterMap = dict(zip(data.index,clusterIdx))
        outBam     = f'{args.prefix}.hptagged.bam'
        addHPtag(args.inBAM,outBam,clusterMap,dropNoClust=args.drop,splitBam=args.splitBam)

    if args.plotReads:
        from src.figures.cluster import plotReads 
        fig = plotReads(data,clusterIdx)
        fig.savefig(f'{args.prefix}.clusters.png')
    
    return None

def printParams(model):
    return '\n'.join(['\t' + '='.join(map(str,v)) for v in model.defaults.items()])

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='ClusterAmplicons.py', description='Clustering by kmer counts')
    parser.add_argument('inBAM', metavar='inBAM', type=str,
                    help='input BAM of CCS alignments')
    parser.add_argument('-j,--njobs', dest='njobs', type=int, default=None,
                    help='j parallel jobs (only for some models). Default 1')
    kmer = parser.add_argument_group('kmers')
    kmer.add_argument('-k,--kmer', dest='kmer', type=int, default=DEFAULTKMER,
                    help=f'kmer size for clustering. Default {DEFAULTKMER}')
    kmer.add_argument('-z,--minimizer', dest='minimizer', type=int, default=0,
                    help='group kmers by minimizer of length z. Default 0 (no minimizer)')
    kmer.add_argument('-H,--noHPcollapse', dest='hpCollapse', action='store_false', default=True,
                    help='do not compress homopolymers.  Default collapse HP')
    clust = parser.add_argument_group('cluster')
    clust.add_argument('-M,--model', dest='model', type=str, choices=MODELS.keys(), default=DEFAULTMODEL,
                    help=f'clustering model. See https://scikit-learn.org/stable/modules/clustering.html. Default {DEFAULTMODEL}')
    clust.add_argument('-a,--agg', dest='agg', type=str, choices=['pca','featagg'],default='pca',
                    help='Feature reduction method. Default pca')
    clust.add_argument('-c,--components', dest='components', type=int, default=DEFAULTCOMP,
                    help=f'Use first c components of PCA/FeatAgg for clustering. Set to 0 for no reduction. Default {DEFAULTCOMP}')
    clust.add_argument('-e,--eps', dest='eps', type=float, default=None,
                    help='eps cluster tolerance. Default None')
    clust.add_argument('-m,--minReads', dest='minReads', type=int, default=DEFAULTMINREADS,
                    help=f'Minimum reads to be a cluster. Default {DEFAULTMINREADS}')
    clust.add_argument('-n,--normalize', dest='normalize', type=str, choices=['l1','l2','none'], default=DEFAULTNORM,
                    help=f'normalization of kmer counts.  Default {DEFAULTNORM}')
    clust.add_argument('-i,--ignoreEnds', dest='ignoreEnds', type=int, default=0,
                    help='ignore i bases at ends of amplicons for clustering.  Default 0')
    clust.add_argument('-P,--params', dest='params', type=str, default=None,
                    help='json file of parameters for specific model. Order of precedence: CL-opts > json > defaults. Default None')
    filt = parser.add_argument_group('filter')
    filt.add_argument('-r,--region', dest='region', type=str, default=None,
                    help='Target region for selection of reads, format \'[chr]:[start]-[stop]\'.  Example \'4:3076604-3076660\'. \nDefault all reads (no region)')
    filt.add_argument('--extractReference', dest='reference', type=str, default=None,
                    help='Extract subsequence at region coordinates for clustering using fasta reference (must have .fai). Maps 100nt on either side of region to each read and extracts sequence inbetween for kmer counting. \nDefault None (use full read)')
    filt.add_argument('-q,--minQV', dest='minQV', type=float, default=0.99,
                    help='Minimum quality [0-1] to use for clustering. Default 0.99')
    filt.add_argument('-s,--simpsonDominance', dest='simpson', type=float, default=DEFAULTSIMP,
                    help=f'Dominance filter for kmers.  Remove kmers with > s (dominance). Default {DEFAULTSIMP:.2f} (no filter)')
    filt.add_argument('-w,--whitelist', dest='whitelist', type=str, default=None,
                    help='whitelist of read names to cluster. Default None')
    filt.add_argument('-f,--flanks', dest='flanks', type=str, default=None,
                    help='fasta of flanking/primer sequence. Reads not mapping to both will be filtered. Default None')
    out = parser.add_argument_group('output')
    out.add_argument('-p,--prefix', dest='prefix', type=str, default=DEFAULTPREFIX,
                    help=f'Output prefix. Default {DEFAULTPREFIX}')
    out.add_argument('-S,--splitBam', dest='splitBam', action='store_true',
                    help='split clusters into separate bams (noise and no-cluster dropped). Default one bam')
    out.add_argument('-x,--noBam', dest='noBam', action='store_true',
                    help='Do not export HP-tagged bam of clustered reads')
    out.add_argument('-d,--drop', dest='drop', action='store_true',
                    help='Drop reads with no cluster in output bam.  Default keep all reads.')
    out.add_argument('-t,--testPlot', dest='testPlot', action='store_true',
                    help='Plot reads vs dist to nearest m-neighbors without clustering')
    out.add_argument('-g,--plotReads', dest='plotReads', action='store_true',
                    help='Plot first 2 axes of PCA for each read.  Default no plot generated')

    try:
        main(parser)
    except (Clustering_Exception,Kmer_Exception,Extract_Exception) as e:
        print(f'ERROR: {e}')
        sys.exit(1)
