"""
Graph generation library for heterokaryon analysis.

This module provides highly configurable plotting functions for data visualization.
Uses a registry system to automatically discover available plot types.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, Union, List, Dict, Callable, Any
import inspect

# Registry to store plot type functions and their metadata
_PLOT_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_plot_type(name: str, display_name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator to register a plot type function.
    
    Args:
        name: Internal name of the plot type
        display_name: Display name (defaults to name if not provided)
        description: Description of the plot type
    
    Example:
        @register_plot_type("boxplot", "Box Plot", "Create box plots with extensive customization")
        def boxplot(...):
            ...
    """
    def decorator(func: Callable):
        _PLOT_REGISTRY[name] = {
            'function': func,
            'display_name': display_name or name,
            'description': description or func.__doc__ or "",
            'name': name
        }
        return func
    return decorator


def get_all_plot_types() -> Dict[str, Dict[str, Any]]:
    """Get all registered plot types."""
    return _PLOT_REGISTRY.copy()


def get_plot_function(plot_type: str) -> Optional[Callable]:
    """Get the function for a specific plot type."""
    if plot_type in _PLOT_REGISTRY:
        return _PLOT_REGISTRY[plot_type]['function']
    return None


def get_plot_signature(plot_type: str) -> Dict[str, Any]:
    """
    Get the signature and parameter information for a plot type.
    Returns a dict with parameter names and their default values.
    """
    if plot_type not in _PLOT_REGISTRY:
        return {}
    
    func = _PLOT_REGISTRY[plot_type]['function']
    sig = inspect.signature(func)
    
    params = {}
    for param_name, param in sig.parameters.items():
        if param_name in ['data', 'self']:  # Skip data parameter and self
            continue
        params[param_name] = {
            'default': param.default if param.default != inspect.Parameter.empty else None,
            'annotation': param.annotation if param.annotation != inspect.Parameter.empty else None,
            'kind': param.kind
        }
    
    return params


@register_plot_type("boxplot", "Box Plot", "Create box plots with extensive customization options")
def boxplot(
    data: Union[pd.DataFrame, pd.Series, List],
    x: Optional[str] = None,
    y: Optional[str] = None,
    color: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    boxcolor: Union[str, List[str]] = '#1f77b4',
    boxmean: Optional[str] = None,  # 'sd', 'True', or None
    boxpoints: Optional[str] = 'outliers',  # 'all', 'outliers', 'suspectedoutliers', False
    pointpos: float = -1.8,
    jitter: float = 0.0,
    whiskerwidth: float = 0.5,
    boxwidth: Optional[float] = None,
    linethickness: float = 1.0,
    fillcolor: Optional[Union[str, List[str]]] = None,
    linecolor: Optional[Union[str, List[str]]] = None,
    marker_color: Optional[Union[str, List[str]]] = None,
    marker_size: float = 5.0,
    marker_symbol: str = 'circle',
    marker_opacity: float = 0.8,
    showlegend: bool = True,
    legend_title: Optional[str] = None,
    orientation: str = 'v',  # 'v' or 'h'
    width: Optional[int] = None,
    height: Optional[int] = None,
    template: str = 'plotly_white',
    showgrid: bool = True,
    gridcolor: str = 'rgba(128, 128, 128, 0.2)',
    gridwidth: float = 1.0,
    zeroline: bool = False,
    zerolinecolor: str = 'rgba(128, 128, 128, 0.5)',
    zerolinewidth: float = 1.0,
    hovermode: str = 'closest',
    hoverlabel_bgcolor: str = 'rgba(255, 255, 255, 0.9)',
    hoverlabel_bordercolor: str = 'rgba(0, 0, 0, 0.1)',
    hoverlabel_font_size: int = 12,
    margin: Optional[Dict[str, int]] = None,
    **kwargs
) -> go.Figure:
    """
    Create a highly configurable boxplot.
    
    Parameters
    ----------
    data : pd.DataFrame, pd.Series, or List
        Data to plot. If DataFrame, use x and y to specify columns.
        If Series or List, will be plotted directly.
    x : str, optional
        Column name for x-axis (categorical grouping).
    y : str, optional
        Column name for y-axis (values to plot).
    color : str, optional
        Column name to use for color grouping.
    title : str, optional
        Plot title.
    xlabel : str, optional
        X-axis label.
    ylabel : str, optional
        Y-axis label.
    boxcolor : str or List[str], default '#1f77b4'
        Color(s) for the box fill. Can be a single color or list for multiple groups.
    boxmean : str or None, default None
        Show mean line: 'sd' (mean ± SD), True (mean only), or None.
    boxpoints : str or False, default 'outliers'
        Which points to show: 'all', 'outliers', 'suspectedoutliers', or False.
    pointpos : float, default -1.8
        Position of points relative to box.
    jitter : float, default 0.0
        Amount of jitter for points (0.0 to 1.0).
    whiskerwidth : float, default 0.5
        Width of whiskers relative to box width.
    boxwidth : float, optional
        Width of boxes. If None, auto-calculated.
    linethickness : float, default 1.0
        Thickness of box and whisker lines.
    fillcolor : str or List[str], optional
        Fill color for boxes. If None, uses boxcolor.
    linecolor : str or List[str], optional
        Color for box and whisker lines. If None, uses boxcolor.
    marker_color : str or List[str], optional
        Color for points. If None, uses boxcolor.
    marker_size : float, default 5.0
        Size of points.
    marker_symbol : str, default 'circle'
        Symbol for points (e.g., 'circle', 'square', 'diamond', 'x').
    marker_opacity : float, default 0.8
        Opacity of points (0.0 to 1.0).
    showlegend : bool, default True
        Whether to show legend.
    legend_title : str, optional
        Title for legend.
    orientation : str, default 'v'
        Orientation: 'v' (vertical) or 'h' (horizontal).
    width : int, optional
        Plot width in pixels.
    height : int, optional
        Plot height in pixels.
    template : str, default 'plotly_white'
        Plotly template name.
    showgrid : bool, default True
        Whether to show grid lines.
    gridcolor : str, default 'rgba(128, 128, 128, 0.2)'
        Color of grid lines.
    gridwidth : float, default 1.0
        Width of grid lines.
    zeroline : bool, default False
        Whether to show zero line.
    zerolinecolor : str, default 'rgba(128, 128, 128, 0.5)'
        Color of zero line.
    zerolinewidth : float, default 1.0
        Width of zero line.
    hovermode : str, default 'closest'
        Hover mode: 'x', 'y', 'closest', 'x unified', 'y unified', False.
    hoverlabel_bgcolor : str, default 'rgba(255, 255, 255, 0.9)'
        Background color of hover label.
    hoverlabel_bordercolor : str, default 'rgba(0, 0, 128, 0.1)'
        Border color of hover label.
    hoverlabel_font_size : int, default 12
        Font size of hover label.
    margin : dict, optional
        Plot margins. Dict with keys: l, r, t, b (left, right, top, bottom).
    **kwargs
        Additional arguments passed to plotly box trace.
    
    Returns
    -------
    go.Figure
        Plotly figure object.
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]})
    >>> fig = boxplot(df, x='group', y='value', boxcolor='red', linethickness=2)
    >>> fig.show()
    """
    # Handle different input types
    if isinstance(data, pd.Series):
        data = data.to_frame()
        if y is None:
            y = data.columns[0]
    
    if isinstance(data, list):
        data = pd.DataFrame({'value': data})
        if y is None:
            y = 'value'
    
    # Use plotly express for easier handling of grouped data
    if x is not None and y is not None:
        # DataFrame with x and y specified
        if color is not None:
            fig = px.box(
                data,
                x=x,
                y=y,
                color=color,
                title=title,
                orientation=orientation,
                width=width,
                height=height,
                template=template,
                **kwargs
            )
        else:
            fig = px.box(
                data,
                x=x,
                y=y,
                title=title,
                orientation=orientation,
                width=width,
                height=height,
                template=template,
                **kwargs
            )
    elif y is not None:
        # Only y specified
        fig = px.box(
            data,
            y=y,
            color=color,
            title=title,
            orientation=orientation,
            width=width,
            height=height,
            template=template,
            **kwargs
        )
    else:
        # Single column or list
        if len(data.columns) == 1:
            col = data.columns[0]
            fig = px.box(
                data,
                y=col,
                title=title,
                orientation=orientation,
                width=width,
                height=height,
                template=template,
                **kwargs
            )
        else:
            raise ValueError("Must specify 'y' parameter when data has multiple columns")
    
    # Customize all traces
    for i, trace in enumerate(fig.data):
        # Handle color lists
        if isinstance(boxcolor, list) and i < len(boxcolor):
            trace_color = boxcolor[i]
        else:
            trace_color = boxcolor if isinstance(boxcolor, str) else boxcolor[0] if isinstance(boxcolor, list) else '#1f77b4'
        
        # Set box properties
        trace.boxmean = boxmean
        trace.boxpoints = boxpoints
        trace.pointpos = pointpos
        trace.jitter = jitter
        trace.whiskerwidth = whiskerwidth
        if boxwidth is not None:
            trace.boxwidth = boxwidth
        
        # Set line properties
        trace.line.width = linethickness
        if linecolor is not None:
            if isinstance(linecolor, list) and i < len(linecolor):
                trace.line.color = linecolor[i]
            else:
                trace.line.color = linecolor if isinstance(linecolor, str) else linecolor[0]
        else:
            trace.line.color = trace_color
        
        # Set fill color
        if fillcolor is not None:
            if isinstance(fillcolor, list) and i < len(fillcolor):
                trace.fillcolor = fillcolor[i]
            else:
                trace.fillcolor = fillcolor if isinstance(fillcolor, str) else fillcolor[0]
        else:
            trace.fillcolor = trace_color
        
        # Set marker properties
        if boxpoints and boxpoints != False:
            if marker_color is not None:
                if isinstance(marker_color, list) and i < len(marker_color):
                    trace.marker.color = marker_color[i]
                else:
                    trace.marker.color = marker_color if isinstance(marker_color, str) else marker_color[0]
            else:
                trace.marker.color = trace_color
            
            trace.marker.size = marker_size
            trace.marker.symbol = marker_symbol
            trace.marker.opacity = marker_opacity
    
    # Update layout
    layout_updates = {
        'showlegend': showlegend,
        'hovermode': hovermode,
        'template': template,
    }
    
    if title is not None:
        layout_updates['title'] = {'text': title, 'x': 0.5, 'xanchor': 'center'}
    
    if xlabel is not None:
        layout_updates['xaxis_title'] = xlabel
    elif x is not None:
        layout_updates['xaxis_title'] = x
    
    if ylabel is not None:
        layout_updates['yaxis_title'] = ylabel
    elif y is not None:
        layout_updates['yaxis_title'] = y
    
    if legend_title is not None:
        layout_updates['legend'] = {'title': {'text': legend_title}}
    
    if width is not None:
        layout_updates['width'] = width
    if height is not None:
        layout_updates['height'] = height
    
    if margin is not None:
        layout_updates['margin'] = margin
    
    # Grid and zero line settings
    if orientation == 'v':
        layout_updates['xaxis'] = {
            'showgrid': showgrid,
            'gridcolor': gridcolor,
            'gridwidth': gridwidth,
            'zeroline': zeroline,
            'zerolinecolor': zerolinecolor,
            'zerolinewidth': zerolinewidth,
        }
        layout_updates['yaxis'] = {
            'showgrid': showgrid,
            'gridcolor': gridcolor,
            'gridwidth': gridwidth,
            'zeroline': zeroline,
            'zerolinecolor': zerolinecolor,
            'zerolinewidth': zerolinewidth,
        }
    else:  # horizontal
        layout_updates['xaxis'] = {
            'showgrid': showgrid,
            'gridcolor': gridcolor,
            'gridwidth': gridwidth,
            'zeroline': zeroline,
            'zerolinecolor': zerolinecolor,
            'zerolinewidth': zerolinewidth,
        }
        layout_updates['yaxis'] = {
            'showgrid': showgrid,
            'gridcolor': gridcolor,
            'gridwidth': gridwidth,
            'zeroline': zeroline,
            'zerolinecolor': zerolinecolor,
            'zerolinewidth': zerolinewidth,
        }
    
    # Hover label settings
    layout_updates['hoverlabel'] = {
        'bgcolor': hoverlabel_bgcolor,
        'bordercolor': hoverlabel_bordercolor,
        'font_size': hoverlabel_font_size,
    }
    
    fig.update_layout(**layout_updates)
    
    return fig


def create_streamlit_config_widgets(plot_type: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Create Streamlit widgets for configuring a plot type.
    Returns a dictionary of parameter values from the widgets.
    
    This is a helper function that creates appropriate widgets based on parameter types.
    For more complex configurations, you can create custom widget functions.
    """
    import streamlit as st
    
    if plot_type not in _PLOT_REGISTRY:
        return {}
    
    params = get_plot_signature(plot_type)
    config = {}
    
    # Get available columns for x, y, color selection
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    all_cols = data.columns.tolist()
    
    # Common parameters that need special handling
    if 'x' in params:
        x_val = st.selectbox("X-axis (grouping)", [None] + all_cols, index=0)
        if x_val is not None:
            config['x'] = x_val
    if 'y' in params:
        y_val = st.selectbox("Y-axis (values)", [None] + numeric_cols, index=1 if len(numeric_cols) > 0 else 0)
        if y_val is not None:
            config['y'] = y_val
    if 'color' in params:
        color_val = st.selectbox("Color grouping", [None] + all_cols, index=0)
        if color_val is not None:
            config['color'] = color_val
    
    # Title and labels
    if 'title' in params:
        title_val = st.text_input("Title", value=params['title']['default'] or "")
        if title_val:
            config['title'] = title_val
    if 'xlabel' in params:
        xlabel_val = st.text_input("X-axis label", value=params['xlabel']['default'] or "")
        if xlabel_val:
            config['xlabel'] = xlabel_val
    if 'ylabel' in params:
        ylabel_val = st.text_input("Y-axis label", value=params['ylabel']['default'] or "")
        if ylabel_val:
            config['ylabel'] = ylabel_val
    
    # Visual customization
    if 'boxcolor' in params:
        config['boxcolor'] = st.color_picker("Box color", value=params['boxcolor']['default'] or '#1f77b4')
    if 'linethickness' in params:
        config['linethickness'] = st.slider("Line thickness", 0.5, 5.0, value=params['linethickness']['default'] or 1.0, step=0.1)
    if 'boxpoints' in params:
        boxpoints_options = ['outliers', 'all', 'suspectedoutliers', False]
        default_idx = boxpoints_options.index(params['boxpoints']['default']) if params['boxpoints']['default'] in boxpoints_options else 0
        config['boxpoints'] = st.selectbox("Show points", boxpoints_options, index=default_idx)
    if 'marker_size' in params:
        config['marker_size'] = st.slider("Marker size", 1.0, 20.0, value=params['marker_size']['default'] or 5.0, step=0.5)
    
    # Layout
    if 'width' in params:
        config['width'] = st.number_input("Width (pixels)", min_value=300, max_value=2000, value=params['width']['default'] or 800, step=50)
    if 'height' in params:
        config['height'] = st.number_input("Height (pixels)", min_value=300, max_value=2000, value=params['height']['default'] or 500, step=50)
    if 'orientation' in params:
        config['orientation'] = st.selectbox("Orientation", ['v', 'h'], index=0 if (params['orientation']['default'] or 'v') == 'v' else 1)
    
    # Handle remaining parameters with generic widgets
    handled_params = {'x', 'y', 'color', 'title', 'xlabel', 'ylabel', 'boxcolor', 'linethickness', 
                     'boxpoints', 'marker_size', 'width', 'height', 'orientation'}
    
    for param_name, param_info in params.items():
        if param_name in handled_params:
            continue
        
        default_val = param_info['default']
        param_type = param_info['annotation']
        
        # Skip if no default and not a common parameter
        if default_val is None and param_name not in ['showlegend', 'showgrid']:
            continue
        
        # Create appropriate widget based on type
        if isinstance(default_val, bool):
            config[param_name] = st.checkbox(param_name.replace('_', ' ').title(), value=default_val)
        elif isinstance(default_val, (int, float)) and default_val is not None:
            if 'size' in param_name.lower() or 'width' in param_name.lower() or 'thickness' in param_name.lower():
                config[param_name] = st.slider(param_name.replace('_', ' ').title(), 0.0, 10.0, value=float(default_val), step=0.1)
            else:
                config[param_name] = st.number_input(param_name.replace('_', ' ').title(), value=default_val)
        elif isinstance(default_val, str):
            config[param_name] = st.text_input(param_name.replace('_', ' ').title(), value=default_val)
    
    # Remove None values
    config = {k: v for k, v in config.items() if v is not None}
    
    return config

