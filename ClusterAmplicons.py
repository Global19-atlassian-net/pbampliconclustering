#! ~/anaconda3/bin/python

import sys,argparse
from src.main import main
from src.model.models import MODELS, \
                             showModels, \
                             Clustering_Exception
from src.model.kmer import Kmer_Exception
from src.utils.extract import Extract_Exception


DEFAULTMODEL    = 'dbscan'
DEFAULTKMER     = 11
DEFAULTNORM     = 'l2'
DEFAULTMINREADS = 5
DEFAULTCOMP     = 2
DEFAULTEPS      = 0.0
DEFAULTTRIM     = 0.1
DEFMINLEN       = 50
DEFMAXLEN       = 25000
DEFAULTPREFIX   = './clustered'

parser      = argparse.ArgumentParser(prog='ClusterAmplicons.py', description='Clustering by kmer counts')
subparsers  = parser.add_subparsers(title='subcommands')
parser_main = subparsers.add_parser('cluster', help='cluster reads')
parser_main.set_defaults(func=main)
parser_main.set_defaults(prog=f'{sys.argv[0]} cluster')
parser_desc = subparsers.add_parser('describe', help='describe models')
parser_desc.set_defaults(func=showModels)
parser_desc.set_defaults(prog=f'{sys.argv[0]} describe')
#describe
parser_desc.add_argument('-M','--model', dest='model', choices=MODELS.keys(), type=str, default=None,
                help='Show argmap and defaults for specfic model. Default None (show all)')

#cluster
parser_main.add_argument('-b','--inBAM', dest='inBAM', type=str, default=None,
                help='input BAM of CCS alignments')
parser_main.add_argument('-Q','--inFastq', dest='inFastq', type=str, default=None,
                help='input BAM of CCS alignments')
parser_main.add_argument('-j,--njobs', dest='njobs', type=int, default=None,
                help='j parallel jobs (only for some models). Default 1')
kmer = parser_main.add_argument_group('kmers')
kmer.add_argument('-k','--kmer', dest='kmer', type=int, default=DEFAULTKMER,
                help=f'kmer size for clustering. Default {DEFAULTKMER}')
kmer.add_argument('-z','--minimizer', dest='minimizer', type=int, default=0,
                help='group kmers by minimizer of length z. Default 0 (no minimizer)')
kmer.add_argument('-H','--noHPcollapse', dest='hpCollapse', nargs='?', type=int, default=1, const=0,
                help='Collapse all HP to max H length.  Default 1 (collapse all HP to length 1)')
kmer.add_argument('-T','--trim', dest='trim', type=float, default=DEFAULTTRIM,
                help=f'Trim kmers with freq < trim or freq > (1-trim). Default {DEFAULTTRIM:.2f}')
kmer.add_argument('--trimLow', dest='trimLow', type=float, default=None,
                help=f'Trim kmers with frequency < trim. Over-rides -T. Default None')
kmer.add_argument('--trimHigh', dest='trimHigh', type=float, default=None,
                help=f'Trim kmers with frequency > trimHigh. Over-rides -T. Default None')
clust = parser_main.add_argument_group('cluster')
clust.add_argument('-M','--model', dest='model', type=str, choices=MODELS.keys(), default=DEFAULTMODEL,
                help=f'clustering model. See https://scikit-learn.org/stable/modules/clustering.html. Default {DEFAULTMODEL}')
clust.add_argument('-a','--agg', dest='agg', type=str, choices=['pca','featagg'],default='pca',
                help='Feature reduction method. Default pca')
clust.add_argument('-c','--components', dest='components', type=int, default=DEFAULTCOMP,
                help=f'Use first c components of PCA/FeatAgg for clustering. Set to 0 for no reduction. Default {DEFAULTCOMP}')
clust.add_argument('-e','--eps', dest='eps', type=float, default=None,
                help='eps cluster tolerance. Default None')
clust.add_argument('-m','--minReads', dest='minReads', type=int, default=DEFAULTMINREADS,
                help=f'Minimum reads to be a cluster. Default {DEFAULTMINREADS}')
clust.add_argument('-n','--normalize', dest='normalize', type=str, choices=['l1','l2','none'], default=DEFAULTNORM,
                help=f'normalization of kmer counts.  Default {DEFAULTNORM}')
clust.add_argument('-i','--ignoreEnds', dest='ignoreEnds', type=int, default=0,
                help='ignore i bases at ends of amplicons for clustering.  Default 0')
clust.add_argument('-P','--params', dest='params', type=str, default=None,
                help='json file of parameters for specific model. Order of precedence: json > CL-opts > defaults. Default None')
filt = parser_main.add_argument_group('filter')
filt.add_argument('-r','--region', dest='region', type=str, default=None,
                help='Target region for selection of reads, format \'[chr]:[start]-[stop]\'.  Example \'4:3076604-3076660\'. \nDefault all reads (no region)')
filt.add_argument('--extractReference', dest='reference', type=str, default=None,
                help='Extract subsequence at region coordinates for clustering using fasta reference (must have .fai). Maps 100nt on either side of region to each read and extracts sequence inbetween for kmer counting. \nDefault None (use full read)')
filt.add_argument('-q','--minQV', dest='minQV', type=float, default=0.99,
                help='Minimum quality [0-1] to use for clustering. Default 0.99')
filt.add_argument('-l','--minLength', dest='minLength', type=int, default=DEFMINLEN,
                help=f'Minimum length read to use for clustering. Default {DEFMINLEN}')
filt.add_argument('-L','--maxLength', dest='maxLength', type=int, default=DEFMAXLEN,
                help=f'Maximum length read to use for clustering. Default {DEFMAXLEN}')
filt.add_argument('-w','--whitelist', dest='whitelist', type=str, default=None,
                help='whitelist of read names to cluster. Default None')
filt.add_argument('-N','--nReads', dest='nReads', type=int, default=0,
                help='Randomly downsample to nReads after filtering. Default 0 (all avail reads)')
filt.add_argument('-f','--flanks', dest='flanks', type=str, default=None,
                help='fasta of flanking/primer sequence. Reads not mapping to both will be filtered. Default None')
filt.add_argument('-A','--noArtifactFilter', dest='palfilter',  action='store_false', default=True,
                help='Turn off palindromic-artifact filtering. Default use artifact filter')
filt.add_argument('-s','--seed', dest='seed',type=int, default=17,
                help='Random seed for downsampling. Default 17')
out = parser_main.add_argument_group('output')
out.add_argument('-p','--prefix', dest='prefix', type=str, default=DEFAULTPREFIX,
                help=f'Output prefix. Default {DEFAULTPREFIX}')
out.add_argument('-S','--splitBam', dest='splitBam', action='store_true',
                help='split clusters into separate bams (noise and no-cluster dropped). Default one bam')
out.add_argument('-x','--noBam', dest='noBam', action='store_true',
                help='Do not export HP-tagged bam of clustered reads')
out.add_argument('-F','--fastq', dest='fastq', action='store_true',
                help='Export one fastq per cluster')
out.add_argument('-d','--drop', dest='drop', action='store_true',
                help='Drop reads with no cluster in output bam.  Default keep all reads.')
out.add_argument('-t','--testPlot', dest='testPlot', action='store_true',
                help='Plot reads vs dist to nearest m-neighbors without clustering')
out.add_argument('-g','--plotReads', dest='plotReads', type=int, default=None,
                help='Write pairplot of first g reduced axes for each read.  Default None (no plot)')
out.add_argument('-X','--exportKmerTable', dest='exportKmerTable', action='store_true',default=False,
                help='Export kmer count table after trimming. Default False')

try:
    args = parser.parse_args()
    if hasattr(args,'inBAM'):
        if args.inBAM=='-' and not args.noBam:
            raise Clustering_Exception('Retagging streamed bam is not supported.  Please use -x option')
        if args.inBAM and args.inFastq:
            raise Clustering_Exception('Please use either BAM or Fastq, not both')
        if not args.inFastq is None:
            if not args.noBam:
                print('Fastq Input. Turning off bam output (-x)')
                args.noBam = True
            if args.palfilter:
                print('Fastq Input. Turning off artifact filter (-A)')
                args.palfilter = False
            if args.region:
                print('Fastq Input. Ignoring region')
    if hasattr(args,'plotReads'):
        if args.plotReads == 1:
            raise Clustering_Exception('PlotReads argument cannot be 1.  Must be 0 (no plot) or >=2')
    if hasattr(args,'reference'):
        if args.reference and args.flanks:
            raise Clustering_Exception('Extracting subsequence and requiring explicit flanks is redundant.  One or the other!')
    args.func(args)
except (Clustering_Exception,Kmer_Exception,Extract_Exception) as e:
    print(f'ERROR: {e}')
    sys.exit(1)
