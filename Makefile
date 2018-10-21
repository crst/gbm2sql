
run-demo: gbm-predictions convert-gbm-to-sql import-sql-data sql-predictions


gbm-predictions:
	python gbm_demo.py --model-file=demo_model.xgb --predictions-file=xgb_predictions.csv

convert-gbm-to-sql:
	python convert_demo_data.py --demo-data-file=demo_data.sql
	python gbm2sql.py --model-file=demo_model.xgb --sql-file=demo_model.sql

import-sql-data:
	psql postgres -c "CREATE DATABASE gbm2sql_demo;"
	psql gbm2sql_demo -c "CREATE SCHEMA gbm;"
	psql gbm2sql_demo -f demo_data.sql
	psql gbm2sql_demo -f demo_model.sql

sql-predictions:
	psql gbm2sql_demo -v TIMING=ON -A -t -F ',' -f sql_demo.sql -o sql_predictions.csv
	@echo "Wrote SQL predictions to sql_predictions.csv"
	@echo "Number of different predictions:"
	diff xgb_predictions.csv sql_predictions.csv | wc -l
