import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==================================================
# PAGE CONFIG (MUST BE FIRST)
# ==================================================

st.set_page_config(
    page_title="Traffic Analysis Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "traffic.csv"
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def generate_insights(df_filtered):
    """Generate dynamic business insights based on real data"""
    insights = []

    avg_conv = df_filtered['Conversion Rate'].mean()
    avg_bounce = df_filtered['Bounce Rate'].mean()
    avg_session = df_filtered['Session Duration'].mean()
    avg_time = df_filtered['Time on Page'].mean()

    # Conversion insight — note: "Conversion Rate" in this dataset is a
    # per-session flag, so the average is "share of sessions with a
    # conversion event," not a typical site-wide conversion rate benchmark.
    insights.append(
        f"📊 **{avg_conv:.1%} of sessions included a conversion event** in this dataset. "
        f"Because this is synthetic data, treat this as a relative signal across traffic "
        f"sources rather than a real-world conversion rate benchmark."
    )

    # Bounce rate insights
    if avg_bounce < 0.20:
        insights.append(f"🌟 **Excellent bounce rate** ({avg_bounce:.1%}) – visitors are highly engaged!")
    elif avg_bounce < 0.35:
        insights.append(f"👌 **Good bounce rate** ({avg_bounce:.1%}) – above industry average.")
    else:
        insights.append(f"🔄 **Bounce rate** at {avg_bounce:.1%}. Consider improving landing page experience.")

    # Session duration
    if avg_session > 5:
        insights.append(f"⏱️ **Great engagement** – {avg_session:.1f}s average session duration.")
    elif avg_session > 3:
        insights.append(f"📊 **Decent engagement** – {avg_session:.1f}s average session.")
    else:
        insights.append(f"⚡ **Short sessions** ({avg_session:.1f}s) – consider adding more engaging content.")

    # Time on page correlation
    if avg_time > 5:
        insights.append(f"📖 **Strong time on page** ({avg_time:.1f}s) – content is resonating with visitors.")

    # Best performing source
    if len(df_filtered['Traffic Source'].unique()) > 1:
        best_source = df_filtered.groupby('Traffic Source')['Conversion Rate'].mean().idxmax()
        best_conv = df_filtered.groupby('Traffic Source')['Conversion Rate'].mean().max()
        insights.append(f"💡 **Top channel**: '{best_source}' converts at {best_conv:.1%} – invest more here!")

    # Previous visits insight
    avg_prev = df_filtered['Previous Visits'].mean()
    if avg_prev > 2.5:
        insights.append(f"🔄 **Strong returning visitors** ({avg_prev:.1f} avg) – loyalty is building!")
    elif avg_prev > 1.5:
        insights.append(f"👋 **Moderate returning visitors** ({avg_prev:.1f} avg).")
    else:
        insights.append(f"🆕 **Mostly new visitors** ({avg_prev:.1f} avg) – focus on first-time experience.")

    # Correlation insight (with safety check)
    if len(df_filtered) > 10:  # Only calculate if enough data
        try:
            corr_data = df_filtered[['Time on Page', 'Session Duration', 'Bounce Rate', 'Conversion Rate']].corr()
            if 'Conversion Rate' in corr_data.columns:
                conv_corr = corr_data['Conversion Rate']
                if 'Time on Page' in conv_corr and abs(conv_corr['Time on Page']) > 0.1:
                    direction = "positive" if conv_corr['Time on Page'] > 0 else "negative"
                    insights.append(f"📈 **Time on Page shows {direction} correlation** with conversion ({conv_corr['Time on Page']:.2f}).")
        except:
            pass  # Skip correlation if it fails

    return insights

def get_traffic_performance(df):
    """Calculate performance scores"""
    performance = df.groupby('Traffic Source').agg({
        'Conversion Rate': 'mean',
        'Bounce Rate': 'mean',
        'Session Duration': 'mean',
        'Page Views': 'mean',
        'Time on Page': 'mean'
    }).round(4)

    # Score calculation (normalized)
    performance['Conversion_Score'] = (performance['Conversion Rate'] - performance['Conversion Rate'].min()) / (performance['Conversion Rate'].max() - performance['Conversion Rate'].min())
    performance['Bounce_Score'] = 1 - (performance['Bounce Rate'] - performance['Bounce Rate'].min()) / (performance['Bounce Rate'].max() - performance['Bounce Rate'].min())
    performance['Duration_Score'] = (performance['Session Duration'] - performance['Session Duration'].min()) / (performance['Session Duration'].max() - performance['Session Duration'].min())
    performance['Overall_Score'] = (
        performance['Conversion_Score'] * 0.4 +
        performance['Bounce_Score'] * 0.3 +
        performance['Duration_Score'] * 0.3
    ).round(3)

    return performance.sort_values('Overall_Score', ascending=False)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.title("🎛️ Filters")

# Traffic source filter
sources = ['All'] + sorted(df['Traffic Source'].unique())
selected_source = st.sidebar.selectbox("Traffic Source", sources)

# Metric selector
metric_options = {
    'Conversion Rate': 'Conversion Rate',
    'Bounce Rate': 'Bounce Rate',
    'Session Duration': 'Session Duration',
    'Time on Page': 'Time on Page'
}
selected_metric = st.sidebar.selectbox("Metric View", list(metric_options.keys()))

# Apply filters
df_filtered = df.copy()
if selected_source != 'All':
    df_filtered = df_filtered[df_filtered['Traffic Source'] == selected_source]

# ==================================================
# SIDEBAR STATS
# ==================================================

st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Stats**")
st.sidebar.metric("Total Sessions", f"{len(df_filtered):,}")
st.sidebar.metric("Traffic Sources", f"{len(df_filtered['Traffic Source'].unique())}")

# ==================================================
# MAIN DASHBOARD
# ==================================================

# Header
st.title("🚀 Traffic Analysis Dashboard")
st.markdown("*Understand your visitors, optimize performance, grow your business*")
st.markdown("---")

# ---- KPI ROW ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Replaced the flat "Conversion Rate" KPI: averaging that column across
    # all sessions produced a misleading ~98% headline number. Top traffic
    # source is a more honest single-number summary at a glance.
    source_counts = df_filtered['Traffic Source'].value_counts()
    top_source = source_counts.idxmax()
    top_source_share = source_counts.max() / len(df_filtered) if len(df_filtered) > 0 else 0
    st.metric(
        label="Top Traffic Source",
        value=top_source,
        delta=f"{top_source_share:.1%} of sessions"
    )

with col2:
    bounce_rate = df_filtered['Bounce Rate'].mean()
    st.metric(
        label="Bounce Rate",
        value=f"{bounce_rate:.1%}",
        delta=f"{((bounce_rate - df['Bounce Rate'].mean()) / df['Bounce Rate'].mean() * 100):.1f}% vs avg" if df['Bounce Rate'].mean() != 0 else None,
        delta_color="inverse"
    )

with col3:
    session_dur = df_filtered['Session Duration'].mean()
    st.metric(
        label="Avg Session Duration",
        value=f"{session_dur:.1f}s",
        delta=f"{df_filtered['Previous Visits'].mean():.1f} avg visits"
    )

with col4:
    time_on_page = df_filtered['Time on Page'].mean()
    st.metric(
        label="Avg Time on Page",
        value=f"{time_on_page:.1f}s",
        delta=f"{df_filtered['Page Views'].mean():.1f} avg page views"
    )

# ---- INSIGHTS ----
st.markdown("---")
with st.expander("💡 Key Insights", expanded=True):
    insights = generate_insights(df_filtered)
    for insight in insights:
        st.markdown(f"- {insight}")

# ---- CHARTS ROW 1 ----
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Traffic source performance
    perf_data = df_filtered.groupby('Traffic Source')[metric_options[selected_metric]].mean().reset_index()
    fig_perf = px.bar(
        perf_data,
        x='Traffic Source',
        y=metric_options[selected_metric],
        title=f"{selected_metric} by Traffic Source",
        color=metric_options[selected_metric],
        color_continuous_scale='Blues' if 'Conversion' in selected_metric else 'Reds' if 'Bounce' in selected_metric else 'Viridis',
        text=metric_options[selected_metric]
    )
    if 'Rate' in selected_metric:
        fig_perf.update_traces(texttemplate='%{text:.1%}', textposition='outside')
    elif 'Duration' in selected_metric or 'Time' in selected_metric:
        fig_perf.update_traces(texttemplate='%{text:.1f}s', textposition='outside')
    else:
        fig_perf.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_perf.update_layout(showlegend=False, margin=dict(t=40, b=40))
    st.plotly_chart(fig_perf, use_container_width=True)

with col2:
    # Traffic distribution donut
    source_dist = df_filtered['Traffic Source'].value_counts().reset_index()
    source_dist.columns = ['Source', 'Count']
    fig_donut = px.pie(
        source_dist,
        values='Count',
        names='Source',
        hole=0.5,
        title="Traffic Distribution",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_donut.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2))
    st.plotly_chart(fig_donut, use_container_width=True)

# ---- CHARTS ROW 2 ----
col1, col2 = st.columns(2)

with col1:
    # Bounce rate by source
    bounce_data = df_filtered.groupby('Traffic Source')['Bounce Rate'].mean().reset_index()
    fig_bounce = px.bar(
        bounce_data,
        x='Traffic Source',
        y='Bounce Rate',
        title="Bounce Rate by Traffic Source",
        color='Bounce Rate',
        color_continuous_scale='Reds_r',
        text='Bounce Rate'
    )
    fig_bounce.update_traces(texttemplate='%{text:.1%}', textposition='outside')
    fig_bounce.update_layout(showlegend=False, margin=dict(t=40, b=40))
    st.plotly_chart(fig_bounce, use_container_width=True)

with col2:
    # Time on Page vs Conversion
    fig_scatter = px.scatter(
        df_filtered,
        x='Time on Page',
        y='Conversion Rate',
        color='Traffic Source',
        size='Session Duration',
        hover_data=['Bounce Rate', 'Previous Visits', 'Page Views'],
        title="Time on Page vs Conversion Rate"
    )
    fig_scatter.update_layout(
        yaxis_tickformat='.0%',
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---- CHARTS ROW 3 ----
col1, col2 = st.columns(2)

with col1:
    # Previous visits impact
    prev_data = df_filtered.groupby('Previous Visits')['Conversion Rate'].mean().reset_index()
    fig_prev = px.line(
        prev_data,
        x='Previous Visits',
        y='Conversion Rate',
        title="Previous Visits Impact on Conversion",
        markers=True,
        color_discrete_sequence=['#00cc96']
    )
    fig_prev.update_layout(yaxis_tickformat='.0%', hovermode='x unified')
    fig_prev.update_traces(line=dict(width=3))
    st.plotly_chart(fig_prev, use_container_width=True)

with col2:
    # Session duration distribution
    fig_session = px.histogram(
        df_filtered,
        x='Session Duration',
        title="Session Duration Distribution",
        nbins=15,
        color_discrete_sequence=['#636efa'],
        marginal='box'
    )
    st.plotly_chart(fig_session, use_container_width=True)

# ---- HEATMAP & SCORECARD ----
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Correlation heatmap
    corr_cols = ['Page Views', 'Session Duration', 'Bounce Rate', 'Time on Page', 'Previous Visits', 'Conversion Rate']
    corr = df_filtered[corr_cols].corr()
    fig_heatmap = px.imshow(
        corr,
        text_auto='.2f',
        title="Feature Correlations",
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        height=400,
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    # Scorecard - Simple version with emojis
    st.subheader("🏆 Traffic Source Scorecard")
    scorecard = get_traffic_performance(df_filtered).reset_index()

    # Format the dataframe for display
    display_df = scorecard.copy()
    display_df['Conversion Rate'] = display_df['Conversion Rate'].apply(lambda x: f"{x:.1%}")
    display_df['Bounce Rate'] = display_df['Bounce Rate'].apply(lambda x: f"{x:.1%}")
    display_df['Session Duration'] = display_df['Session Duration'].apply(lambda x: f"{x:.1f}s")

    # Add emoji indicators for scores
    def add_score_emoji(val):
        try:
            score_val = float(val)
            if score_val > 0.7:
                return f"🟢 {score_val:.2f}"
            elif score_val > 0.4:
                return f"🟡 {score_val:.2f}"
            else:
                return f"🔴 {score_val:.2f}"
        except:
            return val

    display_df['Score'] = display_df['Overall_Score'].apply(add_score_emoji)
    display_df = display_df.drop('Overall_Score', axis=1)

    st.dataframe(
        display_df,
        column_config={
            "Traffic Source": st.column_config.TextColumn("Source"),
            "Conversion Rate": st.column_config.TextColumn("Conversion"),
            "Bounce Rate": st.column_config.TextColumn("Bounce"),
            "Session Duration": st.column_config.TextColumn("Session"),
            "Score": st.column_config.TextColumn("Score")
        },
        use_container_width=True,
        hide_index=True,
        height=250
    )

# ---- FOOTER ----
st.markdown("---")
st.caption("💡 Tip: Click on any chart legend to filter • Hover for detailed metrics • Use sidebar filters to explore")