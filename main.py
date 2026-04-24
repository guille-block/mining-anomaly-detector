import os
from src.data_generator import generate_mining_data
from src.analyzer import MinerAnalyzer
import json

def print_banner(text):
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)

def generate_report(insights):
    print_banner("BITCOIN MINING OPERATIONAL INSIGHTS REPORT")
    print(f"{'CATEGORY':<25} | {'MINER':<6} | {'SEVERITY':<8} | {'OBSERVATION'}")
    print("-" * 80)
    
    # Sort by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    sorted_insights = sorted(insights, key=lambda x: severity_order.get(x['severity'], 99))
    
    unique_insights = []
    seen = set()
    for ins in sorted_insights:
        key = (ins['category'], ins['miner_id'], ins['severity'])
        if key not in seen:
            unique_insights.append(ins)
            seen.add(key)

    for ins in unique_insights:
        print(f"{ins['category']:<25} | {ins['miner_id']:<6} | {ins['severity']:<8} | {ins['observation']}")
        print(f"  > Justification: {ins['numeric_justification']}")
        print(f"  > Actionable:    {ins['action']}\n")

    # Final summary for business value
    print_banner("BUSINESS IMPACT SUMMARY")
    critical_count = len([i for i in unique_insights if i['severity'] == "Critical"])
    optimization_count = len([i for i in unique_insights if i['category'] == "Efficiency Optimization"])
    
    print(f"Total Risks Detected: {len(unique_insights)}")
    print(f"Critical Hardware Risks: {critical_count} (Action required to prevent capital loss)")
    print(f"Efficiency Tuning Ops: {optimization_count} (Potential OPEX reduction)")
    print("\nRecommendation: Address 'Critical' and 'High' category alerts immediately to stabilize fleet hashrate.")

def main():
    data_file = "telemetry_data.csv"
    
    # 1. Generate synthetic data if not exists
    if not os.path.exists(data_file):
        print("Data file not found. Generating sample fleet data...")
        generate_mining_data(data_file)
    
    # 2. Run analysis
    analyzer = MinerAnalyzer(data_file)
    insights = analyzer.run_analysis()
    
    # 3. Output report
    generate_report(insights)
    
    # 4. Save JSON version as requested
    with open("insights.json", "w") as f:
        json.dump(insights, f, indent=4)
        print("\n[DONE] Detailed JSON data exported to 'insights.json'")

if __name__ == "__main__":
    main()
