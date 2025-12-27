# Grafana Dashboard Specifications

This document defines Grafana dashboards for monitoring Procedure Suite.
All PromQL queries assume the `proc_suite_` metric prefix.

## Dashboard 1: Coder Performance

**Purpose**: Monitor AI coding pipeline health, latency, and throughput.

### Row 1: Request Volume

#### Panel 1.1: Suggestions Generated (Time Series)
- **Type**: Graph
- **Description**: Code suggestions generated per minute, segmented by procedure type

```promql
# Total suggestions per minute
sum(rate(proc_suite_coder_suggestions_total[5m])) * 60

# By procedure type
sum by (procedure_type) (rate(proc_suite_coder_suggestions_total[5m])) * 60
```

#### Panel 1.2: LLM vs Rule-Only (Pie Chart)
- **Type**: Pie Chart
- **Description**: Proportion of requests using LLM vs rule-only

```promql
# With LLM
sum(proc_suite_coder_suggestions_total{used_llm="true"})

# Without LLM
sum(proc_suite_coder_suggestions_total{used_llm="false"})
```

#### Panel 1.3: Request Rate (Stat)
- **Type**: Stat / Single Value
- **Description**: Current requests per second

```promql
sum(rate(proc_suite_coder_suggestions_total[5m]))
```

---

### Row 2: Pipeline Latency

#### Panel 2.1: Pipeline Latency P50/P95/P99 (Time Series)
- **Type**: Graph
- **Description**: Pipeline latency percentiles over time

```promql
# P50
histogram_quantile(0.50, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m])))

# P95
histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m])))

# P99
histogram_quantile(0.99, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m])))
```

#### Panel 2.2: Latency by Procedure Type (Heatmap)
- **Type**: Heatmap
- **Description**: Latency distribution by procedure type

```promql
sum by (le, procedure_type) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m]))
```

#### Panel 2.3: Latency with LLM vs Without (Time Series)
- **Type**: Graph
- **Description**: Compare latency impact of LLM usage

```promql
# With LLM (P95)
histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket{used_llm="true"}[5m])))

# Without LLM (P95)
histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket{used_llm="false"}[5m])))
```

---

### Row 3: LLM Performance

#### Panel 3.1: LLM Latency P50/P95 (Time Series)
- **Type**: Graph
- **Description**: Isolated LLM advisor latency

```promql
# P50
histogram_quantile(0.50, sum by (le) (rate(proc_suite_coder_llm_latency_ms_bucket[5m])))

# P95
histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_llm_latency_ms_bucket[5m])))
```

#### Panel 3.2: LLM Contribution to Total Latency (Gauge)
- **Type**: Gauge
- **Description**: Percentage of total pipeline time spent in LLM

```promql
# Ratio of LLM latency to total pipeline latency (average)
(
  sum(rate(proc_suite_coder_llm_latency_ms_sum[5m])) /
  sum(rate(proc_suite_coder_llm_latency_ms_count[5m]))
) / (
  sum(rate(proc_suite_coder_pipeline_latency_ms_sum[5m])) /
  sum(rate(proc_suite_coder_pipeline_latency_ms_count[5m]))
)
```

---

### Row 4: Acceptance & Quality

#### Panel 4.1: Acceptance Rate Over Time (Time Series)
- **Type**: Graph
- **Description**: Rolling acceptance rate of AI suggestions

```promql
# Overall acceptance rate (accepted + modified / total reviewed)
(
  sum(rate(proc_suite_coder_reviews_accepted_total[5m])) +
  sum(rate(proc_suite_coder_reviews_modified_total[5m]))
) / sum(rate(proc_suite_coder_reviews_total[5m]))
```

#### Panel 4.2: Acceptance by Procedure Type (Bar Chart)
- **Type**: Bar Chart
- **Description**: Acceptance rate breakdown by procedure type

```promql
(
  sum by (procedure_type) (rate(proc_suite_coder_reviews_accepted_total[1h])) +
  sum by (procedure_type) (rate(proc_suite_coder_reviews_modified_total[1h]))
) / sum by (procedure_type) (rate(proc_suite_coder_reviews_total[1h]))
```

#### Panel 4.3: Review Actions Breakdown (Stacked Bar)
- **Type**: Stacked Bar / Time Series
- **Description**: Accept vs Reject vs Modify over time

```promql
# Accepted
sum(rate(proc_suite_coder_reviews_accepted_total[5m])) * 60

# Rejected
sum(rate(proc_suite_coder_reviews_rejected_total[5m])) * 60

# Modified
sum(rate(proc_suite_coder_reviews_modified_total[5m])) * 60
```

#### Panel 4.4: Acceptance Rate Gauge (Gauge)
- **Type**: Gauge
- **Description**: Current acceptance rate with thresholds

```promql
(
  sum(increase(proc_suite_coder_reviews_accepted_total[1h])) +
  sum(increase(proc_suite_coder_reviews_modified_total[1h]))
) / sum(increase(proc_suite_coder_reviews_total[1h]))
```

**Thresholds**:
- Green: >= 0.80
- Yellow: 0.60 - 0.80
- Red: < 0.60

---

## Dashboard 2: Registry & Quality

**Purpose**: Monitor registry exports, data quality, and manual code additions.

### Row 1: Registry Exports

#### Panel 1.1: Export Status (Pie Chart)
- **Type**: Pie Chart
- **Description**: Success vs Partial vs Failed exports

```promql
# By status
sum by (status) (increase(proc_suite_coder_registry_exports_total[24h]))
```

#### Panel 1.2: Exports Over Time (Time Series)
- **Type**: Graph / Stacked
- **Description**: Registry exports per hour by status

```promql
# Successful
sum(rate(proc_suite_coder_registry_exports_success_total[5m])) * 3600

# Partial
sum(rate(proc_suite_coder_registry_exports_partial_total[5m])) * 3600

# Total (for reference)
sum(rate(proc_suite_coder_registry_exports_total[5m])) * 3600
```

#### Panel 1.3: Export Success Rate (Stat)
- **Type**: Stat
- **Description**: Percentage of successful exports

```promql
sum(increase(proc_suite_coder_registry_exports_success_total[24h])) /
sum(increase(proc_suite_coder_registry_exports_total[24h]))
```

---

### Row 2: Registry Completeness

#### Panel 2.1: Completeness Score Distribution (Histogram)
- **Type**: Histogram / Heatmap
- **Description**: Distribution of registry entry completeness scores

```promql
# Average completeness score over time
avg(proc_suite_coder_registry_completeness_score)

# By version
avg by (version) (proc_suite_coder_registry_completeness_score)
```

#### Panel 2.2: Completeness Gauge (Gauge)
- **Type**: Gauge
- **Description**: Current average completeness

```promql
avg(proc_suite_coder_registry_completeness_score)
```

**Thresholds**:
- Green: >= 0.90
- Yellow: 0.70 - 0.90
- Red: < 0.70

#### Panel 2.3: Export Latency P95 (Stat)
- **Type**: Stat
- **Description**: Registry export latency

```promql
histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_registry_export_latency_ms_bucket[5m])))
```

---

### Row 3: Manual Overrides

#### Panel 3.1: Manual Codes Added (Time Series)
- **Type**: Graph
- **Description**: Manual code additions per hour

```promql
sum(rate(proc_suite_coder_manual_codes_total[5m])) * 3600
```

#### Panel 3.2: Manual vs AI Codes (Pie Chart)
- **Type**: Pie Chart
- **Description**: Source breakdown of final codes

```promql
# Manual
sum(proc_suite_coder_final_codes_total{source="manual"})

# Rule-based
sum(proc_suite_coder_final_codes_total{source="rule"})

# LLM
sum(proc_suite_coder_final_codes_total{source="llm"})

# Hybrid
sum(proc_suite_coder_final_codes_total{source="hybrid"})
```

#### Panel 3.3: Manual Rate by Procedure Type (Bar Chart)
- **Type**: Bar Chart
- **Description**: Which procedure types need most manual intervention

```promql
sum by (procedure_type) (increase(proc_suite_coder_manual_codes_total[24h]))
```

---

### Row 4: AI Quality Indicators

#### Panel 4.1: Rejection Rate by Procedure Type (Bar Chart)
- **Type**: Bar Chart
- **Description**: Identify procedure types where AI underperforms

```promql
sum by (procedure_type) (rate(proc_suite_coder_reviews_rejected_total[1h])) /
sum by (procedure_type) (rate(proc_suite_coder_reviews_total[1h]))
```

#### Panel 4.2: LLM Drift Alert (Stat)
- **Type**: Stat with alert
- **Description**: Acceptance rate drop indicator

```promql
# Current 1h acceptance rate
(
  sum(increase(proc_suite_coder_reviews_accepted_total[1h])) +
  sum(increase(proc_suite_coder_reviews_modified_total[1h]))
) / sum(increase(proc_suite_coder_reviews_total[1h]))

# Compare to 24h baseline for drift detection
# (Use recording rules for efficiency)
```

**Alert**: Fire when 1h acceptance rate < 0.7 * 24h average

---

## Dashboard 3: LLM Drift Monitoring

**Purpose**: Dedicated dashboard for tracking AI model performance drift.

### Row 1: Acceptance Trends

#### Panel 1.1: Rolling Acceptance Rate (Time Series)
- **Type**: Graph
- **Description**: 1h, 6h, 24h rolling acceptance rates

```promql
# 1h rolling
(
  sum(increase(proc_suite_coder_reviews_accepted_total[1h])) +
  sum(increase(proc_suite_coder_reviews_modified_total[1h]))
) / sum(increase(proc_suite_coder_reviews_total[1h]))

# 6h rolling
(
  sum(increase(proc_suite_coder_reviews_accepted_total[6h])) +
  sum(increase(proc_suite_coder_reviews_modified_total[6h]))
) / sum(increase(proc_suite_coder_reviews_total[6h]))

# 24h rolling
(
  sum(increase(proc_suite_coder_reviews_accepted_total[24h])) +
  sum(increase(proc_suite_coder_reviews_modified_total[24h]))
) / sum(increase(proc_suite_coder_reviews_total[24h]))
```

#### Panel 1.2: Acceptance by Source (Time Series)
- **Type**: Graph
- **Description**: Compare LLM vs Rule acceptance rates

```promql
# LLM source acceptance rate
(
  sum(rate(proc_suite_coder_reviews_accepted_total{source="llm"}[1h])) +
  sum(rate(proc_suite_coder_reviews_modified_total{source="llm"}[1h]))
) / sum(rate(proc_suite_coder_reviews_total{source="llm"}[1h]))

# Rule source acceptance rate
(
  sum(rate(proc_suite_coder_reviews_accepted_total{source="rule"}[1h])) +
  sum(rate(proc_suite_coder_reviews_modified_total{source="rule"}[1h]))
) / sum(rate(proc_suite_coder_reviews_total{source="rule"}[1h]))

# Hybrid source acceptance rate
(
  sum(rate(proc_suite_coder_reviews_accepted_total{source="hybrid"}[1h])) +
  sum(rate(proc_suite_coder_reviews_modified_total{source="hybrid"}[1h]))
) / sum(rate(proc_suite_coder_reviews_total{source="hybrid"}[1h]))
```

---

### Row 2: Volume & Context

#### Panel 2.1: Review Volume (Time Series)
- **Type**: Graph
- **Description**: Ensure sufficient sample size for acceptance metrics

```promql
sum(rate(proc_suite_coder_reviews_total[1h])) * 3600
```

#### Panel 2.2: Suggestions per Procedure (Stat)
- **Type**: Stat
- **Description**: Average suggestions generated per procedure

```promql
# Approximate based on counter increments
sum(rate(proc_suite_coder_suggestions_total[1h])) /
(sum(rate(proc_suite_coder_reviews_total[1h])) + 0.001)  # Avoid division by zero
```

---

## Alerting Rules

### Recording Rules (prometheus.yml)

```yaml
groups:
  - name: proc_suite_recording
    rules:
      # 24h baseline acceptance rate
      - record: proc_suite:acceptance_rate:24h
        expr: |
          (
            sum(increase(proc_suite_coder_reviews_accepted_total[24h])) +
            sum(increase(proc_suite_coder_reviews_modified_total[24h]))
          ) / sum(increase(proc_suite_coder_reviews_total[24h]))

      # 1h rolling acceptance rate
      - record: proc_suite:acceptance_rate:1h
        expr: |
          (
            sum(increase(proc_suite_coder_reviews_accepted_total[1h])) +
            sum(increase(proc_suite_coder_reviews_modified_total[1h]))
          ) / sum(increase(proc_suite_coder_reviews_total[1h]))
```

### Alert Rules

```yaml
groups:
  - name: proc_suite_alerts
    rules:
      # Low acceptance rate alert
      - alert: LowAcceptanceRate
        expr: proc_suite:acceptance_rate:1h < 0.6
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "AI suggestion acceptance rate is low"
          description: "Acceptance rate is {{ $value | humanizePercentage }} over the last hour"

      # Acceptance rate drift alert
      - alert: AcceptanceRateDrift
        expr: proc_suite:acceptance_rate:1h < (proc_suite:acceptance_rate:24h * 0.8)
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "AI acceptance rate has dropped significantly"
          description: "1h rate ({{ $value | humanizePercentage }}) is below 80% of 24h baseline"

      # High pipeline latency
      - alert: HighPipelineLatency
        expr: histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m]))) > 5000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline latency P95 exceeds 5 seconds"
          description: "P95 latency is {{ $value }}ms"

      # Registry export failures
      - alert: RegistryExportFailures
        expr: |
          sum(increase(proc_suite_coder_registry_exports_total{status="failed"}[1h])) > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Multiple registry export failures"
          description: "{{ $value }} failed exports in the last hour"
```

---

## JSON Export (Skeleton)

For importing into Grafana, here's a skeleton dashboard JSON:

```json
{
  "dashboard": {
    "title": "Procedure Suite - Coder Performance",
    "tags": ["proc_suite", "coder"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "Suggestions Generated",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum by (procedure_type) (rate(proc_suite_coder_suggestions_total[5m])) * 60",
            "legendFormat": "{{procedure_type}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Pipeline Latency P95",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum by (le) (rate(proc_suite_coder_pipeline_latency_ms_bucket[5m])))",
            "legendFormat": "P95"
          }
        ]
      },
      {
        "id": 3,
        "title": "Acceptance Rate",
        "type": "gauge",
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "(sum(increase(proc_suite_coder_reviews_accepted_total[1h])) + sum(increase(proc_suite_coder_reviews_modified_total[1h]))) / sum(increase(proc_suite_coder_reviews_total[1h]))"
          }
        ],
        "options": {
          "reduceOptions": {"calcs": ["lastNotNull"]},
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "red", "value": null},
              {"color": "yellow", "value": 0.6},
              {"color": "green", "value": 0.8}
            ]
          }
        }
      }
    ]
  }
}
```

---

## Implementation Notes

1. **Metric naming**: All metrics use `proc_suite_` prefix followed by `coder_` for coding-related metrics
2. **Label consistency**: `procedure_type`, `source`, `used_llm` are the primary segmentation labels
3. **Histogram buckets**: Configured for ms latencies: 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000
4. **Rate windows**: Use 5m for real-time, 1h for trends, 24h for baselines
