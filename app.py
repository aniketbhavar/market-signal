import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page setup
st.set_page_config(page_title="Market Signal POC", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    with open('signals.json', 'r') as f:
        return json.load(f)

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

    try:
        data = load_data()
    except FileNotFoundError:
        st.error("⚠️ Please run Day 1 (Data_Ingestion.py) and Day 2 (signal_analysis.py) first.")
        return

    # Sidebar
    st.sidebar.header("📋 Navigation")
    view_type = st.sidebar.radio(
        "Select View",
        ["Overview", "Indices", "Sectors", "Stocks", "Detailed Analysis"]
    )

    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Last Updated:**  \n{datetime.fromisoformat(data['analysis_time']).strftime('%Y-%m-%d %H:%M:%S')}")

    # CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M%p")
    file_name = f"market_signals_{timestamp}.csv"

    # --- VIEWS ---
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

    else:  # Detailed Analysis
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

        if analysis['projects']:
            st.markdown("### 🎯 Detected Projects")
            display_projects(analysis['projects'])
        else:
            st.info("No opportunity projects detected for this entity.")

if __name__ == "__main__":
    main()
