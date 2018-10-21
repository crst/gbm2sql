import argparse
import sys
import time

import xgboost as xgb


def compute_predictions(model_file, predictions_file):
    try:
        dtrain = xgb.DMatrix('agaricus.txt.train', silent=True)
        dtest = xgb.DMatrix('agaricus.txt.test', silent=True)
    except xgb.core.XGBoostError as err:
        print('Could not load demo data: %s' % err)
        return False

    param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'reg:logistic'}
    num_round = 2
    bst = xgb.train(param, dtrain, num_round)
    bst.save_model(model_file)

    t0 = time.time()
    try:
        preds = bst.predict(dtest)
    except xgb.core.XGBoostError as err:
        print('Could not compute predictions: %s' % err)
        return False

    try:
        with open(predictions_file, 'w') as f:
            for i, p in enumerate(preds):
                f.write('%s,%.4f\n' % (i, p))
    except IOError as err:
        print('Could not write predictions: %s' % err)
        return False
    t1 = time.time()
    duration = 1000 * (t1 - t0)

    print('Computed and wrote XGBoost predictions to %s in %.3fms' % (predictions_file, duration))
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-file', default='demo_model.xgb',
                        help='The name of the trained demo model.')
    parser.add_argument('--predictions-file', default='xgb_predictions.csv',
                        help='The name of the computed predictions file.')
    args = parser.parse_args()

    success = compute_predictions(args.model_file, args.predictions_file)
    if not success:
        sys.exit(1)
    sys.exit(0)
