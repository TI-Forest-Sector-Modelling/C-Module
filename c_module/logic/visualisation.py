import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import webbrowser
from threading import Timer
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

from c_module.parameters.defines import VarNames
from c_module.data_management.data_manager import DataManager

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class Carbon_DashboardPlotter:

    def __init__(self, data):
        self.data = data
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.start = self.data[VarNames.year_name.value].min()
        self.end = self.data[VarNames.year_name.value].max()
        self.pool_colors = self.get_colors()
        self.logo = PACKAGEDIR / 'C-Module_Logo_transparent_v1.png'
        self.create_layout()
        self.create_callbacks()

    def get_colors(self):
        carbon_pools = self.data[VarNames.output_variable.value].unique()
        color_palette = px.colors.qualitative.Bold  # or "Bold", "Plotly", "Set1", "Set2" "Dark2" etc.
        color_map = {var: color_palette[i % len(color_palette)] for i, var in enumerate(carbon_pools)}

        return color_map

    def create_layout(self):
        dropdown_style = {
            'height': '30px',
            'marginRight': '10px',
            'flex': '1 1 200px',
            'minWidth': '200px'
        }
        year_marks = {year: str(year) for year in range(self.start, self.end + 1) if year % 5 == 0}

        self.app.layout = dbc.Container(fluid=True, style={'backgroundColor': 'white'}, children=[

            # 1. filter options (bottom line)
            dbc.Row([
                dbc.Col([
                    dbc.Card(className="border-0 shadow-sm", children=[
                        dbc.CardBody(style={'padding': '15px'}, children=[
                            html.Div(style={
                                'display': 'flex',
                                'flexWrap': 'wrap',
                                'gap': '10px',
                                'alignItems': 'center'
                            }, children=[
                                # Logo links
                                html.Img(
                                    src=self.app.get_asset_url('C-Module_Logo_transparent_v1.png'),
                                    style={'height': '50px', 'marginRight': '20px'}
                                ),

                                # Filter-Dropdowns
                                dcc.Dropdown(id='continent-dropdown',
                                             options=[{'label': i, 'value': i}
                                                      for i in sorted(
                                                     self.data[VarNames.continent.value].dropna().unique())],
                                             multi=True,
                                             placeholder='Select Continent...',
                                             style=dropdown_style),
                                dcc.Dropdown(id='region-dropdown',
                                             options=[{'label': i, 'value': i}
                                                      for i in sorted(
                                                     self.data[VarNames.carbon_region.value].dropna().unique())],
                                             multi=True,
                                             placeholder='Select Region...',
                                             style=dropdown_style),
                                dcc.Dropdown(id='country-dropdown',
                                             options=[{'label': i, 'value': i}
                                                      for i in sorted(
                                                     self.data[VarNames.ISO3.value].dropna().unique())],
                                             multi=True,
                                             placeholder='Select Country...',
                                             style=dropdown_style),
                                dcc.Dropdown(id='variable-dropdown',
                                             options=[{'label': i, 'value': i}
                                                      for i in sorted(
                                                     self.data[VarNames.output_variable.value].dropna().unique())],
                                             placeholder='Select Carbon Pool...',
                                             multi=True,
                                             style=dropdown_style),
                                dcc.Dropdown(id='scenario-dropdown',
                                             options=[{'label': i, 'value': i}
                                                      for i in sorted(
                                                         self.data[VarNames.scenario.value].dropna().unique())],
                                             placeholder='Select Scenario...',
                                             multi=True,
                                             style=dropdown_style),

                                # Download-Button
                                html.Button(
                                    "⬇️ CSV Export",
                                    id="btn_csv",
                                    className="ml-auto",
                                    style={
                                        'height': '30px',
                                        'marginLeft': 'auto',
                                        'padding': '0 15px',
                                        'borderRadius': '4px',
                                        'border': '1px solid #ddd'
                                    }
                                ),
                                dcc.Download(id="download-dataframe-csv")
                            ])
                        ])
                    ], style={'backgroundColor': '#f8f9fa'})
                ])
            ], className="mb-4"),

            # 1b. Timebar (RangeSlider)
            dbc.Row([
                dbc.Col([
                    dbc.Card(className="border-0 shadow-sm", children=[
                        dbc.CardBody(style={'padding': '15px'}, children=[
                            html.Label("Select Time Period:", style={'fontWeight': 'bold'}),
                            dcc.RangeSlider(
                                id='year-range-slider',
                                min=self.start,
                                max=self.end,
                                step=None,
                                value=[self.start, self.end],  # default full range
                                marks={year: str(year) for year in year_marks if year % 5 == 0},
                                allowCross=False,
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),

            # 2. Main content
            dbc.Row([
                # Left column (stacked area chart)
                dbc.Col(children=[
                    dbc.Card(className="h-100 shadow-sm", children=[
                        dbc.CardBody(style={'padding': '15px',
                                            'display': 'flex',
                                            'flexDirection': 'column',
                                            'height': '100%',
                                            },
                                     children=[
                                         html.Div([dcc.Dropdown(
                                             id='value-type-dropdown-1',
                                             options=[{'label': i, 'value': i} for i in ['absolute', 'shares']],
                                             placeholder="Select Value Type...",
                                             value='absolute',
                                             style=dropdown_style
                                         )], style={'marginBottom': '15px'}),
                                         html.Div([dcc.Dropdown(
                                             id='stock-type-dropdown-1',
                                             options=[],
                                             placeholder="Select Stock Type...",
                                             value=None,
                                             style=dropdown_style
                                         )], style={'marginBottom': '15px'}),
                                         dcc.Graph(
                                             id='carbon-stacked-area-chart',
                                             config={'toImageButtonOptions': {'format': 'png'},
                                                     'displayModeBar': True},
                                             style={'flex': '1',
                                                    'minHeight': '0'}
                                         )
                                     ])
                    ], style={'backgroundColor': 'white', 'padding': '15px'})
                ], width=6),

                dbc.Col(md=6, children=[
                    # Right column (world map)
                    dbc.Card(className="h-100 shadow-sm", children=[
                        dbc.CardBody(style={'padding': '15px',
                                            'display': 'flex',
                                            'flexDirection': 'column',
                                            'height': '100%',
                                            },
                                     children=[
                                         # html.H5("Figure filter", className="card-title"),
                                         html.Div([dcc.Dropdown(
                                             id='value-type-dropdown-2',
                                             options=[{'label': i, 'value': i} for i in ['absolute', 'shares']],
                                             placeholder="Select Value Type...",
                                             value='absolute',
                                             style=dropdown_style
                                         )], style={'marginBottom': '15px'}),
                                         html.Div([dcc.Dropdown(
                                             id='stock-type-dropdown-2',
                                             options=[],
                                             placeholder="Select Stock Type...",
                                             value=None,
                                             style=dropdown_style
                                         )], style={'marginBottom': '15px'}),
                                         dcc.Graph(
                                             id='carbon-world-map',
                                             config={'toImageButtonOptions': {'format': 'png'},
                                                     'displayModeBar': True},
                                             style={'flex': '1',
                                                    'minHeight': '0'
                                                    }
                                         )
                                     ])
                    ], style={'backgroundColor': 'white', 'padding': '15px'})
                ], width=6)
            ], style={'height': 'calc(100vh - 220px)'})
        ])

    def create_callbacks(self):
        @self.app.callback([
            Output('carbon-stacked-area-chart', 'figure'),
            Output('carbon-world-map', 'figure')],
            [
                Input('continent-dropdown', 'value'),
                Input('region-dropdown', 'value'),
                Input('country-dropdown', 'value'),
                Input('variable-dropdown', 'value'),
                Input('year-range-slider', 'value'),
                Input('scenario-dropdown', 'value'),
                Input('value-type-dropdown-1', 'value'),
                Input('stock-type-dropdown-1', 'value'),
                Input('value-type-dropdown-2', 'value'),
                Input('stock-type-dropdown-2', 'value')
            ]
        )
        def update_plots(continent, region, country, variable, year_range, scenario, value_type_1, stock_type_1,
                         value_type_2, stock_type_2):

            def normalize_selection(val):
                if isinstance(val, list) and len(val) == 0:
                    return None
                return val

            continent = normalize_selection(continent)
            region = normalize_selection(region)
            country = normalize_selection(country)
            variable = normalize_selection(variable)
            scenario = normalize_selection(scenario)

            return self.update_plot_carbon(continent=continent,
                                           region=region,
                                           country=country,
                                           variable=variable,
                                           scenario=scenario,
                                           year_range=year_range,
                                           value_type_1=value_type_1,
                                           stock_type_1=stock_type_1,
                                           value_type_2=value_type_2,
                                           stock_type_2=stock_type_2,
                                           pool_colors=self.pool_colors)

        @self.app.callback(
            Output("download-dataframe-csv", "data"),
            Input("btn_csv", "n_clicks"),
            [State('continent-dropdown', 'value'),
             State('region-dropdown', 'value'),
             State('country-dropdown', 'value'),
             State('variable-dropdown', 'value'),
             State('year-range-slider', 'value'),
             State('scenario-dropdown', 'value'),
             ],
            prevent_initial_call=True
        )
        def download_csv(n_clicks, continent, region, country, variable, year_range, scenario):
            if n_clicks is None:
                raise dash.exceptions.PreventUpdate

            def normalize_selection(val):
                if isinstance(val, list) and len(val) == 0:
                    return None
                return val

            continent = normalize_selection(continent)
            region = normalize_selection(region)
            country = normalize_selection(country)
            variable = normalize_selection(variable)
            scenario = normalize_selection(scenario)

            filtered_data = self.filter_data(
                continent=continent,
                region=region,
                country=country,
                variable=variable,
                year_range=year_range,
                scenario=scenario
            )

            return dcc.send_data_frame(filtered_data.to_csv, "filtered_carbon_data.csv", index=False)

        @self.app.callback(
            Output('region-dropdown', 'options'),
            Input('continent-dropdown', 'value')
        )
        def _opts_regions(selected_continents):
            df = self.data
            if selected_continents:
                df = df[df[VarNames.continent.value].isin(selected_continents)]
            regions = sorted(df[VarNames.carbon_region.value].dropna().unique())
            return [{'label': r, 'value': r} for r in regions]

        @self.app.callback(
            Output('country-dropdown', 'options'),
            [Input('continent-dropdown', 'value'),
             Input('region-dropdown', 'value')]
        )
        def _opts_countries(selected_continents, selected_regions):
            df = self.data
            if selected_continents:
                df = df[df[VarNames.continent.value].isin(selected_continents)]
            if selected_regions:
                df = df[df[VarNames.carbon_region.value].isin(selected_regions)]
            countries = sorted(df[VarNames.ISO3.value].dropna().unique())
            return [{'label': c, 'value': c} for c in countries]

        @self.app.callback(
            [Output('region-dropdown', 'value'),
             Output('country-dropdown', 'value')],
            [Input('continent-dropdown', 'value'),
             Input('region-dropdown', 'value')],
            [State('region-dropdown', 'value'),
             State('country-dropdown', 'value')]
        )
        def _sync_values(selected_continents, selected_regions, prev_regions, prev_countries):
            df = self.data

            if selected_continents:
                df_r = df[df[VarNames.continent.value].isin(selected_continents)]
            else:
                df_r = df
            allowed_regions = set(df_r[VarNames.carbon_region.value].dropna().unique())

            new_regions = [r for r in (prev_regions or []) if r in allowed_regions]

            if selected_regions is not None:
                new_regions = [r for r in
                               (selected_regions if isinstance(selected_regions, list) else [selected_regions])
                               if r in allowed_regions]

            df_c = df_r
            if new_regions:
                df_c = df_c[df_c[VarNames.carbon_region.value].isin(new_regions)]
            allowed_countries = set(df_c[VarNames.ISO3.value].dropna().unique())

            new_countries = [c for c in (prev_countries or []) if c in allowed_countries]

            if set(new_regions) != set(prev_regions or []):
                new_countries = []

            return (new_regions or None), (new_countries or None)

        @self.app.callback(
            Output("variable-dropdown", "value"),
            Input("variable-dropdown", "value")
        )
        def enforce_mutually_exclusive_variables(selected_vars):
            if not selected_vars:
                return []

            selected_vars = selected_vars.copy()

            if VarNames.carbon_total.value in selected_vars:
                return [VarNames.carbon_total.value]

            hwp_components = [VarNames.carbon_sawnwood.value, VarNames.carbon_wood_based_panels.value,
                              VarNames.carbon_paper_and_paperboard.value]
            if VarNames.carbon_hwp.value in selected_vars:
                selected_vars = [v for v in selected_vars if v not in hwp_components]

            return selected_vars


        @self.app.callback(
            Output('stock-type-dropdown-1', 'options'),
            Output('stock-type-dropdown-1', 'value'),
            Input('value-type-dropdown-1', 'value')
        )
        def update_stock_type_1(value_type):
            if value_type == 'absolute':
                options = [
                    {'label': 'carbon stock', 'value': 'carbon stock'},
                    {'label': 'carbon stock change', 'value': 'carbon stock change'}
                ]
                default_value = 'carbon stock'
            elif value_type == 'shares':
                options = [{'label': 'carbon stock', 'value': 'carbon stock'}]
                default_value = 'carbon stock'
            else:
                options = []
                default_value = None

            return options, default_value

        @self.app.callback(
            Output('stock-type-dropdown-2', 'options'),
            Output('stock-type-dropdown-2', 'value'),
            Input('value-type-dropdown-2', 'value')
        )
        def update_stock_type_2(value_type):
            if value_type == 'absolute':
                options = [
                    {'label': 'carbon stock', 'value': 'carbon stock'},
                    {'label': 'carbon stock change', 'value': 'carbon stock change'}
                ]
                default_value = 'carbon stock'
            elif value_type == 'shares':
                options = [{'label': 'carbon stock', 'value': 'carbon stock'}]
                default_value = 'carbon stock'
            else:
                options = []
                default_value = None

            return options, default_value

        @self.app.callback(
            Output('output', 'children'),
            Input('value-type-dropdown-1', 'value'),
            Input('stock-type-dropdown-1', 'value'),
            Input('value-type-dropdown-2', 'value'),
            Input('stock-type-dropdown-2', 'value')
        )
        def display_selection(v1, s1, v2, s2):
            return f"Pair1: {v1}/{s1} | Pair2: {v2}/{s2}"

    def filter_data(self, continent, region, country, variable, year_range, scenario):
        filtered_data = self.data.copy()
        if isinstance(continent, list):
            if not continent:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[filtered_data[VarNames.continent.value].isin(continent)]

        if isinstance(region, list):
            if not region:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[filtered_data[VarNames.carbon_region.value].isin(region)]

        if isinstance(country, list):
            if not country:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[filtered_data[VarNames.ISO3.value].isin(country)]

        if isinstance(variable, list):
            if not variable:
                filtered_data = filtered_data.iloc[0:0]
            elif "All" not in variable:
                filtered_data = filtered_data[filtered_data[VarNames.output_variable.value].isin(variable)]

        if isinstance(year_range, list):
            if not year_range:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[(filtered_data[VarNames.year_name.value] >= year_range[0]) &
                                              (filtered_data[VarNames.year_name.value] <= year_range[1])]

        if isinstance(scenario, list):
            if not scenario:
                filtered_data = filtered_data.iloc[0:0]
            elif "All" not in scenario:
                filtered_data = filtered_data[filtered_data[VarNames.scenario.value].isin(scenario)]

        filtered_data = filtered_data.reset_index(drop=True)
        return filtered_data

    def plot_stacked_area_chart(self, data, continent, region, country, variable, year_range, value_type, stock_type,
                                scenario, pool_colors):
        fig = go.Figure()

        df_all = data.copy()

        if year_range:
            df_all = df_all[
                (df_all[VarNames.year_name.value] >= year_range[0]) &
                (df_all[VarNames.year_name.value] <= year_range[1])]
        if variable:
            df_all = df_all[df_all[VarNames.output_variable.value].isin(variable)]

        if scenario:
            df_all = df_all[df_all[VarNames.scenario.value].isin(scenario)]

        if df_all.empty:
            fig.update_layout(title="No data for selected years/variables", template="plotly_white")
            return fig

        df_regions = df_all
        if continent:
            df_regions = df_regions[df_regions[VarNames.continent.value].isin(continent)]
        allowed_regions = set(df_regions[VarNames.carbon_region.value].dropna().unique())

        df_countries = df_all
        if continent:
            df_countries = df_countries[df_countries[VarNames.continent.value].isin(continent)]
        if region:
            df_countries = df_countries[df_countries[VarNames.carbon_region.value].isin(
                region if isinstance(region, list) else [region]
            )]
        allowed_countries = set(df_countries[VarNames.ISO3.value].dropna().unique())

        sel_countries = []
        if country:
            if isinstance(country, list):
                sel_countries = [c for c in country if c in allowed_countries]
            else:
                sel_countries = [country] if country in allowed_countries else []

        sel_regions = []
        if region:
            if isinstance(region, list):
                sel_regions = [r for r in region if r in allowed_regions]
            else:
                sel_regions = [region] if region in allowed_regions else []

        if sel_countries:
            df_plot = df_all[df_all[VarNames.ISO3.value].isin(sel_countries)].copy()
            active_level = "country"
            active_label = ", ".join(sel_countries)
        elif sel_regions:
            df_plot = df_all[df_all[VarNames.carbon_region.value].isin(sel_regions)].copy()
            active_level = "region"
            active_label = ", ".join(sel_regions)
        elif continent:
            df_plot = df_all[df_all[VarNames.continent.value].isin(continent)].copy()
            active_level = "continent"
            active_label = ", ".join(continent if isinstance(continent, list) else [continent])
        else:
            df_plot = df_all.copy()
            active_level = "global"
            active_label = "Global"

        if df_plot.empty:
            fig.update_layout(
                title=f"No data for selected geography (level={active_level})",
                template="plotly_white"
            )
            return fig

        col_name = VarNames.carbon_stock.value if stock_type == VarNames.carbon_stock.value else VarNames.carbon_stock_chg.value

        df_agg = df_plot.groupby([VarNames.year_name.value, VarNames.output_variable.value,
                                  VarNames.scenario.value], as_index=False).agg({col_name: "sum"})

        if value_type == "shares":

            default_mode = not variable or len(variable) == 0

            if default_mode:
                df_disagg = df_agg[
                    ~df_agg[VarNames.output_variable.value].isin(
                        [VarNames.carbon_total.value,
                         VarNames.carbon_sawnwood.value,
                         VarNames.carbon_wood_based_panels.value,
                         VarNames.carbon_paper_and_paperboard.value]
                    )
                ].copy()
                df_hwp = pd.DataFrame(columns=df_agg.columns)

            else:
                hwp_selected = VarNames.carbon_hwp.value in df_agg[VarNames.output_variable.value].unique()
                if hwp_selected:
                    df_disagg = df_agg[
                        ~df_agg[VarNames.output_variable.value].isin(
                            [VarNames.carbon_total.value,
                             VarNames.carbon_sawnwood.value,
                             VarNames.carbon_wood_based_panels.value,
                             VarNames.carbon_paper_and_paperboard.value]
                        )
                    ].copy()

                    df_hwp = pd.DataFrame(columns=df_agg.columns)
                else:
                    df_disagg = df_agg[
                        ~df_agg[VarNames.output_variable.value].isin(
                            [VarNames.carbon_total.value, VarNames.carbon_hwp.value])
                    ].copy()
                    df_hwp = pd.DataFrame(columns=df_agg.columns)

            df_total = df_agg[df_agg[VarNames.output_variable.value] == VarNames.carbon_total.value].copy()

            totals = df_disagg.groupby([VarNames.year_name.value,
                                        VarNames.scenario.value])[col_name].transform("sum")

            df_disagg[col_name] = (df_disagg[col_name] / totals * 100).fillna(0.0)

            if not df_hwp.empty:
                df_hwp[col_name] = 100.0
            if not df_total.empty:
                df_total[col_name] = 100.0

            df_agg = pd.concat([df_disagg, df_hwp, df_total], ignore_index=True)

        available_vars = df_agg[VarNames.output_variable.value].unique().tolist()
        if variable and len(variable) > 0:
            variables_order = [v for v in variable if v in available_vars]
        else:
            variables_order = [v for v in available_vars
                               if v not in [VarNames.carbon_total.value,
                                            VarNames.carbon_sawnwood.value,
                                            VarNames.carbon_paper_and_paperboard.value,
                                            VarNames.carbon_wood_based_panels.value]]

        df_agg['x_cat'] = df_agg.apply(lambda r: f"{r[VarNames.year_name.value]} - {r[VarNames.scenario.value]}",
                                       axis=1)
        n_scenarios = df_agg[VarNames.scenario.value].nunique()
        years = df_agg[VarNames.year_name.value].unique()
        n_years = df_agg[VarNames.year_name.value].nunique()
        tickvals = DataManager.generate_tickvals(n_scenarios=n_scenarios, n_years=n_years)
        ticktext = sorted(df_agg[VarNames.year_name.value].unique())
        unit = "%" if value_type == "shares" else " MtC"
        for var in variables_order:
            subset = df_agg[df_agg[VarNames.output_variable.value] == var]
            # activate the main and footer hover for hovermode closest
            # main_hover = [f"<b>{var}</b>: {y_val:.2f}{unit}" for y_val in subset[col_name]]
            # footer_hover = [f"<span style='font-size:12px'>Year: {yr}<br>Scenario: {sc}</span>"
            #                for yr, sc in zip(subset[VarNames.year_name.value], subset[VarNames.scenario.value])]

            # subset['main_hover'] = main_hover
            # subset['footer_hover'] = footer_hover

            fig.add_trace(go.Bar(
                x=subset['x_cat'],
                y=subset[col_name],
                name=var,
                marker=dict(color=pool_colors[var]),
                # customdata=subset[['main_hover', 'footer_hover']],
                hovertemplate=f"<b>{var}</b>: %{{y:.2f}}{unit}<extra></extra>"
            ))

        if stock_type == VarNames.carbon_stock_chg.value:
            df_total = df_agg[df_agg[VarNames.output_variable.value].isin(variables_order)
            ].groupby(['x_cat'], as_index=False)[col_name].sum()

            x_vals = df_total['x_cat'].tolist()
            y_vals = df_total[col_name].tolist()

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                marker=dict(size=10, color='black', symbol='circle-cross'),
                showlegend=False,
                hovertemplate="<b>Total</b>: %{y:.2f} MtC<extra></extra>"
            ))

        if value_type == "shares":
            y0 = 0
            y1 = 100
        else:
            df_min_max = df_agg[df_agg[VarNames.output_variable.value].isin(variables_order)
            ].groupby([VarNames.year_name.value, VarNames.scenario.value]).agg({col_name: "sum"})
            y1 = max(df_min_max[col_name])
            if stock_type == VarNames.carbon_stock_chg.value:
                y0 = min(df_min_max[col_name])
            else:
                y0 = 0

        line_positions = [i * n_scenarios - 0.5 for i in range(1, len(years))]
        for x in line_positions:
            fig.add_shape(
                type="line",
                x0=x, x1=x,
                y0=y0, y1=y1,
                line=dict(color="black", width=1, dash="dot"),
                xref="x", yref="y"
            )

        title_level = {
            "country": "Country level",
            "region": "Region level",
            "continent": "Continent level",
            "global": "Global"
        }[active_level]

        fig.update_layout(
            title=f"Carbon Stocks by Pool — {title_level}: {active_label}",
            barmode="relative",
            xaxis=dict(title=VarNames.year_name.value,
                       tickvals=tickvals,
                       ticktext=ticktext,
                       tickangle=0
                       ),
            yaxis=dict(title="Share [%]" if value_type == "shares" else "Carbon Stock [MtC]", rangemode="tozero"),
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", y=-0.2),
            bargap=0.2
        )

        return fig

    def plot_world_map(self, data, continent, region, country, variable, value_type, stock_type, year_range, scenario):
        df_all = data.copy()
        if year_range:
            df_all = df_all[(df_all[VarNames.year_name.value] >= year_range[0]) &
                            (df_all[VarNames.year_name.value] <= year_range[1])]

        if scenario:
            df_all = df_all[df_all[VarNames.scenario.value].isin([scenario[0]])]

        default_pools = [VarNames.carbon_forest_biomass.value, VarNames.carbon_dwl.value, VarNames.carbon_soil.value,
                         VarNames.carbon_hwp.value, VarNames.carbon_substitution.value]
        selected_vars = variable if variable and len(variable) > 0 else default_pools

        df_all = df_all[df_all[VarNames.output_variable.value].isin(selected_vars)].copy()

        sel_countries = country if country else []
        sel_regions = region if region else []
        sel_continents = continent if continent else []

        if sel_countries:
            df_plot = df_all[df_all[VarNames.ISO3.value].isin(sel_countries)].copy()
            active_level = "Country"
            active_label = ", ".join(sel_countries)
        elif sel_regions:
            df_plot = df_all[df_all[VarNames.carbon_region.value].isin(sel_regions)].copy()
            active_level = "Region"
            active_label = ", ".join(sel_regions)
        elif sel_continents:
            df_plot = df_all[df_all[VarNames.continent.value].isin(sel_continents)].copy()
            active_level = "Continent"
            active_label = ", ".join(sel_continents if isinstance(sel_continents, list) else [sel_continents])
        else:
            df_plot = df_all.copy()
            active_level = "Global"
            active_label = "Global"

        country_data = df_plot.groupby([VarNames.ISO3.value,
                                       VarNames.output_variable.value], as_index=False).agg({stock_type: "mean"})
        country_data = country_data[country_data[stock_type] >= 0.001].reset_index()

        country_pivot = country_data.pivot(index=VarNames.ISO3.value,
                                           columns=VarNames.output_variable.value,
                                           values=stock_type).reset_index()
        country_pivot["Total_Selected"] = country_pivot[selected_vars].sum(axis=1)

        if value_type == "shares":
            totals = country_pivot[selected_vars].sum(axis=1).replace(0, np.nan)
            for v in selected_vars:
                country_pivot[v] = (country_pivot[v] / totals * 100).fillna(0.0)

        hover_texts = []
        footer_texts = []
        for _, row in country_pivot.iterrows():
            if scenario:
                footer_texts.append(f'<span style="font-size:12px;"><b>ISO: {row[VarNames.ISO3.value]}</b>'
                                    f'<br><b>{scenario[0]}</b>')
            else:
                footer_texts.append(f'<span style="font-size:12px;"><b>ISO: {row[VarNames.ISO3.value]}</b>')
            parts = []
            for v in selected_vars:
                if value_type == "shares":
                    parts.append(f"{v}: {row[v]:.2f}%")
                else:
                    parts.append(f"{v}: {row[v]:.2f} MtC")
            parts.append(f"Total: {row['Total_Selected']:.2f} MtC")
            hover_texts.append("<br>".join(parts))

        country_pivot["hover_text"] = hover_texts
        country_pivot["footer_text"] = footer_texts

        fig = px.choropleth(
            country_pivot,
            locations=VarNames.ISO3.value,
            color='Total_Selected',
            color_continuous_scale="Greens"
        )

        fig.update_traces(
            customdata=country_pivot[["hover_text", "footer_text"]],
            hovertemplate="%{customdata[0]}<extra>%{customdata[1]}</extra>"
        )

        fig.update_layout(
            title=f"<br><br>Carbon Stock by Pool – {active_level}: {active_label}",
            geo=dict(
                showcoastlines=True,
                coastlinecolor="LightGray",
                showocean=False,
                oceancolor="LightBlue",
                projection_type="natural earth",
                lonaxis_range=[-360, 360],
                lataxis_range=[-55, 55],
                projection=dict(scale=0.8)
            ),
            margin=dict(l=1, r=1, t=1, b=1),
            coloraxis_showscale=False,
            template='plotly_white'
        )
        return fig

    def update_plot_carbon(self, continent, region, country, variable, scenario, year_range, value_type_1, stock_type_1,
                           value_type_2, stock_type_2, pool_colors):
        filtered_data = self.filter_data(continent, region, country, variable, year_range, scenario)

        fig_carbon_left = self.plot_stacked_area_chart(data=filtered_data,
                                                       continent=continent,
                                                       region=region,
                                                       country=country,
                                                       variable=variable,
                                                       scenario=scenario,
                                                       value_type=value_type_1,
                                                       stock_type=stock_type_1,
                                                       year_range=year_range,
                                                       pool_colors=pool_colors)

        fig_carbon_right = self.plot_world_map(data=filtered_data,
                                               continent=continent,
                                               region=region,
                                               country=country,
                                               variable=variable,
                                               scenario=scenario,
                                               value_type=value_type_2,
                                               stock_type=stock_type_2,
                                               year_range=year_range)

        return fig_carbon_left, fig_carbon_right

    def open_browser(self, url):
        import webbrowser
        webbrowser.open_new(url)

    def run(self, open_browser=True, port=8050):
        if open_browser:
            from threading import Timer
            Timer(1, lambda: self.open_browser(f"http://localhost:{port}")).start()

        self.app.run(host='localhost', port=port, debug=False, dev_tools_ui=False, dev_tools_hot_reload=False)


