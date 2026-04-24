# Bitcoin Mining Operational Optimizer

This system provides automated telemetry analysis for Bitcoin mining sites, focusing on hardware health, performance optimization, and operational efficiency.

## Overview

The system processes telemetry data from miners (hashrate, chip temperature, immersion cooling pressure/temp) to generate actionable insights. It identifies critical risks (thermal throttling, equipment failure) and optimization opportunities (energy reduction).

## Key Features

1.  **Performance Impact Detection:** Correlations between hashrate drops and temperature rising to identify thermal throttling.
2.  **Hardware Risk Guard:** Alerts on critical temperature thresholds and rapid temperature spikes that signal potential hardware damage.
3.  **Cooling System Audit:** Monitors immersion cooling telemetry for sudden pressure/temp anomalies.
4.  **Fleet Benchmarking:** Identifies underperforming miners by comparing them against the fleet average under similar conditions.
5.  **Efficiency Optimization:** Spots miners that are being over-cooled without performance gains, allowing for energy savings.

## Setup & Run

### Requirements
- Python 3.8+
- `pandas`, `numpy`

### Installation
```bash
pip install -r requirements.txt
```

### Execution
To generate synthetic data and run the analysis:
```bash
python main.py
```

## Analytical Approach & Reasoning

### Assumptions
- **Safe Operating Threshold:** Assumed critical chip temperature threshold is **85°C**.
- **Cooling Lower Bound:** 65°C is considered more than sufficient for immersion cooling; anything below this without performance gain is tagged for optimization.
- **Peer Comparison:** Miners within the same fleet should have an efficiency ratio (Hashrate/Temp) within 15% of the fleet average.

### Methodology
- **Statistical Filtering:** Uses baseline deviations and fleet-wide averages to filter out noise from actual hardware issues.
- **Correlation Analysis:** Uses Pearson correlation between hashrate and temperature to confirm thermal throttling.
- **Delta Analysis:** Monitors the first derivative of temperature and pressure to catch sudden failures (e.g., pump stops).

## Scaling to Production

To extend this to a real-time production system:
1.  **Ingestion:** Replace the CSV loader with a stream processor (e.g., Kafka or MQTT) connected to the mining controller API.
2.  **Time-Series Database:** Use InfluxDB or Prometheus for long-term storage of telemetry.
3.  **Alerting:** Integrate the analysis categories with PagerDuty or Slack for real-time operational response.
4.  **Model Retraining:** Use the identified anomalies to train a more sophisticated machine learning model (e.g., LSTMs) for predictive maintenance.

## Output

The system generates:
- **Console Report:** A high-level summary of risks and business impact.
- **insights.json:** Machine-readable data for integration with dashboards.
