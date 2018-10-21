import argparse
import json
import sys

import xgboost as xgb


def gbm2sql(model_file, model_schema, model_table, sql_file, with_ddl, with_constraints):
    try:
        model = xgb.Booster(model_file=model_file)
    except xgb.core.XGBoostError as err:
        print('Could not load model file: %s' % err)
        return False

    boosters = model.get_dump(dump_format='json')
    sql_nodes = []

    for booster_id, booster in enumerate(boosters):
        bst = json.loads(booster)

        gbm_nodes = [bst]
        while len(gbm_nodes) != 0:
            node = gbm_nodes.pop()
            sql_nodes.append([
                "'%s'" % model_file,
                booster_id,
                node['nodeid'],
                node.get('split', 'NULL'),
                node.get('split_condition', 'NULL'),
                node.get('yes', 'NULL'),
                node.get('no', 'NULL'),
                node.get('missing', 'NULL'),
                node.get('leaf', 'NULL')
            ])
            gbm_nodes.extend(node.get('children', []))

    sql = []

    if with_ddl:
        sql.append('''CREATE TABLE IF NOT EXISTS %(model_schema)s.%(model_table)s (
  model_name    VARCHAR NOT NULL,
  booster_id    INTEGER NOT NULL,
  node_id       INTEGER NOT NULL,
  feature_index INTEGER,
  split         DOUBLE PRECISION,
  node_yes      INTEGER,
  node_no       INTEGER,
  node_missing  INTEGER,
  prediction    DOUBLE PRECISION
);\n
''' % ({'model_schema': model_schema, 'model_table': model_table}))

    if with_constraints:
        sql.append('''ALTER TABLE %(model_schema)s.%(model_table)s
  ADD PRIMARY KEY (model_name, booster_id, node_id);

ALTER TABLE %(model_schema)s.%(model_table)s
  ADD FOREIGN KEY (model_name, booster_id, node_yes) REFERENCES %(model_schema)s.%(model_table)s (model_name, booster_id, node_id);

ALTER TABLE %(model_schema)s.%(model_table)s
  ADD FOREIGN KEY (model_name, booster_id, node_no) REFERENCES %(model_schema)s.%(model_table)s (model_name, booster_id, node_id);

ALTER TABLE %(model_schema)s.%(model_table)s
  ADD FOREIGN KEY (model_name, booster_id, node_missing) REFERENCES %(model_schema)s.%(model_table)s (model_name, booster_id, node_id);\n
''' % {'model_schema': model_schema, 'model_table': model_table})

    sql.append('INSERT INTO %s.%s VALUES\n' % (model_schema, model_table))
    for node in sql_nodes:
        sql.append('  (%s)' % (', '.join(map(str, node))))
        sql.append(',\n')
    sql[-1] = ';\n'

    try:
        with open(sql_file, 'w') as f:
            f.write(''.join(sql))
    except IOError as err:
        print('Could not write SQL file: %s' % err)
        return False

    print('Wrote converted model to %s' % sql_file)
    return True



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-file', default='model.xgb',
                        help='The XGBoost model to convert.')
    parser.add_argument('--model-schema', default='gbm',
                        help='The database schema of the model table.')
    parser.add_argument('--model-table', default='model',
                        help='The name of the model table.')
    parser.add_argument('--sql-file', default='model.sql',
                        help='The name of the generated SQL file.')
    parser.add_argument('--with-ddl', default=True,
                        help='If the table DDL should be included.')
    parser.add_argument('--with-constraints', default=True,
                        help='If table constraints should be included.')
    args = parser.parse_args()

    success = gbm2sql(
        args.model_file,
        args.model_schema,
        args.model_table,
        args.sql_file,
        args.with_ddl,
        args.with_constraints
    )

    if not success:
        sys.exit(1)
    sys.exit(0)
