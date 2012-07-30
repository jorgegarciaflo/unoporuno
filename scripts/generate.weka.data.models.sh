java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.trees.NBTree -t 102.mobility.resample.arff -d NBTree.data.model

java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.bayes.NaiveBayes -t 102.mobility.resample.arff -d NaiveBayes.data.model

java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.trees.J48 -t 102.mobility.resample.arff -d J48.data.model


java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.functions.SMO -t 102.mobility.resample.arff -d SMO.data.model

