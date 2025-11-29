"""
Feature calculation functions for heterokaryon analysis.

This module provides a registry-based system for calculating features.
To add a new feature, simply:
1. Define a calculation function that takes (feature_df, main_df) and returns feature_df
2. Register it using the @register_feature decorator
"""

import pandas as pd
from typing import Callable, Dict

# Registry to store feature calculation functions
_FEATURE_REGISTRY: Dict[str, Callable] = {}


def register_feature(name: str):
    """
    Decorator to register a feature calculation function.
    
    Args:
        name: The name of the feature (used as the column name)
    
    Example:
        @register_feature("Total Area")
        def calc_total_area(feature_df, main_df):
            ...
    """
    def decorator(func: Callable):
        _FEATURE_REGISTRY[name] = func
        return func
    return decorator


def get_all_features() -> Dict[str, Callable]:
    """Get all registered feature calculation functions."""
    return _FEATURE_REGISTRY.copy()


@register_feature("Total Area")
def calc_total_area(feature_df: pd.DataFrame, main_df: pd.DataFrame) -> pd.DataFrame:
    """Sum areas of ES and MEF per block."""
    total_area = (
        main_df[main_df["Type"].isin(["ES", "MEF"])]
        .groupby("Block_ID")["Area"]
        .sum()
    )
    feature_df["Total Area"] = feature_df["Block_ID"].map(total_area)
    return feature_df


@register_feature("Total Oct4 in Heterokaryon (CID)")
def calc_total_Oct4_heterokaryon_CID(feature_df: pd.DataFrame, main_df: pd.DataFrame) -> pd.DataFrame:
    """Sum Corrected Integrated Density for ES and MEF per block."""
    total_oct4 = (
        main_df[main_df["Type"].isin(["ES", "MEF"])]
        .groupby("Block_ID")["Corrected Integrated Density"]
        .sum()
    )
    feature_df["Total Oct4 in Heterokaryon (CID)"] = feature_df["Block_ID"].map(total_oct4)
    return feature_df


@register_feature("Total HET:Single ES (CID)")
def calc_total_HET_single_ES_CID(feature_df: pd.DataFrame, main_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate ratio of Total Oct4 in Heterokaryon to Unfused ES."""
    unfused = (
        main_df[main_df["Type"] == "Unfused ES"]
        .set_index("Block_ID")["Corrected Integrated Density"]
    )
    feature_df["Total HET:Single ES (CID)"] = (
        feature_df["Total Oct4 in Heterokaryon (CID)"] /
        feature_df["Block_ID"].map(unfused)
    )
    return feature_df


@register_feature("Mean Oct4 Concentration Ratio in HETS:Single")
def calc_mean_Oct4_heterokaryon_concentration_ratio_HETS_single(
    feature_df: pd.DataFrame, 
    main_df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate mean Oct4 concentration ratio in heterokaryons vs single ES."""
    # per-block values
    mean_es = (
        main_df[main_df["Type"] == "ES"]
        .set_index("Block_ID")["Corrected Mean"]
    )
    mean_mef = (
        main_df[main_df["Type"] == "MEF"]
        .set_index("Block_ID")["Corrected Mean"]
    )
    mean_unfused = (
        main_df[main_df["Type"] == "Unfused ES"]
        .set_index("Block_ID")["Corrected Mean"]
    )

    # map into feature_df (guarantee correct block alignment)
    es = feature_df["Block_ID"].map(mean_es)
    mef = feature_df["Block_ID"].map(mean_mef)
    unfused = feature_df["Block_ID"].map(mean_unfused)

    # compute ratio
    feature_df["Mean Oct4 Concentration Ratio in HETS:Single"] = (
        (es + mef) / unfused
    )
    return feature_df

