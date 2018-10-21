WITH recursive tree_eval AS (
  SELECT
    f.sample_id,
    m.model_name,
    m.booster_id,
    CASE
      WHEN f.feature_values[m.feature_index] <  m.split THEN m.node_yes
      WHEN f.feature_values[m.feature_index] >= m.split THEN m.node_no
      WHEN f.feature_values[m.feature_index] IS NULL THEN m.node_missing
    END AS node_id,
    m.prediction
  FROM gbm.model m
  CROSS JOIN gbm.features f
  WHERE m.model_name = 'demo_model.xgb'
    AND m.node_id = 0

  UNION ALL

  SELECT
    f.sample_id,
    p.model_name,
    p.booster_id,
    CASE
      WHEN f.feature_values[m.feature_index] <  m.split THEN m.node_yes
      WHEN f.feature_values[m.feature_index] >= m.split THEN m.node_no
      WHEN f.feature_values[m.feature_index] IS NULL THEN m.node_missing
    END AS node_id,
    m.prediction
  FROM tree_eval p
  JOIN gbm.model m USING (model_name, booster_id, node_id)
  JOIN gbm.features f USING (sample_id)
)
SELECT
  sample_id,
  (1 / (1 + exp(-sum(prediction)))) :: NUMERIC(9, 4) AS prediction
FROM tree_eval
WHERE prediction IS NOT NULL
GROUP BY sample_id
ORDER BY sample_id;
