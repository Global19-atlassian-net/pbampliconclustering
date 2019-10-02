from sklearn.cluster import DBSCAN,\
                            OPTICS, \
                            AgglomerativeClustering, \
                            AffinityPropagation, \
                            KMeans, \
                            MeanShift
import numpy as np
from collections import Counter
import json

class ClusterModel:
    '''
    defaults: { modelKwargs     : defaultValue }
    pmap    : { CommandLineArgs : modelKwargs } 
    
    returns : parameterized model instance with fit method 
    '''
    defaults = {}
    pmap     = {}
    MODEL    = None

    def __init__(self,args):
        #load json first to override defaults
        if args.params:
            with open(args.params) as configFile:
                config = json.load(configFile)
            self.defaults.update(config)
        #override again with CL if not None or 0
        self.defaults.update({mparam:getattr(args,aparam) 
                              for aparam,mparam in self.pmap.items() 
                              if getattr(args,aparam)})
        self.model = self.MODEL(**self.defaults)
    def fit(self,X):
        return self.model.fit(X)

class ClusterModel_wNoise(ClusterModel):
    '''
    Subclass for models without a min cluster size.
    Re-labels small clusters < minReads to noise (-1)
    '''
    def __init__(self,args):
        self.minCnt = args.minReads
        super().__init__(args)
    def fit(self,X):
        res = self.model.fit(X)
        for val,count in Counter(res.labels_).items():
            if count < self.minCnt:
                res.labels_[res.labels_==val] = -1
        return res

class Dbscan(ClusterModel):
    MODEL    = DBSCAN
    defaults = {'eps'        : 0.01,
                'min_samples': 3,
                'metric'     : 'euclidean'}
    pmap     = {'eps'        : 'eps',
                'minReads'   : 'min_samples',
                'njobs'      : 'n_jobs'}

class Optics(ClusterModel):
    MODEL    = OPTICS
    defaults = {'max_eps'    : np.inf,
                'min_samples': 3,
                'n_jobs'     : 1,
                'metric'     : 'l2',
                'xi'         : 0.1}
    pmap     = {'eps'        : 'max_eps',
                'minReads'   : 'min_samples',
                'njobs'      : 'n_jobs',
                'normalize'  : 'metric'}

class Kmeans(ClusterModel):
    MODEL    = KMeans
    defaults = {'n_clusters'  : 2,
                'max_iter'    : 300,
                'tol'         : 1e-4,
                'random_state': None,
                'n_jobs'      : 1}
    pmap     = {'eps'         : 'tol',
                'njobs'       : 'n_jobs'}                

class Aggcluster(ClusterModel_wNoise):
    MODEL    = AgglomerativeClustering
    defaults = {'affinity'          : 'euclidean',
                'compute_full_tree' : True,
                'distance_threshold': 0.01,
                'n_clusters'        : None}
    pmap     = {'eps':'distance_threshold'}

class Affprop(ClusterModel_wNoise):
    MODEL    = AffinityPropagation
    defaults = {'damping' : 0.5}
    pmap     = {'eps'     : 'damping'}

    def __init__(self,args):
        if args.eps and (args.eps < 0.5 or args.eps >1):
            raise Clustering_Exception('Damping (-e) must be in [0.5-1] for AffinityPropagation')
        super().__init__(args)

class Meanshift(ClusterModel):
    MODEL    = MeanShift
    defaults = {'bandwidth'   : None, #estimate from data
                'bin_seeding' : True,
                'min_bin_freq': 3,
                'cluster_all' : False,
                'n_jobs'      : 2}
    pmap     = {'eps'         : 'bandwidth',
                'minReads'    : 'min_bin_freq',
                'njobs'       : 'n_jobs'}

MODELS = {'dbscan'    : Dbscan,
          'optics'    : Optics,
          'aggcluster': Aggcluster,
          'affprop'   : Affprop,
          'meanshift' : Meanshift,
          'kmeans'    : Kmeans}

class Clustering_Exception(Exception):
    pass

