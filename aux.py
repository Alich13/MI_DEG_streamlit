import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path


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

def scatter_highlight(df, title_suffix="", genes_to_annotate=None, binary_column=None, y='avg_log2FC_N6', x='MI_with_condition'):
    """Create scatter plot with selected binary column highlighted in different colors"""

    # If no binary column selected, use default MitoCarta
    if binary_column is None:
        binary_column = 'is_mitocarta'
    
    # Create a combined category column for coloring
    df_plot = df.copy()
     
    # Create category labels
    df_plot['category'] = 'Other'
    if binary_column in df.columns:
        mask = df_plot[binary_column] == 1
        df_plot.loc[mask, 'category'] = binary_column
    
    # Define color mapping
    color_map = {'Other': 'blue', binary_column: 'red'}
    
    fig = px.scatter(
        df_plot,
        x=x,
        y=y,
        color='category',
        color_discrete_map=color_map,
        hover_data={
            'gene': df.index, 
            'p_val_adj_N6': True, 
            'Il10': True,
            'Il6': True,
            'pct_ratio_N6': True,
            'pct.1_N6': True,
            'pct.2_N6': True
        },
        labels={
            x: x.replace('_', ' ').title(),
            y: y.replace('_', ' ').title()
        },
        title=f'Scatter plot of {x} vs {y} ({binary_column} highlighted) {title_suffix}'
    )
    
    # Add text annotations for selected genes
    for gene in genes_to_annotate:
        if gene in df.index:
            row = df.loc[gene]
            fig.add_annotation(
                x=row[x],
                y=row[y],
                text=gene,
                showarrow=True,
                arrowhead=1,
                ax=20,
                ay=-20,
                font=dict(color="black", size=12)
            )
    
    return fig

def create_pct_ratio_scatter(df, title_suffix=""):
    """Create scatter plot colored by pct_ratio_N6"""
    fig = px.scatter(
        df,
        x='MI_with_condition',
        y='avg_log2FC_N6',
        color='pct_ratio_N6',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj_N6': True, 
            'Il10': True,
            'Il6': True,
            'pct_ratio_N6': True,
            'pct.1_N6': True,
            'pct.2_N6': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC_N6': 'Average log2 Fold Change'
        },
        title=f'Scatter plot of MI vs avg_log2FC_N6 (colored by pct_ratio_N6) {title_suffix}'
    )
    return fig

def create_volcano_mi_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by MI"""
    fig = px.scatter(
        df,
        y='p_val_adj_log10_N6',
        x='avg_log2FC_N6',
        color='MI_with_condition',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj_N6': True, 
            'Il10': True,
            'Il6': True,
            'pct_ratio_N6': True,
            'pct.1_N6': True,
            'pct.2_N6': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC_N6': 'Average log2 Fold Change',
            'p_val_adj_log10_N6': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by MI {title_suffix}'
    )
    return fig

def create_volcano_il10_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by IL10"""
    fig = px.scatter(
        df,
        y='p_val_adj_log10_N6',
        x='avg_log2FC_N6',
        color='Il10',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj_N6': True, 
            'Il10': True,
            'Il6': True,
            'pct_ratio_N6': True,
            'pct.1_N6': True,
            'pct.2_N6': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC_N6': 'Average log2 Fold Change',
            'p_val_adj_log10_N6': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by IL10 {title_suffix}'
    )
    return fig

def create_volcano_pct_ratio_scatter(df, title_suffix=""):
    """Create volcano-style plot colored by pct_ratio_N6"""

    #df["pct_ratio_N6_log"] = np.log10(df["pct_ratio_N6"].replace(0, np.nan))  # Handle zero values for log transformation
    df["min_pct"] = min(df["pct.1"],df["pct.2"])  # Handle zero values for log transformation


    fig = px.scatter(
        df,
        y='p_val_adj_log10_N6',
        x='avg_log2FC_N6',
        color='min_pct',
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_data={
            'gene': df.index, 
            'p_val_adj_N6': True, 
            'Il10': True,
            'Il6': True,
            'pct_ratio_N6': True,
            'pct.1_N6': True,
            'pct.2_N6': True
        },
        labels={
            'MI_with_condition': 'Mutual Information (condition)', 
            'avg_log2FC_N6': 'Average log2 Fold Change',
            'p_val_adj_log10_N6': '-log10(adjusted p-value)'
        },
        title=f'Volcano plot colored by min_pct {title_suffix}'
    )
    return fig
