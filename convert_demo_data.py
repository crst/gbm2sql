import argparse
import sys


def convert_demo_data(source_data_file, demo_schema, demo_data_table, demo_data_file):
    sql = ['''
CREATE TABLE %(demo_schema)s.%(demo_data_table)s(
  sample_id        INTEGER NOT NULL,
  prediction_truth INTEGER,
  feature_values   INTEGER[126] NOT NULL
);

ALTER TABLE %(demo_schema)s.%(demo_data_table)s
  ADD PRIMARY KEY (sample_id);\n
''' % {'demo_schema': demo_schema, 'demo_data_table': demo_data_table}]

    sql.append('INSERT INTO %(demo_schema)s.%(demo_data_table)s VALUES\n'
           % {'demo_schema': demo_schema, 'demo_data_table': demo_data_table})
    try:
        with open(source_data_file, 'r') as f:
            for sample_id, row in enumerate(f):
                data = row.split(' ')
                prediction_truth = data[0]
                feature_values = ['NULL' for _ in range(126)]
                for d in data[1:]:
                    idx, val = map(int, d.split(':'))
                    feature_values[idx - 1] = val
                feature_values = 'Array[%s]' % (', '.join(map(str, feature_values)))
                sql.append('  (%s, %s, %s)' % (sample_id, prediction_truth, feature_values))
                sql.append(',\n')
            sql[-1] = ';'
    except IOError as err:
        print('Could not convert demo data: %s' % err)
        return False

    try:
        with open(demo_data_file, 'w') as f:
            f.writelines(''.join(sql))
    except IOError as err:
        print('Could not write converted demo data: %s' % err)
        return False
    print('Wrote converted data to %s.sql' % (source_data_file))

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-data-file', default='agaricus.txt.test',
                        help='')
    parser.add_argument('--demo-schema', default='gbm',
                        help='The database schema for the demo data.')
    parser.add_argument('--demo-data-table', default='features',
                        help='The name of the demo data table.')
    parser.add_argument('--demo-data-file', default='demo_data.sql',
                        help='The file for the demo data.')
    args = parser.parse_args()

    success = convert_demo_data(
        args.source_data_file,
        args.demo_schema,
        args.demo_data_table,
        args.demo_data_file
    )
    if not success:
        sys.exit(1)
    sys.exit(0)
