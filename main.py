import streamlit as st
import pandas as pd
from src.data_cleaning import prepare_data, create_feature_dataframe
from src.graphs import get_all_plot_types, get_plot_function, create_streamlit_config_widgets

# Page configuration
st.set_page_config(
    page_title="Heterokaryon Analysis",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
        .scrollable-container {
            max-height: 80vh;   /* height of the scroll box */
            overflow-y: auto;   /* enable vertical scrolling */
            padding-right: 10px; /* so content is not cut off */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Define paths
RAW_DATA_PATH = 'data/heterokaryon_analysis.csv'
CLEANED_DATA_PATH = 'data/heterokaryon_analysis_cleaned.csv'
FEATURE_DATA_PATH = 'data/heterokaryon_analysis_features.csv'

# Cache data loading functions
@st.cache_data
def load_cleaned_data():
    """Load or generate cleaned data."""
    try:
        df = pd.read_csv(CLEANED_DATA_PATH)
    except FileNotFoundError:
        # Generate cleaned data if it doesn't exist
        df = prepare_data(RAW_DATA_PATH, CLEANED_DATA_PATH)
    return df

@st.cache_data
def load_feature_data():
    """Load or generate feature data."""
    try:
        df = pd.read_csv(FEATURE_DATA_PATH)
    except FileNotFoundError:
        # Generate feature data if it doesn't exist
        _ = load_cleaned_data()
        df = create_feature_dataframe(CLEANED_DATA_PATH, FEATURE_DATA_PATH)
    return df

def style_by_block_id(df):
    """Apply very subtle, transparent background color based on Block_ID (even vs odd)."""
    def highlight_row(row):
        """Apply very transparent background color based on Block_ID."""
        block_id = int(row['Block_ID'])
        # Use rgba with very low opacity for transparency
        # Even blocks: very light gray with low opacity
        # Odd blocks: white (no background)
        if block_id % 2 == 0:
            color = 'rgba(248, 249, 250, 0.1)'
        else:
            color = 'transparent'
        return ['background-color: ' + color] * len(row)
    
    styled = df.style.apply(highlight_row, axis=1)
    styled = styled.hide(axis='index')
    return styled

# Main app
def main():
    st.title("📊 Heterokaryon Analysis Dashboard")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["Data", "Graph Generator", "Stored Graphs"])
    
    # Data Tab
    with tab1:
        # Subtabs within Data tab
        subtab1, subtab2 = st.tabs(["Raw Data", "Aggregated Features"])
        
        # Raw Data subtab
        with subtab1:
            st.header("Base Data")
            cleaned_df = load_cleaned_data()
            styled_cleaned = style_by_block_id(cleaned_df)
            st.dataframe(styled_cleaned, use_container_width=True, hide_index=True)
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(cleaned_df))
            with col2:
                st.metric("Number of Blocks", cleaned_df['Block_ID'].nunique())
            with col3:
                st.metric("Number of Types", cleaned_df['Type'].nunique())
        
        # Aggregated Features subtab
        with subtab2:
            st.header("Aggregated Features")
            feature_df = load_feature_data()
            styled_features = style_by_block_id(feature_df)
            st.dataframe(styled_features, use_container_width=True, hide_index=True)
            
            # Display summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Blocks", len(feature_df))
            with col2:
                st.metric("Number of Features", len(feature_df.columns) - 1)  # -1 for Block_ID
    
    # Graph Generator Tab
    with tab2:
        st.header("Graph Generator")

        # Get available plot types from registry
        plot_types = get_all_plot_types()
        
        if not plot_types:
            st.warning("No plot types registered. Add plot functions to src/graphs.py with @register_plot_type decorator.")
        else:
            # Create layout with sidebars
            col_left, col_main, col_right = st.columns([1, 3, 1])
            
            # Left sidebar: Plot type selection
            with col_left:
                st.subheader("Plot Type")
                plot_type_names = {name: info['display_name'] for name, info in plot_types.items()}
                selected_plot_type = st.radio(
                    "Select plot type:",
                    options=list(plot_type_names.keys()),
                    format_func=lambda x: plot_type_names[x],
                    label_visibility="collapsed"
                )
                
                # Show description
                if selected_plot_type in plot_types:
                    st.caption(plot_types[selected_plot_type]['description'])
            
            # Right sidebar: Configuration
            with col_right:
                st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
                st.subheader("Configuration")
                
                # Data source selection
                data_source = st.radio(
                    "Data source:",
                    ["Base Data", "Aggregated Features"],
                    index=0
                )
                
                # Load appropriate data
                if data_source == "Base Data":
                    plot_data = load_cleaned_data()
                else:
                    plot_data = load_feature_data()
                
                # Create configuration widgets
                config = create_streamlit_config_widgets(selected_plot_type, plot_data)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Main area: Display plot
            with col_main:
                if selected_plot_type:
                    try:
                        # Get the plot function
                        plot_func = get_plot_function(selected_plot_type)
                        
                        if plot_func:
                            # Prepare arguments
                            plot_args = {'data': plot_data, **config}
                            
                            # Generate plot
                            fig = plot_func(**plot_args)
                            
                            # Display plot
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"Plot function not found for {selected_plot_type}")
                    except Exception as e:
                        st.error(f"Error generating plot: {str(e)}")
                        st.exception(e)
                else:
                    st.info("Select a plot type from the left sidebar to get started.")
    
    # Stored Graphs Tab
    with tab3:
        st.header("Stored Graphs")
        st.info("Previously generated graphs will be displayed here.")
        # Placeholder for stored graphs functionality

if __name__ == "__main__":
    main()
