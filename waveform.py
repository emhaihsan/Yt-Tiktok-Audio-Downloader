import plotly.graph_objects as go
from audio_utils import format_time

def create_waveform_plot(y, sr, duration, cut_points=[]):
    """Create interactive waveform plot with cut points"""
    import numpy as np

    times = np.linspace(0, duration, len(y))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times,
        y=y,
        mode='lines',
        name='Waveform',
        line=dict(color='#1f77b4', width=1),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.3)',
    ))

    for cut_point in sorted(cut_points):
        fig.add_vline(
            x=cut_point,
            line_dash="dash",
            line_color="red",
            annotation_text=f"CUT {format_time(cut_point)}",
            annotation_position="top"
        )

    fig.update_layout(
        title="🎵 Audio Waveform",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        hovermode='x unified',
        height=400,
        template="plotly_dark",
        xaxis=dict(rangeslider=dict(visible=False)),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig
