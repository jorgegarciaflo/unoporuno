#!/bin/sh
java weka.filters.supervised.instance.SpreadSubsample -M 1 -c last -i training/600.strong.99.arff  > training/600.strong.spread.99.arff

rm -f models/*
echo 'training SMO model'
java weka.classifiers.meta.FilteredClassifier -F weka.filters.unsupervised.attribute.RemoveType -W weka.classifiers.functions.SMO -t training/600.strong.spread.99.arff -d models/weka.classifiers.functions.SMO.data.model

