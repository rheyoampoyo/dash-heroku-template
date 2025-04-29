import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import Dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = """
##### What is the General Social Survey (GSS)?\n

1971 was the first year during an era of social change which the director of the National Opinion Research Center (NORC) at the University of Chicago, 
James A. Davis, had propsed to conduct an annual national research project to monitor our attitudes on social issues. Then, in 1972, NORC launched the 
General Social Survey (GSS) which became the standard for unbiased social research.\n

The data in the GSS aims to monitor the trends in opinions, attitude and behaviors over the years with a core of demographic, behavioral, attitudinal questions and 
additional questions on topics such as civil liberties, crime and violence economic performance and many other issues. These questions are also adapted to
include current issues such as COVID-19 issues in 2020. Up until 1994, the data was collected via in-person surveys yearly, but switched to be held every other year. 
Additionally, the GSS had been adapted to become computer assisted to be efficient and cost effective.

##### Discussing the Gender Wage Gap, Prestige Wage Gap, and the Gender Wage Gap Based on Prestige \n

According to the Pew Research Center, the gender wage gap has narrowed slightly over the past two decades. In 2024, women were reported to earn 85% of what men were paid. In contrast
to 2003, women were reported to earn 81% of what men were paid. Interestingly, according to Stocks University, the wage gap based on prestige has not changed much over the past two decades.
Below, we will beexploring the gender wage gap and the gender wage gap based on prestige. Hopefully, we can find that the gap has further narrowed in the analysis below. \n


References: \n
https://gss.norc.org/us/en/gss/about-the-gss.html \n
https://gss.norc.org/us/en/gss/gss50.html \n
https://www.pewresearch.org/short-reads/2025/03/04/gender-pay-gap-in-us-has-narrowed-slightly-over-2-decades/
"""

gss_means_by_sex = gss_clean.groupby(['sex']).agg({'income': 'mean',
                                            'job_prestige': 'mean', 
                                            'socioeconomic_index': 'mean', 
                                            'education': 'mean'}).reset_index()

gss_means_by_sex = gss_means_by_sex.round(2)

fig_means = ff.create_table(gss_means_by_sex)

gss_bread_winner = gss_clean.groupby(['sex','male_breadwinner']).size().reset_index(name = 'count')

fig_breadwinner = px.bar(gss_bread_winner,
                         x = 'male_breadwinner', 
                         y = 'count', 
                         color = 'sex',
                         labels={'male_breadwinner':'Sentiment of Men as Breadwinners',
                                 'count':'Number of Respondents'})
fig_prestige_income = px.scatter(gss_clean, 
                                x = 'job_prestige', 
                                y = 'income', 
                                color = 'sex',
                                labels={'job_prestige':'Job Prestige',
                                        'income':'Income'},
                                hover_data=['education', 'socioeconomic_index'],
                                trendline='ols')
gss_income_prestige = gss_clean[['sex', 'income', 'job_prestige']].dropna()

fig_income_box = px.box(gss_income_prestige,
                                        x='sex',
                                        y='income',
                                        color='sex',
                                        labels={'income':'Income', 'sex':'Sex'})

fig_prestige_box = px.box(gss_income_prestige,
                                        x='sex',
                                        y='job_prestige',
                                        color='sex',
                                        labels={'job_prestige':'Job Prestige', 'sex':'Sex'})


fig_income_box.update_layout(showlegend=False)
fig_prestige_box.update_layout(showlegend=False)

gss_income_prestige['job_prestige_cat'] = pd.cut(gss_clean.job_prestige, 6)

gss_income_prestige_cat = gss_income_prestige[['sex','income','job_prestige_cat']].dropna()
fig_income_prestige = px.box(
    gss_income_prestige_cat,
    x='sex', 
    y='income', 
    facet_col='job_prestige_cat',
    facet_col_wrap=2,
    color='sex',
    labels={'sex':'Sex', 'income':'Income', 'job_prestige_cat':'Job Prestige Category'}
)

gss_columns = gss_clean[['satjob', 'relationship','male_breadwinner','men_bettersuited','child_suffer','men_overwork']].dropna()
group = ['sex', 'region', 'education']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1("Exploring the Gender-Prestige Pay Gap through the General Social Survey"),
    
    dcc.Markdown(children=markdown_text),

    html.H2("Mean income, Occupational prestige, Socioeconomic index, and Years of Education across Sexes",
            style={'fontSize': '28px'}),
    dcc.Graph(figure=fig_means),

    html.H3('Count of Sentiments grouped by Sex, Region, or Education'),
    
    html.Div([
        html.Label("Select feature:"),
        dcc.Dropdown(
            id='x-axis',
            options=[{'label': col, 'value': col} for col in gss_columns],
            value='satjob'
        ),

        html.Label("Group by:"),
        dcc.Dropdown(
            id='group',
            options=[{'label': col, 'value': col} for col in group],
            value='sex'
        )
    ], style={'width': '35%', 'float': 'left'}),


    html.Div([
        dcc.Graph(id='bar-chart')
    ], style={'width': '65%', 'float': 'right'}),

                dcc.Markdown(children=
                     """
* `sex` - male or female
* `education` - years of formal education
* `region` - region of the country where the respondent lives
* `satjob` - responses to "On the whole, how satisfied are you with the work you do?"
* `relationship` - agree or disagree with: "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."
* `male_breadwinner` - agree or disagree with: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."
* `men_bettersuited` - agree or disagree with: "Most men are better suited emotionally for politics than are most women."
* `child_suffer` - agree or disagree with: "A preschool child is likely to suffer if his or her mother works."
* `men_overwork` - agree or disagree with: "Family life often suffers because men concentrate too much on their work.
                     """),

    html.H4('Income vs. Job Prestige'),
    dcc.Graph(figure=fig_prestige_income),

    html.Div([
        html.H5("Distribution of Income by Sex"),
        dcc.Graph(figure=fig_income_box)
    ], style={'width': '50%', 'float': 'left'}),

    html.Div([
        html.H5("Distribution of Job Prestige by Sex"),
        dcc.Graph(figure=fig_prestige_box)
    ], style={'width': '50%', 'float': 'right'}),

    html.H6('Income Distribution by Sex and Job Prestige Category'),
    dcc.Graph(figure=fig_income_prestige)
])

@app.callback(
    Output('bar-chart', 'figure'),
    Input(component_id='x-axis', component_property='value'),
    Input(component_id='group', component_property='value')
)
def update_bar_chart(x, group):
    df_filtered = gss_clean[[x, group]].dropna()
    grouped = df_filtered.groupby([x, group]).size().reset_index(name='Count')
    fig = px.bar(grouped, 
                 x=x, 
                 y='Count', 
                 color=group, 
                 barmode='group')
    fig.update_layout(height=600)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
