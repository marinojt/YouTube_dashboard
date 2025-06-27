import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(layout="wide")

# --- Data Loading and Preparation (Same as Dash) ---
try:
    df = pd.read_csv('youtube_metrics.csv')
except FileNotFoundError:
    st.error("Error: 'youtube_metrics.csv' not found. Please make sure the file is in the same directory as the script.")
    st.stop()

METRICS_CONFIG = {
    'reach': {
        'name': 'REACH', 'metric_col': 'Subs/Age', 'z_score_col': 'Z Subs/Age',
        'kpi_text_metric': 'Subscribers/per Month',
        'kpi_bold_text': 'subscribers',
        'kpi_text_z': '{direction} average Subscribers/per channel age',
        'pie_chart_col': 'Total Views', 'pie_chart_title': 'Total Views',
        'pie_hover_unit': 'views',
        'hover_unit_text': 'subscribers per month',
        'ranking_title': 'Subscribers per Month',
        'color_primary': '#3b8ac4', 'color_secondary': '#a8d8f0', 'color_bg': '#e0f2f7'
    },
    'efficiency': {
        'name': 'EFFICIENCY', 'metric_col': 'subs/min', 'z_score_col': 'Z Subs/Min',
        'kpi_text_metric': 'Subscribers/per Minute',
        'kpi_bold_text': 'subscribers',
        'kpi_text_z': '{direction} average subscribers/per minute of long-form content',
        'pie_chart_col': 'Total Minutes',
        'pie_chart_title': 'Total Minutes',
        'pie_hover_unit': 'minutes',
        'hover_unit_text': 'subscribers per minute',
        'ranking_title': 'Subscribers per Minute',
        'color_primary': '#f57c00', 'color_secondary': '#ffcc80', 'color_bg': '#fff3e0'
    },
    'engagement': {
        'name': 'ENGAGEMENT', 'metric_col': 'com/min', 'z_score_col': 'Z com/min',
        'kpi_text_metric': 'Comments/per Minute',
        'kpi_bold_text': 'comments',
        'kpi_text_z': '{direction} average comments/per minute',
        'pie_chart_col': 'Likes', 'pie_chart_title': 'Total Likes',
        'pie_hover_unit': 'likes',
        'hover_unit_text': 'comments per minute',
        'ranking_title': 'Comments per Minute',
        'color_primary': '#8e24aa', 'color_secondary': '#e1bee7', 'color_bg': '#f3e5f5'
    },
    'activity': {
        'name': 'ACTIVITY', 'metric_col': 'Videos/Age', 'z_score_col': 'Z Vid/Age',
        'kpi_text_metric': 'Videos/per Month',
        'kpi_bold_text': 'videos',
        'kpi_text_z': '{direction} average long-form videos/per age of channel',
        'pie_chart_col': 'Total Videos',
        'pie_chart_title': 'Total Videos',
        'pie_hover_unit': 'videos',
        'hover_unit_text': 'videos per month',
        'ranking_title': 'Videos per Month',
        'color_primary': '#e53935', 'color_secondary': '#ffcdd2', 'color_bg': '#ffebee'
    }
}

# --- Pre-computation (Same as Dash) ---
mean_com_min = df['com/min'].mean()
std_com_min = df['com/min'].std()
df['Z com/min'] = (df['com/min'] - mean_com_min) / std_com_min

df['engagement_ratio'] = (df['Likes'] + df['Comments']) / df['Total Views']
mean_engagement = df['engagement_ratio'].mean()
std_engagement = df['engagement_ratio'].std()
df['Z engagement_ratio'] = (df['engagement_ratio'] - mean_engagement) / std_engagement

for pillar in METRICS_CONFIG.values():
    metric_col = pillar['metric_col']
    mean_val = df[metric_col].mean()
    df[f'pct_diff_{metric_col}'] = ((df[metric_col] - mean_val) / mean_val) * 100 if mean_val != 0 else 0

df['Subscriber_k'] = (df['Subscriber Count'] / 1000).round(1).astype(str) + 'k'

# --- Font and CSS Styling ---
MODERN_FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
st.markdown(f"""
<style>
    /* Global font setting */
    html, body, [class*="st-"], .st-emotion-cache-12fmjuu, .st-emotion-cache-1jicfl2 {{
        font-family: {MODERN_FONT_STACK};
    }}
    /* Main container styling - REDUCED TOP PADDING */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }}
    /* --- NEW: Dropdown/Selectbox Styling --- */
    /* Container of the selectbox */
    div[data-testid="stSelectbox"] > div {{
        background-color: #e8f5e8; /* Light green background */
        border: 1px solid #c8e6c9;
        border-radius: 0.25rem;
    }}
    /* Text of the selected item */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div {{
        color: #2e7d32 !important; /* Dark green text */
        font-weight: bold;
    }}
    /* Dropdown arrow */
    div[data-testid="stSelectbox"] svg {{
        color: #2e7d32;
    }}
    
    /* Remove some padding from columns to make cards tighter */
    div[data-testid="column"] {{
        padding-left: 5px;
        padding-right: 5px;
        padding-top: 0px !important;
        margin-top: 0px !important;
    }}
    
    /* REDUCE SPACING BETWEEN ELEMENTS */
    .element-container {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Style for the pillar container */
    .pillar-container {{
        border: 1px solid #eee;
        border-radius: 5px;
        background-color: white;
        padding: 10px;
        display: flex;
        flex-direction: column;
        margin-top: 0px !important;
    }}
    hr {{
        margin: 10px 0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'metrics'

# --- Header Section ---
header_cols = st.columns([3, 1])
with header_cols[0]:
    st.markdown("#### YouTube Top 10 Competitor Analysis | KDP PUBLISHING")
with header_cols[1]:
    sorted_channels = sorted(df['Channel Name'].unique())
    default_index = sorted_channels.index('Ken Fornari') if 'Ken Fornari' in sorted_channels else 0
    selected_channel = st.selectbox(
        "Select Channel:",
        options=sorted_channels,
        index=default_index,
        format_func=lambda name: name.upper(),
        label_visibility="collapsed"
    )

# --- Toggle Button ---
button_cols = st.columns([1, 1, 1])
with button_cols[1]:
    if st.button("TOGGLE METRICS / Z-SCORES", use_container_width=True):
        st.session_state.view_mode = 'z-scores' if st.session_state.view_mode == 'metrics' else 'metrics'
        st.rerun()

# --- Dashboard Layout ---
view_mode = st.session_state.view_mode
col1, col2, col3, col4 = st.columns(4, gap="small")
cols = [col1, col2, col3, col4]

for (key, config), col in zip(METRICS_CONFIG.items(), cols):
    with col:
        st.markdown(f'<div class="pillar-container">', unsafe_allow_html=True)
        
        # --- Pillar Header ---
        st.markdown(f"""
        <div style="background-color: {config['color_bg']}; color: {config['color_primary']}; padding: 8px;
                     text-align: center; font-weight: bold; font-size: 18px;
                     border-top-left-radius: 5px; border-top-right-radius: 5px;">
            {config['name']}
        </div>
        """, unsafe_allow_html=True)

        is_z_score_mode = (view_mode == 'z-scores')
        ranking_col = config['z_score_col'] if is_z_score_mode else config['metric_col']

        df_sorted = df.sort_values(by=ranking_col, ascending=False).reset_index()
        df_sorted['rank'] = df_sorted.index + 1
        
        main_channel_data = df_sorted[df_sorted['Channel Name'] == selected_channel].iloc[0]

        # --- KPI Block ---
        if is_z_score_mode:
            pct_diff_col = f"pct_diff_{config['metric_col']}"
            kpi_value = main_channel_data[pct_diff_col]
            direction = "above" if kpi_value >= 0 else "below"
            kpi_desc_full_text = config['kpi_text_z'].format(direction=direction)
            kpi_main_val = f"{abs(kpi_value):.1f}%"
        else:
            kpi_value = main_channel_data[config['metric_col']]
            kpi_desc_full_text = config['kpi_text_metric']
            kpi_main_val = f"{kpi_value:.1f}" if key != 'engagement' else f"{kpi_value:.2f}"

        line1_full, line2_content = kpi_desc_full_text.split('/')
        if not is_z_score_mode:
            if key == 'reach':
                line1_full = line1_full.replace('Subscribers', '<strong>Subscribers</strong>')
            elif key == 'efficiency':
                line1_full = line1_full.replace('Subscribers', '<strong>Subscribers</strong>')
            elif key == 'engagement':
                line1_full = line1_full.replace('Comments', '<strong>Comments</strong>')
            elif key == 'activity':
                line1_full = line1_full.replace('Videos', '<strong>Videos</strong>')
                
        # Set text color for each pillar
        if key == 'reach':
            p1_color = '#3b8ac4'
        elif key == 'efficiency':
            p1_color = '#f57c00'
        elif key == 'engagement':
            p1_color = '#8e24aa'
        elif key == 'activity':
            p1_color = '#e53935'
        else:
            p1_color = 'black'
                
        kpi_html = f"""
        <div style="height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <div style="display: flex; align-items: center; justify-content: center; padding: 5px 0;">
                <h1 style="font-size: 44px; color: {config['color_primary']} !important; margin: 0 10px 0 0; line-height: 1;">{kpi_main_val}</h1>
                <div style="font-size: 12px; text-align: left; line-height: 1.3;">
                    <p style="margin: 0; padding: 0; color: {p1_color} !important;">{line1_full}</p>
                    <p style="margin: 0; padding: 0; color: black !important;">{line2_content}</p>
                </div>
            </div>
            <p style="font-weight: normal; margin-top: 12px; font-size: 16px; color: {config['color_primary']} !important;">
                #{main_channel_data['rank']}/{len(df)}
            </p>
        </div>
        """


        st.markdown(kpi_html, unsafe_allow_html=True)
        st.divider()

        # --- Pie Chart Block ---
        pie_data = df.copy()
        pie_data['is_main'] = pie_data['Channel Name'] == selected_channel
        colors = [config['color_primary'] if is_main else config['color_secondary'] for is_main in pie_data['is_main']]
        
        # --- Generate subtitle text and combined title for the pie chart ---
        total_val = df[config['pie_chart_col']].sum()
        subtitle_text = ""
        if key == 'reach':
            subtitle_text = f"{total_val / 1e6:.1f} million views"
        elif key == 'efficiency':
            subtitle_text = f"{total_val:,.0f} minutes"
        elif key == 'engagement':
            subtitle_text = f"{total_val:,.0f} likes"
        elif key == 'activity':
            subtitle_text = f"{total_val:,.0f} long-form videos"
        
        full_title_text = (
            f"<b>{config['pie_chart_title']}</b><br>"
            f"<span style='font-size: 12px; color: #666; font-weight: normal;'>{subtitle_text}</span>"
        )
        
        pie_fig = go.Figure(data=[go.Pie(
            labels=pie_data['Channel Name'], values=pie_data[config['pie_chart_col']],
            marker_colors=colors,
            hovertemplate=f"<b>%{{label}}</b><br>%{{percent}}<br>%{{value:,}} {config['pie_hover_unit']}<extra></extra>",
            textinfo='none', sort=False
        )])
        pie_fig.update_traces(
            pull=[0.05 if is_main else 0 for is_main in pie_data['is_main']],
            marker={'line': {'color': 'white', 'width': 2}}
        )
        pie_fig.update_layout(
            title_text=full_title_text,
            title_x=0.5,
            title_xanchor='center',
            title_font=dict(size=14, color=config['color_primary'], family=MODERN_FONT_STACK),
            showlegend=False, 
            margin=dict(t=70, b=10, l=10, r=10), # Adjusted top margin for subtitle
            height=250,
            paper_bgcolor='white', 
            plot_bgcolor='white', 
            font=dict(family=MODERN_FONT_STACK)
        )
        st.plotly_chart(pie_fig, use_container_width=True, config={'displayModeBar': False})
        
        st.divider()

        # --- Rankings Block ---
        st.markdown(f"<h4 style='text-align: left; margin: 0 0 15px 0; font-size: 16px;'>{config['ranking_title']}</h4>", unsafe_allow_html=True)
        
        ranking_chart = go.Figure(go.Bar(
            x=df_sorted[ranking_col], y=df_sorted['Channel Name'], orientation='h',
            marker_color=[config['color_primary'] if row['Channel Name'] == selected_channel else config['color_secondary'] for _, row in df_sorted.iterrows()],
            customdata=df_sorted[['Subscriber_k', 'Subscriber Count']],
            hovertemplate=f'<b>%{{y}}</b><br>%{{x:,.2f}} {config["hover_unit_text"]}<br>%{{customdata[1]:,.0f}} subscribers<extra></extra>'
        ))

        annotations = []
        for i, row in df_sorted.iterrows():
            is_main = (row['Channel Name'] == selected_channel)
            label_text = row['Channel Name']
            annotations.append(dict(
                x=0, y=row['Channel Name'], text=f"  {label_text}", xref="paper", yref="y",
                showarrow=False, xanchor='left', align='left',
                font=dict(
                    size=12,
                    color='black',
                    family=MODERN_FONT_STACK
                ),
                font_weight='bold' if is_main else 'normal'
            ))

        ranking_chart.update_layout(
            yaxis={'visible': False}, xaxis_title=None, xaxis={'visible': False},
            plot_bgcolor='white', margin=dict(t=5, b=20, l=0, r=0), height=280,
            annotations=annotations, barmode='stack'
        )
        ranking_chart.update_yaxes(autorange="reversed")
        ranking_chart.update_xaxes(showticklabels=False)

        st.plotly_chart(ranking_chart, use_container_width=True, config={'displayModeBar': False})

        st.markdown('</div>', unsafe_allow_html=True)
