from src.data_cleaning import prepare_data, create_feature_dataframe

if __name__ == "__main__":
    # Define paths
    RAW_DATA_PATH = 'data/heterokaryon_analysis.csv'
    CLEANED_DATA_PATH = 'data/heterokaryon_analysis_cleaned.csv'
    FEATURE_DATA_PATH = 'data/heterokaryon_analysis_features.csv'
    
    # Clean the data and add features
    cleaned_df = prepare_data(RAW_DATA_PATH, CLEANED_DATA_PATH)
    
    print(cleaned_df.head(10))
    print("Total number of rows in cleaned dataframe: ", len(cleaned_df))

    print("\n--------------------------------\n")

    # Create feature dataframe
    feature_df = create_feature_dataframe(CLEANED_DATA_PATH, FEATURE_DATA_PATH)

    print(feature_df.head(10))
    print("Total number of rows in feature dataframe: ", len(feature_df))