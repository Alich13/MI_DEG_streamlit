import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path


# streamlit run deg_mi_visualizer.py
# This script visualizes DEG vs MI data using Streamlit and Plotly.
# It allows users to upload an Excel file containing merged DEG and MI data,
# filter the data, and create various scatter plots with options for gene annotations.


# Set page configuration
st.set_page_config(
    page_title="DEG vs MI Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data(file_path):
    """Load data from Excel file"""
    try:
        # Try to load the first sheet (usually 'sorted_by_pval')
        df = pd.read_excel(file_path, sheet_name=0, index_col=0)
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def create_mitocarta_scatter(df, title_suffix="", genes_to_annotate=None):
    """Create scatter plot with MitoCarta genes highlighted in red"""
    # Use provided genes or default list
    if genes_to_annotate is None:
        genes_to_annotate = ['Klra4', 'Jchain', 'Ighg2b', 'Bank1', 'mt-Nd3']
    
    fig = px.scatter(
        df,
        x='MI_with_condition',
        y='avg_log2FC',
        color=df['is_mitocarta'].map({1: 'MitoCarta', 0: 'Other'}),
        color_discrete_map={'MitoCarta': 'red', 'Other': 'blue'},
        hover_data={
            'gene': df.index, 
            'p_val_adj': True, 
            'p_val': True, 
            'is_mitocarta': True,
            'Il10': True,
            'pct_ratio': True,
            'pct.1': True,
            'pct.2': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC': 'Average log2 Fold Change'
        },
        title=f'Scatter plot of MI vs avg_log2FC (MitoCarta genes in red) {title_suffix}'
    )
    
    # Add text annotations for selected genes
    for gene in genes_to_annotate:
        if gene in df.index:
            row = df.loc[gene]
            fig.add_annotation(
                x=row['MI_with_condition'],
                y=row['avg_log2FC'],
                text=gene,
                showarrow=True,
                arrowhead=1,
                ax=20,
                ay=-20,
                font=dict(color="black", size=12)
            )
    
    return fig

def create_pct_ratio_scatter(df, title_suffix=""):
    """Create scatter plot colored by pct_ratio"""
    fig = px.scatter(
        df,
        x='MI_with_condition',
        y='avg_log2FC',
        color='pct_ratio',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj': True, 
            'p_val': True, 
            'is_mitocarta': True,
            'Il10': True,
            'pct_ratio': True,
            'pct.1': True,
            'pct.2': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC': 'Average log2 Fold Change'
        },
        title=f'Scatter plot of MI vs avg_log2FC (colored by pct_ratio) {title_suffix}'
    )
    return fig

def create_volcano_mi_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by MI"""
    fig = px.scatter(
        df,
        y='p_val_adj_log10',
        x='avg_log2FC',
        color='MI_with_condition',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj': True, 
            'p_val': True,
            'Il10': True,
            'pct_ratio': True,
            'pct.1': True,
            'pct.2': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC': 'Average log2 Fold Change',
            'p_val_adj_log10': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by MI {title_suffix}'
    )
    return fig

def create_volcano_il10_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by IL10"""
    fig = px.scatter(
        df,
        y='p_val_adj_log10',
        x='avg_log2FC',
        color='Il10',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj': True, 
            'p_val': True,
            'Il10': True,
            'pct_ratio': True,
            'pct.1': True,
            'pct.2': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC': 'Average log2 Fold Change',
            'p_val_adj_log10': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by IL10 {title_suffix}'
    )
    return fig

def create_volcano_pct_ratio_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by pct_ratio"""
    fig = px.scatter(
        df,
        y='p_val_adj_log10',
        x='avg_log2FC',
        color='pct_ratio',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj': True, 
            'p_val': True,
            'Il10': True,
            'pct_ratio': True,
            'pct.1': True,
            'pct.2': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC': 'Average log2 Fold Change',
            'p_val_adj_log10': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by pct_ratio {title_suffix}'
    )
    return fig

def main():
    st.title("📊 DEG vs MI Visualizer")
    st.markdown("---")
    
    # Sidebar for file upload
    st.sidebar.header("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel file containing merged DEG/MI data",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with merged DEG and MI data"
    )
    
    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ Successfully loaded data with {len(df)} genes")
            
            # Display basic info about the dataset
            st.sidebar.subheader("📈 Dataset Info")
            st.sidebar.write(f"**Total genes:** {len(df)}")
            st.sidebar.write(f"**Columns:** {len(df.columns)}")
            
            # Check for required columns
            required_columns = ['MI_with_condition', 'avg_log2FC', 'is_mitocarta', 'p_val_adj_log10', 'Il10', 'pct_ratio']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {missing_columns}")
                st.info("Please ensure your Excel file contains the merged DEG/MI data with all required columns.")
                return
            
            # Filter options
            st.sidebar.subheader("🔍 Filter Options")
            
            # MI filter
            mi_min = st.sidebar.slider(
                "Minimum MI value",
                min_value=float(df['MI_with_condition'].min()),
                max_value=float(df['MI_with_condition'].max()),
                value=float(df['MI_with_condition'].min()),
                step=0.001
            )
            
            # P-value filter
            pval_max = st.sidebar.slider(
                "Maximum adjusted p-value",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.01
            )
            
            # Gene annotation options
            st.sidebar.subheader("🏷️ Gene Annotations")
            
            # Get available genes for annotation selection
            available_genes = sorted(df.index.tolist())
            default_genes = []
            # Only keep default genes that are actually in the dataset
            default_genes = [gene for gene in default_genes if gene in available_genes]
            
            # Search box for genes
            gene_search = st.sidebar.text_input(
                "🔍 Search for genes",
                placeholder="Type gene name...",
                help="Search for specific genes to add to annotation list"
            )
            
            # Filter genes based on search
            if gene_search:
                filtered_genes = [gene for gene in available_genes if gene_search.lower() in gene.lower()]
                st.sidebar.write(f"Found {len(filtered_genes)} genes matching '{gene_search}'")
                if len(filtered_genes) <= 20:  # Show matches if not too many
                    st.sidebar.write("Matches:", ", ".join(filtered_genes[:10]))
                    if len(filtered_genes) > 10:
                        st.sidebar.write("... and more")
            else:
                filtered_genes = available_genes
            
            # Multiselect for gene annotation
            genes_to_annotate = st.sidebar.multiselect(
                "Select genes to annotate on plots",
                options=filtered_genes if gene_search else available_genes,
                default=default_genes,
                help="Choose which genes to label on the scatter plots"
            )
            
            # Option to show/hide annotations
            show_annotations = st.sidebar.checkbox(
                "Show gene annotations",
                value=True,
                help="Toggle gene labels on/off"
            )
            
            # If annotations are disabled, clear the gene list
            if not show_annotations:
                genes_to_annotate = []
                
            # Show selected genes count
            if genes_to_annotate:
                st.sidebar.write(f"📌 {len(genes_to_annotate)} genes selected for annotation")
            
            # Apply filters
            filtered_df = df[
                (df['MI_with_condition'] >= mi_min) & 
                (df['p_val_adj'] <= pval_max)
            ]
            
            st.sidebar.write(f"**Filtered genes:** {len(filtered_df)}")
            
            # Main content
            st.header("📊 Scatter Plots")
            
            # Create tabs for different plot types
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔴 MitoCarta Genes", 
                "📊 Pct Ratio", 
                "🌋 Volcano (MI)", 
                "🌋 Volcano (IL10)", 
                "🌋 Volcano (Pct Ratio)"
            ])
            
            with tab1:
                st.subheader("MitoCarta Genes Highlighted")
                fig1 = create_mitocarta_scatter(filtered_df, f"(n={len(filtered_df)})", genes_to_annotate)
                st.plotly_chart(fig1, use_container_width=True)
                
            with tab2:
                st.subheader("Colored by Percentage Ratio")
                fig2 = create_pct_ratio_scatter(filtered_df, f"(n={len(filtered_df)})")
                st.plotly_chart(fig2, use_container_width=True)
                
            with tab3:
                st.subheader("Volcano Plot - Colored by Mutual Information")
                fig3 = create_volcano_mi_scatter(filtered_df, f"(n={len(filtered_df)})")
                st.plotly_chart(fig3, use_container_width=True)
                
            with tab4:
                st.subheader("Volcano Plot - Colored by IL10")
                fig4 = create_volcano_il10_scatter(filtered_df, f"(n={len(filtered_df)})")
                st.plotly_chart(fig4, use_container_width=True)
                
            with tab5:
                st.subheader("Volcano Plot - Colored by Percentage Ratio")
                fig5 = create_volcano_pct_ratio_scatter(filtered_df, f"(n={len(filtered_df)})")
                st.plotly_chart(fig5, use_container_width=True)
            
            # Display summary statistics
            st.header("📋 Summary Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("MitoCarta Genes")
                mitocarta_count = filtered_df['is_mitocarta'].sum()
                st.metric("Count", mitocarta_count)
                st.metric("Percentage", f"{mitocarta_count/len(filtered_df)*100:.1f}%")
                
            with col2:
                st.subheader("Key Statistics")
                st.metric("Mean MI", f"{filtered_df['MI_with_condition'].mean():.3f}")
                st.metric("Mean log2FC", f"{filtered_df['avg_log2FC'].mean():.3f}")
                st.metric("Median p-val", f"{filtered_df['p_val_adj'].median():.2e}")
            
            # Show data preview
            with st.expander("🔍 Data Preview"):
                st.dataframe(filtered_df.head(20))
                
    else:
        st.info("👆 Please upload an Excel file to get started")
        st.markdown("""
        ### Expected File Format
        
        The Excel file should contain merged DEG/MI data with the following columns:
        - `MI_with_condition`: Mutual Information values
        - `avg_log2FC`: Average log2 fold change
        - `is_mitocarta`: Binary indicator for MitoCarta genes (1/0)
        - `p_val_adj_log10`: -log10 of adjusted p-values
        - `Il10`: IL10 values
        - `pct_ratio`: Percentage ratio
        - `p_val_adj`: Adjusted p-values
        - `p_val`: Raw p-values
        - `pct.1`, `pct.2`: Percentage values for conditions
        
        Gene names should be in the index.
        """)

if __name__ == "__main__":
    main()
