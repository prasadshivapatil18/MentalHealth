"""
Analytics and insight generation module for CDC Household Pulse Survey dataset
'Indicators of Anxiety or Depression Based on Reported Frequency of Symptoms'.
Provides cached aggregations, demographic distributions, state metrics, and risk benchmarking.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

DATASET_FILE = Path(__file__).resolve().parent / "Indicators_of_Anxiety_or_Depression.csv"


class IndicatorsAnalytics:
    """Manages loading, cleaning, and aggregating the mental health indicators dataset."""

    def __init__(self, csv_path: Path = DATASET_FILE):
        self.csv_path = csv_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.is_loaded: bool = False
        self._summary_cache: Optional[Dict[str, Any]] = None
        self._trends_cache: Optional[List[Dict[str, Any]]] = None
        self._demographics_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._states_cache: Optional[List[Dict[str, Any]]] = None
        self.load_data()

    def load_data(self) -> bool:
        """Load and clean dataset."""
        if not self.csv_path.exists():
            print(f"[Analytics] Dataset file not found at {self.csv_path}")
            return False

        try:
            df = pd.read_csv(self.csv_path)
            # Clean and standardize columns
            df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
            df["Low CI"] = pd.to_numeric(df["Low CI"], errors="coerce")
            df["High CI"] = pd.to_numeric(df["High CI"], errors="coerce")
            df["Time Period"] = pd.to_numeric(df["Time Period"], errors="coerce")

            # Drop rows missing essential Value and Indicator
            self.df = df.dropna(subset=["Value", "Indicator", "Group"]).copy()
            self.is_loaded = True
            print(f"[Analytics] Successfully loaded {len(self.df)} clean rows from {self.csv_path.name}")
            return True
        except Exception as e:
            print(f"[Analytics] Error loading dataset: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Return overarching KPI summary statistics."""
        if not self.is_loaded or self.df.empty:
            return {"status": "error", "message": "Dataset not loaded"}

        if self._summary_cache is not None:
            return self._summary_cache

        total_records = len(self.df)
        indicators = self.df["Indicator"].unique().tolist()
        groups = self.df["Group"].unique().tolist()

        # National estimates (latest time period)
        nat_df = self.df[self.df["Group"] == "National Estimate"].copy()
        latest_period = nat_df["Time Period"].max() if not nat_df.empty else 1
        latest_nat = nat_df[nat_df["Time Period"] == latest_period]

        nat_stats = {}
        for _, row in latest_nat.iterrows():
            ind = row["Indicator"]
            val = float(row["Value"])
            if "Anxiety Disorder or Depressive Disorder" in ind:
                nat_stats["combined"] = val
            elif "Anxiety Disorder" in ind:
                nat_stats["anxiety"] = val
            elif "Depressive Disorder" in ind:
                nat_stats["depression"] = val

        # Age group with highest overall average rate
        age_df = self.df[self.df["Group"] == "By Age"]
        age_avg = age_df.groupby("Subgroup")["Value"].mean().sort_values(ascending=False)
        highest_age_group = age_avg.index[0] if not age_avg.empty else "18 - 29 years"
        highest_age_rate = round(float(age_avg.iloc[0]), 1) if not age_avg.empty else 0.0

        # State rates
        state_df = self.df[self.df["Group"] == "By State"]
        state_latest_period = state_df["Time Period"].max()
        state_latest = state_df[
            (state_df["Time Period"] == state_latest_period)
            & (state_df["Indicator"] == "Symptoms of Anxiety Disorder or Depressive Disorder")
        ]
        top_state = (
            state_latest.sort_values(by="Value", ascending=False).iloc[0]["State"]
            if not state_latest.empty
            else "N/A"
        )
        lowest_state = (
            state_latest.sort_values(by="Value", ascending=True).iloc[0]["State"]
            if not state_latest.empty
            else "N/A"
        )

        self._summary_cache = {
            "total_records": total_records,
            "indicators": indicators,
            "groups": groups,
            "latest_period": int(latest_period) if pd.notna(latest_period) else 1,
            "national_stats": {
                "anxiety_rate": nat_stats.get("anxiety", 17.6),
                "depression_rate": nat_stats.get("depression", 13.9),
                "combined_rate": nat_stats.get("combined", 21.4),
            },
            "highest_age_demographic": {
                "group": highest_age_group,
                "average_prevalence": highest_age_rate,
            },
            "top_state_prevalence": top_state,
            "lowest_state_prevalence": lowest_state,
        }
        return self._summary_cache

    def get_trends(self) -> List[Dict[str, Any]]:
        """Return time-series trend of national prevalence across time periods."""
        if not self.is_loaded or self.df.empty:
            return []

        if self._trends_cache is not None:
            return self._trends_cache

        nat_df = self.df[self.df["Group"] == "National Estimate"].copy()
        if nat_df.empty:
            return []

        # Sort by Time Period
        nat_df = nat_df.sort_values(by=["Time Period"])
        periods = sorted(nat_df["Time Period"].dropna().unique())

        trends = []
        for p in periods:
            sub = nat_df[nat_df["Time Period"] == p]
            if sub.empty:
                continue

            label = sub["Time Period Label"].iloc[0] if "Time Period Label" in sub else f"Period {int(p)}"
            start_date = sub["Time Period Start Date"].iloc[0] if "Time Period Start Date" in sub else ""
            end_date = sub["Time Period End Date"].iloc[0] if "Time Period End Date" in sub else ""

            row_data = {
                "period": int(p),
                "label": label,
                "start_date": str(start_date) if pd.notna(start_date) else "",
                "end_date": str(end_date) if pd.notna(end_date) else "",
                "anxiety": None,
                "depression": None,
                "combined": None,
            }

            for _, row in sub.iterrows():
                ind = row["Indicator"]
                val = round(float(row["Value"]), 1)
                if "Anxiety Disorder or Depressive Disorder" in ind:
                    row_data["combined"] = val
                elif "Anxiety Disorder" in ind:
                    row_data["anxiety"] = val
                elif "Depressive Disorder" in ind:
                    row_data["depression"] = val

            trends.append(row_data)

        self._trends_cache = trends
        return trends

    def get_demographics(self, group: str = "By Age") -> List[Dict[str, Any]]:
        """
        Return breakdown for demographic group (e.g. 'By Age', 'By Sex', 'By Education', 'By Race/Hispanic ethnicity').
        """
        if not self.is_loaded or self.df.empty:
            return []

        if group in self._demographics_cache:
            return self._demographics_cache[group]

        grp_df = self.df[self.df["Group"] == group].copy()
        if grp_df.empty:
            return []

        # Latest period
        latest_period = grp_df["Time Period"].max()
        grp_latest = grp_df[grp_df["Time Period"] == latest_period]

        results = []
        subgroups = grp_latest["Subgroup"].unique().tolist()

        for sub in subgroups:
            sub_rows = grp_latest[grp_latest["Subgroup"] == sub]
            entry = {
                "subgroup": str(sub),
                "anxiety": 0.0,
                "depression": 0.0,
                "combined": 0.0,
                "low_ci": 0.0,
                "high_ci": 0.0,
            }

            for _, row in sub_rows.iterrows():
                ind = row["Indicator"]
                val = round(float(row["Value"]), 1)
                if "Anxiety Disorder or Depressive Disorder" in ind:
                    entry["combined"] = val
                    entry["low_ci"] = round(float(row["Low CI"]), 1) if pd.notna(row["Low CI"]) else val
                    entry["high_ci"] = round(float(row["High CI"]), 1) if pd.notna(row["High CI"]) else val
                elif "Anxiety Disorder" in ind:
                    entry["anxiety"] = val
                elif "Depressive Disorder" in ind:
                    entry["depression"] = val

            results.append(entry)

        self._demographics_cache[group] = results
        return results

    def get_state_metrics(self) -> List[Dict[str, Any]]:
        """Return state-by-state rates for the latest survey period."""
        if not self.is_loaded or self.df.empty:
            return []

        if self._states_cache is not None:
            return self._states_cache

        state_df = self.df[self.df["Group"] == "By State"].copy()
        if state_df.empty:
            return []

        latest_period = state_df["Time Period"].max()
        state_latest = state_df[state_df["Time Period"] == latest_period]

        states = sorted(state_latest["State"].dropna().unique().tolist())
        results = []

        for st in states:
            st_rows = state_latest[state_latest["State"] == st]
            entry = {
                "state": str(st),
                "anxiety": 0.0,
                "depression": 0.0,
                "combined": 0.0,
                "quartile": "",
            }

            for _, row in st_rows.iterrows():
                ind = row["Indicator"]
                val = round(float(row["Value"]), 1)
                quart = str(row["Quartile Range"]) if pd.notna(row.get("Quartile Range")) else ""
                if "Anxiety Disorder or Depressive Disorder" in ind:
                    entry["combined"] = val
                    entry["quartile"] = quart
                elif "Anxiety Disorder" in ind:
                    entry["anxiety"] = val
                elif "Depressive Disorder" in ind:
                    entry["depression"] = val

            results.append(entry)

        # Sort alphabetically
        results = sorted(results, key=lambda x: x["combined"], reverse=True)
        self._states_cache = results
        return results

    def benchmark_screener(
        self,
        anxiety_score: int,
        depression_score: int,
        age_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate PHQ-4 score against CDC population benchmark.
        PHQ-4 scale:
        - 0-2: Normal / Minimal
        - 3-5: Mild
        - 6-8: Moderate
        - 9-12: Severe
        Anxiety subscale (questions 1-2): >= 3 indicates positive screen for anxiety
        Depression subscale (questions 3-4): >= 3 indicates positive screen for depression
        """
        total_score = anxiety_score + depression_score

        if total_score <= 2:
            severity = "Minimal"
            status_desc = "Symptoms are minimal or within normal baseline."
            color = "#10B981"
        elif total_score <= 5:
            severity = "Mild"
            status_desc = "Mild symptoms reported. Mindfulness and stress management can help."
            color = "#F59E0B"
        elif total_score <= 8:
            severity = "Moderate"
            status_desc = "Moderate symptoms reported. Consulting a mental healthcare provider is recommended."
            color = "#F97316"
        else:
            severity = "Severe"
            status_desc = "Elevated symptoms reported. Seeking professional guidance is strongly advised."
            color = "#EF4444"

        anxiety_screen_positive = anxiety_score >= 3
        depression_screen_positive = depression_score >= 3

        summary = self.get_summary()
        nat_stats = summary.get("national_stats", {})
        nat_combined = nat_stats.get("combined_rate", 21.4)

        return {
            "total_score": total_score,
            "max_score": 12,
            "severity": severity,
            "severity_color": color,
            "description": status_desc,
            "subscales": {
                "anxiety_score": anxiety_score,
                "anxiety_screen_positive": anxiety_screen_positive,
                "depression_score": depression_score,
                "depression_screen_positive": depression_screen_positive,
            },
            "population_benchmark": {
                "national_reported_rate": f"{nat_combined}%",
                "survey_context": "Based on U.S. CDC Household Pulse Survey population indicators.",
            },
        }


# Singleton analytics engine instance
analytics_engine = IndicatorsAnalytics()
