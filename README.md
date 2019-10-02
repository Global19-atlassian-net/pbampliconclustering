Under Construction

    $ py3 ClusterAmplicons.py -h
    usage: ClusterAmplicons.py [-h] [-j,--njobs NJOBS] [-k,--kmer KMER]
                               [-z,--minimizer MINIMIZER] [-H,--noHPcollapse]
                               [-M,--model {dbscan,optics,aggcluster,affprop,meanshift,kmeans}]
                               [-a,--agg {pca,featagg}]
                               [-c,--components COMPONENTS] [-e,--eps EPS]
                               [-m,--minReads MINREADS]
                               [-n,--normalize {l1,l2,none}]
                               [-i,--ignoreEnds IGNOREENDS] [-r,--region REGION]
                               [-q,--minQV MINQV] [-s,--simpsonDominance SIMPSON]
                               [-w,--whitelist WHITELIST] [-f,--flanks FLANKS]
                               [-p,--prefix PREFIX] [-S,--splitBam] [-x,--noBam]
                               [-d,--drop] [-t,--testPlot] [-g,--plotReads]
                               inBAM
    
    Clustering by kmer counts
    
    positional arguments:
      inBAM                 input BAM of CCS alignments
    
    optional arguments:
      -h, --help            show this help message and exit
      -j,--njobs NJOBS      j parallel jobs (only for OPTICS). Default 1
    
    kmers:
      -k,--kmer KMER        kmer size for clustering. Default 11
      -z,--minimizer MINIMIZER
                            group kmers by minimizer of length z. Default 0 (no
                            minimizer)
      -H,--noHPcollapse     do not compress homopolymers. Default collapse HP
    
    cluster:
      -M,--model {dbscan,optics,aggcluster,affprop,meanshift,kmeans}
                            clustering model. See https://scikit-
                            learn.org/stable/modules/clustering.html#clustering.
                            Default dbscan
      -a,--agg {pca,featagg}
                            Feature reduction method. Default pca
      -c,--components COMPONENTS
                            Use first c components of PCA/FeatAgg for clustering.
                            Set to 0 for no reduction. Default 2
      -e,--eps EPS          eps cluster tolerance. Default None
      -m,--minReads MINREADS
                            Minimum reads to be a cluster. Default 5
      -n,--normalize {l1,l2,none}
                            normalization of kmer counts. Default l1
      -i,--ignoreEnds IGNOREENDS
                            ignore i bases at ends of amplicons for clustering.
                            Default 0
    
    filter:
      -r,--region REGION    Target region for selection of reads, format
                            '[chr]:[start]-[stop]'. Example '4:3076604-3076660'.
                            Default all reads (no region)
      -q,--minQV MINQV      Minimum quality [0-1] to use for clustering. Default
                            0.99
      -s,--simpsonDominance SIMPSON
                            Dominance filter for kmers. Remove kmers with > s
                            (dominance). Default 0.00 (no filter)
      -w,--whitelist WHITELIST
                            whitelist of reads to cluster. Default None
      -f,--flanks FLANKS    fasta of flanking/primer sequence. Reads not mapping
                            to both will be filtered. Default None
    
    output:
      -p,--prefix PREFIX    Output prefix. Default ./clustered
      -S,--splitBam         split clusters into separate bams (noise and no-
                            cluster dropped). Default one bam
      -x,--noBam            Do not export HP-tagged bam of clustered reads
      -d,--drop             Drop reads with no cluster in output bam. Default keep
                            all reads.
      -t,--testPlot         Plot reads vs dist to nearest m-neighbors without
                            clustering
      -g,--plotReads        Plot first 2 axes of PCA for each read. Default no
                            plot generated 
    
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
