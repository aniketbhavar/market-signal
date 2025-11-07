import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import math

# Page setup
st.set_page_config(page_title="Market Signal POC", page_icon="📊", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    """
    Try loading AI-enriched data first; if not found, fall back to basic signals.json.
    """
    try:
        with open('signals_enriched.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('signals.json', 'r') as f:
            return json.load(f)

@st.cache_data
def load_hni_data():
    """Load HNI shareholders data from CSV"""
    return pd.read_csv('final_shareholders_with_networth.csv')

# --- VISUALIZATION HELPERS ---
def create_performance_chart(data, entity_type):
    """Bar chart showing weekly change by signal type"""
    items = []
    source = data[entity_type]
    for name, analysis in source.items():
        items.append({
            'Name': name,
            'Weekly Change': analysis['basic_data']['weekly_change'],
            'Signal': analysis['signal']
        })

    df = pd.DataFrame(items)
    color_map = {'BULLISH': '#00cc66', 'NEUTRAL': '#ffaa00', 'BEARISH': '#ff4444'}
    df['Color'] = df['Signal'].map(color_map)

    fig = go.Figure(data=[
        go.Bar(
            x=df['Name'],
            y=df['Weekly Change'],
            marker_color=df['Color'],
            text=df['Weekly Change'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside'
        )
    ])
    fig.update_layout(
        title=f"{entity_type.title()} Weekly Performance",
        xaxis_title="",
        yaxis_title="Weekly Change (%)",
        height=400,
        showlegend=False
    )
    return fig

def create_summary_table(data):
    """Combined overview for indices, sectors, and stocks"""
    rows = []
    for group, gtype in [('indices', 'Index'), ('sectors', 'Sector'), ('stocks', 'Stock')]:
        if group not in data:
            continue
        for name, analysis in data[group].items():
            rows.append({
                "Name": name,
                "Type": gtype,
                "Category": analysis.get('portfolio_category', ''),
                "Price": f"₹{analysis['basic_data']['current_price']:,.2f}",
                "Weekly %": f"{analysis['basic_data']['weekly_change']:+.2f}%",
                "Signal": analysis['signal'],
                "Action": analysis['recommendation']['action'],
                "Adjustment": analysis['recommendation']['adjustment'],
                "Confidence": analysis['recommendation']['confidence']
            })
    return pd.DataFrame(rows)

def display_projects(projects):
    """Render detected opportunity projects"""
    if not projects:
        st.info("No specific projects detected.")
        return
    for i, project in enumerate(projects, 1):
        st.markdown(f"""
        **Project {i}: {project['type']}**  
        {project['description']}  
        *Confidence: {project['confidence']}*
        """)

# --- MAIN APP ---
def main():
    st.title("📊 Market Signal & Portfolio Guidance POC")
    st.markdown("### Real-time Market Analysis for Indices, Sectors & Stocks")

    # Sidebar Navigation
    st.sidebar.header("📋 Navigation")
    view_type = st.sidebar.radio(
        "Select View",
        [
            "Overview",
            "Indices",
            "Sectors",
            "Stocks",
            "Detailed Analysis",
            "Future Predictions",
            "HNI DATA"  # Fixed: matches the conditional check below
        ]
    )

    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # === HNI DATA VIEW ===
    if view_type == "HNI DATA":
        st.subheader("💼 HNI Shareholders Database")
        
        try:
            hni_df = load_hni_data()
            
            # Display column selection based on available columns
            available_cols = hni_df.columns.tolist()
            st.markdown(f"**Available columns:** {', '.join(available_cols)}")
            
            # Try to display with expected columns
            display_cols = []
            for col in ["Stock", "Shareholder Name", "Category", "Net Worth"]:
                if col in hni_df.columns:
                    display_cols.append(col)
            
            if display_cols:
                display_df = hni_df[display_cols].copy()
            else:
                st.warning("Expected columns not found. Showing all columns.")
                display_df = hni_df.copy()
            
            # Add serial number
            display_df.insert(0, "S.No", range(1, len(display_df) + 1))

            # Pagination
            rows_per_page = 20
            total_pages = max(1, math.ceil(len(display_df) / rows_per_page))
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="page_num")
            start = (page - 1) * rows_per_page
            end = start + rows_per_page

            st.markdown("---")
            st.subheader("HNI Data Table")
            st.dataframe(display_df.iloc[start:end], use_container_width=True, height=600)
            st.markdown(f"**Page {page} of {total_pages}** | Total Records: {len(display_df)}")

            # Download button
            st.download_button(
                "📥 Download HNI CSV", 
                display_df.to_csv(index=False), 
                "final_shareholders_with_networth.csv", 
                "text/csv"
            )
                             
        except FileNotFoundError:
            st.error("⚠️ File 'final_shareholders_with_networth.csv' not found!")
            st.info("💡 Make sure the CSV file is in the same directory as this script.")
            
            # Show available CSV files in directory
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            if csv_files:
                st.write("**CSV files found in current directory:**")
                for f in csv_files:
                    st.write(f"- {f}")
            else:
                st.write("No CSV files found in current directory.")
                
        except Exception as e:
            st.error(f"❌ Error loading HNI data: {type(e).__name__}")
            st.write(f"Error details: {str(e)}")
        
        return  # Exit early for HNI view

    # === LOAD MARKET DATA FOR OTHER VIEWS ===
    try:
        data = load_data()
    except FileNotFoundError:
        st.error("⚠️ Please run Day 1 (Data_Ingestion.py), Day 2 (signal_analysis.py), and future_prediction.py first.")
        return

    st.sidebar.markdown("---")
    if "analysis_time" in data:
        st.sidebar.markdown(f"**Last Updated:**  \n{datetime.fromisoformat(data['analysis_time']).strftime('%Y-%m-%d %H:%M:%S')}")

    # CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M%p")
    file_name = f"market_signals_{timestamp}.csv"

    # --- VIEW SECTIONS ---
    if view_type == "Overview":
        all_items = list(data.get('indices', {}).values()) + \
                    list(data.get('sectors', {}).values()) + \
                    list(data.get('stocks', {}).values())

        bullish = sum(1 for x in all_items if x['signal'] == 'BULLISH')
        neutral = sum(1 for x in all_items if x['signal'] == 'NEUTRAL')
        bearish = sum(1 for x in all_items if x['signal'] == 'BEARISH')
        strong_buy = sum(1 for x in all_items if x['recommendation']['action'] == 'STRONG BUY')
        buy = sum(1 for x in all_items if x['recommendation']['action'] == 'BUY')

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🟢 Bullish", bullish)
        col2.metric("🟡 Neutral", neutral)
        col3.metric("🔴 Bearish", bearish)
        col4.metric("⭐ Strong Buy", strong_buy)
        col5.metric("✅ Buy", buy)

        st.markdown("---")
        st.subheader("📋 Combined Market Summary")
        summary_df = create_summary_table(data)
        summary_df.insert(0, "S.No", range(1, len(summary_df) + 1))

        st.data_editor(summary_df, use_container_width=True, hide_index=True, height=600)
        st.download_button("📥 Download CSV", summary_df.to_csv(index=False), file_name, "text/csv")

    elif view_type == "Indices":
        st.subheader("📊 Indices Performance")
        df = create_summary_table({'indices': data['indices']})
        df.insert(0, "S.No", range(1, len(df) + 1))
        st.plotly_chart(create_performance_chart(data, 'indices'), use_container_width=True)
        st.data_editor(df, use_container_width=True, hide_index=True, height=600)
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name, "text/csv")

    elif view_type == "Sectors":
        st.subheader("🏦 Sectoral Performance")
        df = create_summary_table({'sectors': data['sectors']})
        df.insert(0, "S.No", range(1, len(df) + 1))
        st.plotly_chart(create_performance_chart(data, 'sectors'), use_container_width=True)
        st.data_editor(df, use_container_width=True, hide_index=True, height=600)
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name, "text/csv")

    elif view_type == "Stocks":
        st.subheader("📈 Stock Performance")
        df = create_summary_table({'stocks': data['stocks']})
        df.insert(0, "S.No", range(1, len(df) + 1))
        st.plotly_chart(create_performance_chart(data, 'stocks'), use_container_width=True)
        st.data_editor(df, use_container_width=True, hide_index=True, height=600)
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name, "text/csv")

    elif view_type == "Detailed Analysis":
        st.subheader("🔍 Detailed Entity Analysis")

        entity_type = st.selectbox("Select Type", ["Indices", "Sectors", "Stocks"])
        entity_key = entity_type.lower()
        selected = st.selectbox(f"Select {entity_type[:-1]}", list(data[entity_key].keys()))
        analysis = data[entity_key][selected]

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"₹{analysis['basic_data']['current_price']:,.2f}",
                    f"{analysis['basic_data']['daily_change']:+.2f}%")
        col2.metric("Weekly Change", f"{analysis['basic_data']['weekly_change']:+.2f}%")
        col3.metric("Signal", analysis['signal'])

        st.markdown("---")
        rec = analysis['recommendation']

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Action:** {rec['action']}  
            **Adjustment:** {rec['adjustment']}  
            **Confidence:** {rec['confidence']}
            """)
        with col2:
            st.markdown(f"""
            **Target:** ₹{rec['target_price']:,.2f}  
            **Stop Loss:** ₹{rec['stop_loss']:,.2f}  
            **Category:** {analysis['portfolio_category']}
            """)

        st.info(f"**Rationale:** {rec['rationale']}")

        st.markdown("### 📊 Technical Indicators")
        tech = analysis['technical_indicators']
        col1, col2, col3 = st.columns(3)
        col1.metric("RSI", f"{tech['rsi']:.1f}")
        col2.metric("20-day SMA", f"₹{tech['sma_20']:,.2f}")
        col3.metric("Score", tech['score'])

        # --- AI Future Outlook (Optional inline display) ---
        if "future_outlook" in analysis:
            outlook = analysis["future_outlook"]
            st.markdown("### 🤖 AI Future Outlook (Gemini 1.5 Flash)")
            st.markdown(f"""
            **Prediction:** {outlook.get('prediction', 'N/A')}  
            **Expected Change:** {outlook.get('expected_change', 'N/A')}  
            **Confidence:** {outlook.get('confidence', 'N/A')}  
            **Reasoning:** {outlook.get('reasoning', 'N/A')}
            """)

        if analysis['projects']:
            st.markdown("### 🎯 Detected Projects")
            display_projects(analysis['projects'])
        else:
            st.info("No opportunity projects detected for this entity.")

    elif view_type == "Future Predictions":
        st.subheader("🤖 AI-Based Future Outlook (Next 6 to 12 Months)")
        st.markdown(
            "This section displays Gemini 2.0 Flash-Lite generated forecasts for each stock — "
            "including 6-month and 12-month expected changes, confidence levels, and reasoning."
        )

        if "stocks" not in data:
            st.warning("No stock data found. Please run Data_Ingestion.py, signal_analysis.py, and future_prediction.py first.")
        else:
            rows = []

            for name, analysis in data["stocks"].items():
                outlook = analysis.get("future_outlook", {})

                # Parse JSON if stored as a string
                if isinstance(outlook, str):
                    try:
                        outlook = json.loads(outlook)
                    except Exception:
                        outlook = {"prediction": "Neutral", "expected_change_6m": "0%", "expected_change_1y": "0%", "confidence": "Low", "reasoning": outlook}

                reasoning = outlook.get("reasoning", "")
                short_reason = reasoning[:120] + "..." if len(reasoning) > 120 else reasoning

                rows.append({
                    "Name": name,
                    "Prediction": outlook.get("prediction", "Neutral"),
                    "6-Month Change": outlook.get("expected_change_6m", "0%"),
                    "1-Year Change": outlook.get("expected_change_1y", "0%"),
                    "Confidence": outlook.get("confidence", "Low"),
                    "Short Reasoning": short_reason,
                    "Full Reasoning": reasoning
                })

            df = pd.DataFrame(rows)

            st.markdown("### 📈 Summary Table")
            st.dataframe(
                df[["Name", "Prediction", "6-Month Change", "1-Year Change", "Confidence", "Short Reasoning"]],
                use_container_width=True,
                height=500,
            )

            # --- Detailed reasoning viewer ---
            st.markdown("---")
            st.markdown("### 🧩 Detailed Reasoning Explorer")
            selected_stock = st.selectbox("Select a stock to view full reasoning", [""] + df["Name"].tolist())
            if selected_stock:
                full_reasoning = df.loc[df["Name"] == selected_stock, "Full Reasoning"].values[0]
                st.markdown(f"**{selected_stock} — Full AI Reasoning:**")
                st.write(full_reasoning if full_reasoning else "No detailed reasoning available.")

        st.markdown("---")
        st.caption("🕒 Last updated: " + str(data.get("forecast_time", "N/A")))


if __name__ == "__main__":
    main()
