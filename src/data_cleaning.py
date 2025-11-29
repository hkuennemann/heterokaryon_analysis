"""
Data cleaning and preparation functions for heterokaryon analysis.
"""

import pandas as pd
from .features import get_all_features


def _remove_blank_rows(df):
    '''
    Remove blank rows (rows where all values are NaN or empty strings)
    '''
    # Remove blank rows (rows where all values are NaN or empty strings)
    df = df.dropna(how='all')
    df = df[~(df.astype(str).apply(lambda x: x.str.strip().eq('')).all(axis=1))]

    # Reset index after removing rows
    df = df.reset_index(drop=True)
    return df


def _add_block_id(df):
    '''
    Add Block_ID column to identify each block
    '''
    # Add Block_ID column
    # Blocks are identified by Type resetting to 1 (new block starts)
    block_id = 1
    block_ids = []
    
    for idx, row in df.iterrows():
        # If Type is 1, it could be a new block or continuation
        # Check if previous row had Type 4 (end of previous block)
        if idx == 0:
            # First row always starts block 1
            block_ids.append(block_id)
        elif row['Type'] == 1:
            # Check if previous row was Type 4 (end of block)
            if df.iloc[idx - 1]['Type'] == 4:
                block_id += 1
            block_ids.append(block_id)
        else:
            # Continue with current block
            block_ids.append(block_id)
    
    # Insert Block_ID as the first column
    df.insert(0, 'Block_ID', block_ids)
    
    return df


def _rename_type_values(df):
    '''
    Rename the type values to more descriptive names
    '''
    # Ensure column is object type
    df['Type'] = df['Type'].astype(object)

    # Rename the type values
    df.loc[df.Type == 1.0, 'Type'] = 'Background'
    df.loc[df.Type == 2.0, 'Type'] = 'ES'
    df.loc[df.Type == 3.0, 'Type'] = 'MEF'
    df.loc[df.Type == 4.0, 'Type'] = 'Unfused ES'

    return df


def _calc_corrected_integrated_density(df):
    """Calculate corrected integrated density by subtracting background."""
    # Extract background mean per block
    bg_mean = df[df["Type"] == "Background"].set_index("Block_ID")["Mean"]

    # Map background mean to all rows
    df["Background_Mean"] = df["Block_ID"].map(bg_mean)

    # Compute corrected integrated density (skip Background itself)
    df["Corrected Integrated Density"] = df["IntDen"] - (df["Area"] * df["Background_Mean"])

    # Set Background rows to NaN for the corrected value
    df.loc[df["Type"] == "Background", "Corrected Integrated Density"] = None

    # Drop Background_Mean column
    df = df.drop(columns=["Background_Mean"])

    return df


def _calc_corrected_mean(df):
    """Calculate corrected mean intensity."""
    df["Corrected Mean"] = df["Corrected Integrated Density"] / df["Area"]
    return df


def clean_data(raw_data_path):
    """
    Clean CSV by:
    1. Removing blank separator rows
    2. Adding Block_ID column to identify each block
    3. Ensuring proper data structure
    """
    # Read the CSV file
    df = pd.read_csv(raw_data_path)
    
    # Remove blank rows (rows where all values are NaN or empty strings)
    df = _remove_blank_rows(df)
    
    # Add Block_ID column
    df = _add_block_id(df)

    # Rename the type values
    df = _rename_type_values(df)
    
    return df


def prepare_data(raw_data_path, cleaned_data_path=None):
    """
    Clean data and add derived features to the main dataframe.
    
    Args:
        raw_data_path: Path to raw CSV file
        cleaned_data_path: Optional path to save cleaned data
    
    Returns:
        DataFrame with cleaned data and derived features
    """
    # ------------------------------
    # Clean data
    # ------------------------------
    df = clean_data(raw_data_path)

    # ------------------------------
    # Add derived features to main dataframe
    # ------------------------------

    # Corrected Integrated Density
    df = _calc_corrected_integrated_density(df)

    # Corrected Mean
    df = _calc_corrected_mean(df)

    # ------------------------------
    # Save data
    # ------------------------------
    if cleaned_data_path:
        df.to_csv(cleaned_data_path, index=False)

    return df


def create_feature_dataframe(cleaned_data_path, feature_data_path=None, feature_names=None):
    """
    Create feature dataframe from cleaned data.
    
    Args:
        cleaned_data_path: Path to cleaned CSV file
        feature_data_path: Optional path to save feature dataframe
        feature_names: Optional list of feature names to calculate.
                      If None, calculates all registered features.
    
    Returns:
        DataFrame with calculated features
    """
    # ------------------------------
    # Load main dataframe
    # ------------------------------
    main_df = pd.read_csv(cleaned_data_path)

    # ------------------------------
    # Create feature dataframe
    # ------------------------------

    # Initialize empty feature dataframe
    feature_df = pd.DataFrame()

    # Add Block_ID column
    feature_df["Block_ID"] = main_df["Block_ID"].unique()

    # ------------------------------
    # Calculate features using registry
    # ------------------------------
    all_features = get_all_features()
    
    # Determine which features to calculate
    if feature_names is None:
        features_to_calc = all_features
    else:
        features_to_calc = {name: all_features[name] for name in feature_names if name in all_features}
    
    # Calculate features in order (respecting dependencies)
    # Note: Features that depend on others should be calculated after their dependencies
    for feature_name, calc_func in features_to_calc.items():
        feature_df = calc_func(feature_df, main_df)

    # ------------------------------
    # Save data
    # ------------------------------
    if feature_data_path:
        feature_df.to_csv(feature_data_path, index=False)

    return feature_df
