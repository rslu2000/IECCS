import os
import sys
sys.path.append(os.path.abspath(__file__ + "/../../"))

import numpy as np
import pandas as pd
from glob import glob
from System.DataProcessing.GloveVectorizer.glove_transformer import GloveVectorizer
import System.DataProcessing.process_data as ptd

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.cross_validation import cross_val_predict, StratifiedKFold
from sklearn.metrics import fbeta_score
from sklearn.ensemble import VotingClassifier

validate = 1
testing = 0

data = pd.read_csv(open('../TextFiles/data/tcp_train.csv'), sep='\t', index_col=0)
val = pd.read_csv(open('../TextFiles/data/tcp_validate.csv'), sep='\t', index_col=0)
test = pd.read_csv(open('../TextFiles/data/tcp_test.csv'), sep='\t', index_col=0)

print("using down sampling")
print 'Downsample favor: ' + str(0.2)
print 'Downsample none: ' + str(0.4)
#test_data = ptd.getTestData()
sub_favor = ptd.getDownsample2_0(data, "FAVOR", "soft", 0.2)
sub_none = ptd.getDownsample2_0(data, "NONE", "soft", 0.4)
against = data[data.Stance == "AGAINST"]

data = pd.concat([sub_favor, sub_none, against])

#glove_fnames1 = glob('../DataProcessing/GloveVectorizer/vectors/glove.6B.300d_tcp_abstracts.pkl')
glove_fnames = glob('../DataProcessing/GloveVectorizer/vectors/glove.840B.300d_tcp_abstracts.pkl')
#glove_fnames = glove_fnames1 + glove_fnames2
print glove_fnames

glove_ids = [fname.split('/')[-1].split('_')[0] for fname in glove_fnames]

# *****     FINDING BEST VECTOR SPACE     *****
for fname, glove_id in zip(glove_fnames, glove_ids):
    print 80 * '='
    print 'GLOVE VECTORS:', glove_id
    print 80 * '='

    glove_vecs = pd.read_pickle(fname)

    glove_clf = Pipeline([('vect', GloveVectorizer(glove_vecs)),
                          ('clf', LogisticRegression(C=0.83,
                                                     solver='lbfgs',
                                                     multi_class='multinomial',
                                                     class_weight='balanced',
                                                     ))])

    char_clf = Pipeline([('vect', CountVectorizer(analyzer="word",
                                                  ngram_range=(1, 2),
                                                  stop_words=None,
                                                  max_features=None,
                                                  decode_error='ignore')),
                         #('tfidf', TfidfTransformer(use_idf=False)),
                         ('clf', SVC(C=5.2, kernel='linear', probability=True))
                         ])

    vot_clf = VotingClassifier(estimators=[('glove', glove_clf),
                                             ('linear', char_clf)],
                                     voting='soft')

    print char_clf.named_steps

    print "TRAIN"
    print 80 * '='
    cv = StratifiedKFold(data.Stance, n_folds=10, shuffle=True, random_state=1)

    pred_stances = cross_val_predict(vot_clf, data.Abstract, data.Stance, cv=cv)

    print classification_report(data.Stance, pred_stances, digits=4)

    macro_f = fbeta_score(data.Stance, pred_stances, 1.0,
                          labels=['AGAINST', 'FAVOR', 'NONE'],
                          average='macro')

    print 'macro-average of F-score(FAVOR) and F-score(AGAINST): {:.4f}\n'.format(macro_f)

    print "VALIDATE"
    print 80 * '='

    vot_clf.fit(data.Abstract, data.Stance)

    pred_stances = vot_clf.predict(val.Abstract)

    print classification_report(val.Stance, pred_stances, digits=4)

    macro_f = fbeta_score(val.Stance, pred_stances, 1.0,
                          labels=['AGAINST', 'FAVOR', 'NONE'],
                          average='macro')

    print 'macro-average of F-score(FAVOR) and F-score(AGAINST): {:.4f}\n'.format(macro_f)

    testing = 1
    if testing:
        print "TEST"
        print 80 * '='
        merged = pd.concat([data, val])
        vot_clf.fit(merged.Abstract, merged.Stance)

        pred_stances = vot_clf.predict(test.Abstract)

        print classification_report(test.Stance, pred_stances, digits=4)

        macro_f = fbeta_score(test.Stance, pred_stances, 1.0,
                              labels=['AGAINST', 'FAVOR', 'NONE'],
                              average='macro')

        print 'macro-average of F-score(FAVOR) and F-score(AGAINST): {:.4f}\n'.format(macro_f)