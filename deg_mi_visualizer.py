

from aux import *


# streamlit run deg_mi_visualizer.py
# This script visualizes DEG vs MI data using Streamlit and Plotly.
# It allows users to upload an Excel file containing merged DEG and MI data,
# filter the data, and create various scatter plots with options for gene annotations.


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
            # fill NaN values in 'p_val_adj' with 1.0
            df['p_val_adj_N6'] = df['p_val_adj_N6'].fillna(1.0)


            
            # Display basic info about the dataset
            st.sidebar.subheader("📈 Dataset Info")
            st.sidebar.write(f"**Total genes:** {len(df)}")
            st.sidebar.write(f"**Columns:** {len(df.columns)}")
            
            # Check for required columns
            required_columns = ['MI_with_condition', 'avg_log2FC_N6', 'is_mitocarta', 'p_val_adj_log10_N6', 'Il10', 'pct_ratio_N6']
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
                value=0.05,
                step=0.001
            )
            
            # Regulation filter
            regulation_filter = st.sidebar.selectbox(
                "Gene regulation filter",
                options=["Both", "Up-regulated only", "Down-regulated only"],
                index=0,
                help="Filter genes based on their regulation status (avg_log2FC)"
            )
            
            # Gene annotation options
            st.sidebar.subheader("🏷️ Gene Annotations")
            
            # Get available genes for annotation selection
            available_genes = sorted(df.index.tolist())
            default_genes = []
            # Only keep default genes that are actually in the dataset
            default_genes = [gene for gene in default_genes if gene in available_genes]
                        
            # Multiselect for gene annotation
            genes_to_annotate = st.sidebar.multiselect(
                "Select genes to annotate on plots",
                options=available_genes,
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
                (df['p_val_adj_N6'] <= pval_max)
            ]
            
            # Apply regulation filter
            if regulation_filter == "Up-regulated only":
                filtered_df = filtered_df[filtered_df['avg_log2FC_N6'] > 0]
                filtered_df = filtered_df.sort_values(by="avg_log2FC_N6", ascending=False)
            elif regulation_filter == "Down-regulated only":
                filtered_df = filtered_df[filtered_df['avg_log2FC_N6'] < 0]
                filtered_df = filtered_df.sort_values(by="avg_log2FC_N6", ascending=True)
            # If "Both" is selected, no additional filtering is needed
            
            st.sidebar.write(f"**Filtered genes:** {len(filtered_df)}")
            
            # Main content
            st.header("📊 Scatter Plots")
            # Show data preview
            # print small values as 10-n
            st.subheader("Data Preview")
            filtered_df_display = filtered_df.copy()
            # Display the filtered DataFrame
            st.dataframe(filtered_df_display)
            # print df size
            st.write(f"Data size: {filtered_df_display.shape[0]} rows, {filtered_df_display.shape[1]} columns")
            st.markdown("---")

        
            
            # Find all binary columns (columns that contain only 0s and 1s)
            binary_columns = ['is_mitocarta',
                                  'decrease_IL10_day7',
                                  'increase_IL10_day7',
                                  'decrease_IL10_day3',
                                  'increase_IL10_day3',
                                  'proteomics_UP_7day',
                                  'proteomics_DOWN_7day']

            selected_binary_column = st.selectbox(
                "Select category to highlight in the scatter plot:",
                options=binary_columns,
                index=0,
                help="Choose which binary category to highlight with a different color in the scatter plot"
            )

            # Create tabs for different plot types
            tab0,tab1,tab1_bis,tab2, tab3, tab4, tab5 = st.tabs([
                "🏷️ avg_log2FC vs log10(pval)", 
                "🏷️ condition MI vs avg_log2FC", 
                "🏷️ condition MI vs IL10", 
                "📊 Pct Ratio", 
                "🌋 Volcano (MI)", 
                "🌋 Volcano (IL10)", 
                "🌋 Volcano (Pct)"
            ])
            
            with tab0:

                fig1 = scatter_highlight(filtered_df, f"(n={len(filtered_df)})", genes_to_annotate, selected_binary_column,x='avg_log2FC_N6', y='p_val_adj_log10_N6')
                st.plotly_chart(fig1, use_container_width=True)


            with tab1:
                
                fig1 = scatter_highlight(filtered_df, f"(n={len(filtered_df)})", genes_to_annotate, selected_binary_column, x='MI_with_condition', y='avg_log2FC_N6')
                st.plotly_chart(fig1, use_container_width=True)

            with tab1_bis:
                
                fig1_bis = scatter_highlight(filtered_df, f"(n={len(filtered_df)})", genes_to_annotate, selected_binary_column, x='MI_with_condition', y='Il10')
                st.plotly_chart(fig1_bis, use_container_width=True)

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
                st.subheader("Volcano Plot - Colored min pct")
                fig5 = create_volcano_pct_ratio_scatter(filtered_df, f"(n={len(filtered_df)})")
                st.plotly_chart(fig5, use_container_width=True)
            

                
    else:
        st.info("👆 Please upload an Excel file to get started")


if __name__ == "__main__":
    main()
