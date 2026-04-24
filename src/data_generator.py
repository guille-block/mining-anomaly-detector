import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_mining_data(output_path="telemetry_data.csv", num_miners=5, hours=24, interval_mins=5):
    """
    Generates synthetic telemetry data for Bitcoin miners with injected anomalies.
    """
    timestamps = []
    start_time = datetime(2025, 1, 1, 10, 0, 0)
    total_steps = (hours * 60) // interval_mins
    
    data = []
    miner_ids = [f"M{str(i).zfill(3)}" for i in range(1, num_miners + 1)]
    
    # Baselines
    # Hashrate: ~110 TH/s
    # Chip Temp: ~75 C
    # Immersion Temp: ~52 C
    # Pressure: ~1.8 bar

    for step in range(total_steps):
        current_time = start_time + timedelta(minutes=step * interval_mins)
        
        for m_id in miner_ids:
            # Default values with slight noise
            hashrate = 110 + np.random.normal(0, 2)
            chip_temp = 75 + np.random.normal(0, 1)
            immersion_temp = 52 + np.random.normal(0, 0.5)
            pressure = 1.8 + np.random.normal(0, 0.05)
            
            # Inject Anomalies
            
            # 1. Thermal Throttling Scenario (M001, around step 50)
            if m_id == "M001" and 50 <= step <= 60:
                chip_temp += (step - 50) * 2  # Temp rising quickly
                hashrate -= (step - 50) * 5   # Hashrate dropping as result
                
            # 2. Consistent Overheating (M002, entire period)
            if m_id == "M002":
                chip_temp += 10 # Running hot but stable hashrate
                
            # 3. Cooling System Failure / Pump Spike (M003, step 100)
            if m_id == "M003" and 100 <= step <= 110:
                pressure += 0.5 # Sudden pressure spike
                immersion_temp += 5
                
            # 4. Underperforming Miner (M004)
            if m_id == "M004":
                hashrate = 95 + np.random.normal(0, 1) # Consistently lower hashrate than peers at same temp
                
            # 5. Over-cooled / Inefficient (M005)
            if m_id == "M005":
                chip_temp = 60 # Very cool, but same hashrate as others - wasting cooling energy
                immersion_temp = 45

            data.append({
                "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "miner_id": m_id,
                "hashrate_ths": round(hashrate, 2),
                "chip_temp_c": round(chip_temp, 2),
                "immersion_temp_c": round(immersion_temp, 2),
                "immersion_pressure_bar": round(pressure, 2)
            })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Synthentic data generated at {output_path} with {len(df)} rows.")
    return output_path

if __name__ == "__main__":
    generate_mining_data()
