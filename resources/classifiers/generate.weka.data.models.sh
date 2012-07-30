java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.trees.NBTree -t training/102.mobility.resample.arff -d nbtree/NBTree.data.model

java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.bayes.NaiveBayes -t training/102.mobility.resample.arff -d naivebayes/NaiveBayes.data.model

java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.trees.J48 -t training/102.mobility.resample.arff -d j48/J48.data.model


java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.functions.SMO -t training/102.mobility.resample.arff -d smo/SMO.data.model

