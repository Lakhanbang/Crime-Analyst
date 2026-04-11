"""Business logic for state, crime, and national crime analytics."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.loaders.csv_loader import get_crime_dataset
from app.utils.helpers import normalize_lookup, safe_percentage_change, title_sorted, to_float


@dataclass(slots=True)
class AnalyticsService:
    """Service layer wrapping reusable pandas-based aggregations."""

    dataframe: pd.DataFrame

    @classmethod
    def from_cache(cls) -> "AnalyticsService":
        """Build the service using the globally cached dataset."""

        return cls(dataframe=get_crime_dataset())

    def list_states(self) -> list[str]:
        """Return all unique states in sorted order."""

        return title_sorted(self.dataframe["state"].dropna().unique().tolist())

    def list_crimes(self) -> list[str]:
        """Return all unique crime types in sorted order."""

        return title_sorted(self.dataframe["crime_type"].dropna().unique().tolist())

    def resolve_state_name(self, state: str) -> str:
        """Match user input to a canonical dataset state name."""

        lookup = normalize_lookup(state)
        state_map = (
            self.dataframe[["state", "state_key"]]
            .drop_duplicates()
            .set_index("state_key")["state"]
            .to_dict()
        )
        if lookup not in state_map:
            raise LookupError(f"Invalid state: {state}")
        return str(state_map[lookup])

    def resolve_crime_name(self, crime: str) -> str:
        """Match user input to a canonical dataset crime type."""

        lookup = normalize_lookup(crime)
        crime_map = (
            self.dataframe[["crime_type", "crime_type_key"]]
            .drop_duplicates()
            .set_index("crime_type_key")["crime_type"]
            .to_dict()
        )
        if lookup not in crime_map:
            raise LookupError(f"Invalid crime type: {crime}")
        return str(crime_map[lookup])

    def _yearly_trend(self, df: pd.DataFrame) -> list[dict[str, float]]:
        """Build yearly totals for the provided slice."""

        yearly = (
            df.groupby("year", as_index=False)["number_of_cases"]
            .sum()
            .sort_values("year")
        )
        return [
            {"year": int(row.year), "value": float(row.number_of_cases)}
            for row in yearly.itertuples(index=False)
        ]

    def get_state_analytics(self, state: str) -> dict[str, object]:
        """Return summary analytics for a single state."""

        canonical_state = self.resolve_state_name(state)
        state_df = self.dataframe[self.dataframe["state_key"] == normalize_lookup(canonical_state)]

        top_crimes = (
            state_df.groupby("crime_type", as_index=False)["number_of_cases"]
            .sum()
            .sort_values("number_of_cases", ascending=False)
            .head(5)
        )

        return {
            "state": canonical_state,
            "total_cases": int(state_df["number_of_cases"].sum()),
            "total_arrests": int(state_df["arrests_made"].sum()),
            "avg_arrests_per_record": to_float(state_df["arrests_made"].mean()),
            "avg_charge_sheet_filed_pct": to_float(state_df["charge_sheet_filed_pct"].mean()),
            "avg_crime_rate_per_100k": to_float(state_df["crime_rate_per_100k"].mean()),
            "avg_police_response_time_min": to_float(state_df["police_response_time_min"].mean()),
            "yearly_trend": self._yearly_trend(state_df),
            "top_crimes": [
                {"name": str(row.crime_type), "value": float(row.number_of_cases)}
                for row in top_crimes.itertuples(index=False)
            ],
        }

    def get_state_crime_analytics(self, state: str, crime: str) -> dict[str, object]:
        """Return analytics for one crime type within one state."""

        canonical_state = self.resolve_state_name(state)
        canonical_crime = self.resolve_crime_name(crime)

        slice_df = self.dataframe[
            (self.dataframe["state_key"] == normalize_lookup(canonical_state))
            & (self.dataframe["crime_type_key"] == normalize_lookup(canonical_crime))
        ]
        if slice_df.empty:
            raise LookupError(
                f"No records found for crime '{canonical_crime}' in state '{canonical_state}'"
            )

        yearly_trend = self._yearly_trend(slice_df)
        growth_pct = None
        if len(yearly_trend) >= 2:
            previous = yearly_trend[-2]["value"]
            current = yearly_trend[-1]["value"]
            growth_pct = safe_percentage_change(previous=previous, current=current)

        return {
            "state": canonical_state,
            "crime_type": canonical_crime,
            "total_cases": int(slice_df["number_of_cases"].sum()),
            "total_arrests": int(slice_df["arrests_made"].sum()),
            "avg_charge_sheet_filed_pct": to_float(slice_df["charge_sheet_filed_pct"].mean()),
            "avg_crime_rate_per_100k": to_float(slice_df["crime_rate_per_100k"].mean()),
            "avg_police_response_time_min": to_float(slice_df["police_response_time_min"].mean()),
            "growth_pct_latest_year": growth_pct,
            "yearly_trend": yearly_trend,
        }

    def get_national_analytics(self) -> dict[str, object]:
        """Return national-level analytics across the complete dataset."""

        top_states = (
            self.dataframe.groupby("state", as_index=False)["number_of_cases"]
            .sum()
            .sort_values("number_of_cases", ascending=False)
            .head(5)
        )
        top_crimes = (
            self.dataframe.groupby("crime_type", as_index=False)["number_of_cases"]
            .sum()
            .sort_values("number_of_cases", ascending=False)
            .head(5)
        )

        return {
            "total_cases": int(self.dataframe["number_of_cases"].sum()),
            "total_arrests": int(self.dataframe["arrests_made"].sum()),
            "avg_charge_sheet_filed_pct": to_float(self.dataframe["charge_sheet_filed_pct"].mean()),
            "avg_crime_rate_per_100k": to_float(self.dataframe["crime_rate_per_100k"].mean()),
            "avg_police_response_time_min": to_float(
                self.dataframe["police_response_time_min"].mean()
            ),
            "top_dangerous_states": [
                {"name": str(row.state), "value": float(row.number_of_cases)}
                for row in top_states.itertuples(index=False)
            ],
            "top_crime_categories": [
                {"name": str(row.crime_type), "value": float(row.number_of_cases)}
                for row in top_crimes.itertuples(index=False)
            ],
            "yearly_trend": self._yearly_trend(self.dataframe),
        }
