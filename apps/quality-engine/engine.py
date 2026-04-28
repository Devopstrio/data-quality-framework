import pandas as pd
import numpy as np
import logging
import time

class QualityEngine:
    def __init__(self):
        self.logger = logging.getLogger("quality-engine")

    def profile_dataset(self, df: pd.DataFrame):
        """
        Generates a statistical profile of the dataset.
        """
        self.logger.info("Starting automated profiling...")
        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "uniqueness": {col: df[col].is_unique for col in df.columns},
            "stats": df.describe(include='all').to_dict()
        }
        return profile

    def run_completeness_rules(self, df: pd.DataFrame, rules: list):
        """
        Evaluates completeness rules (null checks).
        """
        results = []
        for rule in rules:
            col = rule["column"]
            threshold = rule.get("threshold", 0.0)
            null_pct = df[col].isnull().mean()
            passed = null_pct <= threshold
            results.append({
                "rule": f"Completeness:{col}",
                "metric": null_pct,
                "passed": passed,
                "severity": rule.get("severity", "P2")
            })
        return results

    def calculate_trust_score(self, results: list):
        """
        Aggregates rule results into a weighted trust score.
        """
        if not results:
            return 1.0
        
        passed_count = sum(1 for r in results if r["passed"])
        score = passed_count / len(results)
        return round(score, 4)

    def detect_schema_drift(self, current_schema: dict, baseline_schema: dict):
        """
        Identifies differences between current and baseline schemas.
        """
        added = set(current_schema.keys()) - set(baseline_schema.keys())
        removed = set(baseline_schema.keys()) - set(current_schema.keys())
        
        return {
            "is_drifted": len(added) > 0 or len(removed) > 0,
            "added_columns": list(added),
            "removed_columns": list(removed)
        }

if __name__ == "__main__":
    engine = QualityEngine()
    
    # Mock data
    data = {
        'id': [1, 2, 3, 4, 5],
        'email': ['a@b.com', 'c@d.com', None, 'e@f.com', 'g@h.com'],
        'age': [25, 30, 45, 120, -5]
    }
    df = pd.DataFrame(data)
    
    # 1. Profile
    print("Dataset Profile:", engine.profile_dataset(df))
    
    # 2. Run Rules
    rules = [{"column": "email", "threshold": 0.1, "severity": "P1"}]
    results = engine.run_completeness_rules(df, rules)
    print("Rule Results:", results)
    
    # 3. Calculate Score
    print("Trust Score:", engine.calculate_trust_score(results))
