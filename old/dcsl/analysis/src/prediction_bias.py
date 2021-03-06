import util

from analysis_module import AnalysisModule

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class PredictionBias(AnalysisModule):
    def __init__(self):
        self._name = 'PredictionBias'
        AnalysisModule.__init__(self)
        
    def analyze(self, train_data, test_data, models):
        keys = ['application']
        error = dict(application=[], model=[], model_nice_name=[], error=[])
        grouped = test_data.groupby(keys)
        for app, group in grouped:
            y=group['time']
            X = util.get_predictors(group).values
            for model_name in models[app]:
                model = models[app][model_name]
                pred = model.predict(X)

                res = util.relative_error(y, pred)
                for err in res.values:
                    error['error'].append(err)
                    error['model'].append(model_name)
                    error['model_nice_name'].append(str(model))
                    error['application'].append(app)
        self.error = pd.DataFrame(error)
        return self
       
    def plot(self, prefix, suffix):
        grid = sns.FacetGrid(self.error, col='model')
        grid.map(plt.hist, 'error', bins=40)
        grid.add_legend()
        grid.set_xlabels('Relative Error (%)')
        plt.savefig('%s_bias.%s' % (prefix, suffix))
        return self
