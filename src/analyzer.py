import pandas as pd
import numpy as np

class MinerAnalyzer:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        # Robustness: Strip any trailing spaces from headers
        self.df.columns = self.df.columns.str.strip()
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.insights = []

    def run_analysis(self):
        """Executes all analysis modules aligned with the 5 requirement categories."""
        self._detect_performance_impact()
        self._detect_hardware_risks()
        self._analyze_cooling_system()
        self._benchmark_peers()
        self._identify_optimization_opportunities()
        return self.insights

    def _detect_performance_impact(self):
        """1. Performance Impact: Drops, correlations, and baseline deviations."""
        baselines = self.df.groupby('miner_id')['hashrate_ths'].transform('mean')
        self.df['hashrate_deviation'] = (self.df['hashrate_ths'] - baselines) / baselines
        
        # Check: Hashrate drop > 10%
        drops = self.df[self.df['hashrate_deviation'] < -0.10]
        
        for name, group in drops.groupby('miner_id'):
            # Check: Correlation between hashrate and rising temperature
            # Only compute if we have enough variance and rows
            if len(group) > 1 and group['chip_temp_c'].std() > 0:
                temp_corr = group['hashrate_ths'].corr(group['chip_temp_c'])
            else:
                temp_corr = 0 # Default if no variation
            
            self.insights.append({
                "category": "Performance Impact",
                "miner_id": name,
                "severity": "High" if temp_corr < -0.5 else "Medium",
                "observation": f"Hashrate drop ({group['hashrate_deviation'].mean()*100:.1f}% deviation).",
                "numeric_justification": f"Correlation: {temp_corr:.2f}, Baseline: {baselines.loc[group.index[0]]:.1f} TH/s",
                "action": "Inspect for thermal throttling or board failure."
            })

    def _detect_hardware_risks(self):
        """2. Hardware Damage: Critical thresholds and rapid spikes."""
        CRITICAL_TEMP = 85.0
        RAPID_TEMP_RISE = 5.0 
        
        # Check: Consistent exceeding of safe thresholds
        overheating = self.df[self.df['chip_temp_c'] > CRITICAL_TEMP]
        for name, group in overheating.groupby('miner_id'):
            self.insights.append({
                "category": "Hardware Risk",
                "miner_id": name,
                "severity": "Critical",
                "observation": f"Exceeded threshold of {CRITICAL_TEMP}C.",
                "numeric_justification": f"Peak Temp: {group['chip_temp_c'].max()}C",
                "action": "Immediate thermal audit or shutdown."
            })

        # Check: Rapid temp rise over short window
        self.df['temp_delta'] = self.df.groupby('miner_id')['chip_temp_c'].diff()
        spikes = self.df[self.df['temp_delta'] > RAPID_TEMP_RISE]
        for _, row in spikes.iterrows():
            self.insights.append({
                "category": "Hardware Risk",
                "miner_id": row['miner_id'],
                "severity": "High",
                "observation": "Rapid temperature spike detected.",
                "numeric_justification": f"Delta: +{row['temp_delta']}C in 5 mins",
                "action": "Check for fan/pump failure."
            })

    def _analyze_cooling_system(self):
        """3. Immersion Cooling: Pressure anomalies and trend divergence."""
        # Check: Sudden pressure spikes or drops
        self.df['pressure_delta'] = self.df.groupby('miner_id')['immersion_pressure_bar'].diff()
        spikes = self.df[self.df['pressure_delta'].abs() > 0.3]
        
        for _, row in spikes.iterrows():
            self.insights.append({
                "category": "Cooling System",
                "miner_id": row['miner_id'],
                "severity": "High",
                "observation": "Immersion pressure anomaly.",
                "numeric_justification": f"Pressure Delta: {row['pressure_delta']:.2f} bar",
                "action": "Inspect pump seals and fluid levels."
            })

        # Check: Pressure/Temp changes NOT reflected in chip temp improvements
        # If pressure went up but chip temp stayed SAME or INCREASED
        ineffective = self.df[(self.df['pressure_delta'] > 0.1) & (self.df['temp_delta'] >= 0)]
        for name, group in ineffective.groupby('miner_id'):
            self.insights.append({
                "category": "Cooling System",
                "miner_id": name,
                "severity": "Medium",
                "observation": "Ineffective cooling response to pressure increase.",
                "numeric_justification": f"Pressure +{group['pressure_delta'].mean():.2f} bar yielded no temp drop.",
                "action": "Inspect fluid heat exchanger for scaling or obstruction."
            })

    def _benchmark_peers(self):
        """4. Peer Comparison: Fleet outliers and repeated patterns."""
        # Calculate Fleet Average for the current timestamp
        fleet_avg = self.df.groupby('timestamp')['hashrate_ths'].transform('mean')
        self.df['fleet_diff'] = self.df['hashrate_ths'] - fleet_avg
        
        # Check: Disproportionate hashrate loss compared to peers (Fleet underperformers)
        outliers = self.df[self.df['fleet_diff'] < -15]
        for name, group in outliers.groupby('miner_id'):
            self.insights.append({
                "category": "Peer Benchmarking",
                "miner_id": name,
                "severity": "Medium",
                "observation": "Miner significantly underperforming vs fleet avg.",
                "numeric_justification": f"Avg Diff: {group['fleet_diff'].mean():.1f} TH/s below peers",
                "action": "Calibrate miner settings or swap PSU."
            })

    def _identify_optimization_opportunities(self):
        """5. Optimization: Identifying thermal headroom."""
        SAFE_LIMIT_LOW = 65.0
        # Check: Miners well below limits with no extra gains
        undercool = self.df[self.df['chip_temp_c'] < SAFE_LIMIT_LOW]
        for name, group in undercool.groupby('miner_id'):
            self.insights.append({
                "category": "Efficiency Optimization",
                "miner_id": name,
                "severity": "Low",
                "observation": "Operating well below thermal limits.",
                "numeric_justification": f"Avg Temp: {group['chip_temp_c'].mean():.1f}C (Limit: {SAFE_LIMIT_LOW}C)",
                "action": "Consider reducing system pressure to save power."
            })
