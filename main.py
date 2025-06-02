import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_ind, levene
from database import init_db, q3_query, q4_query, q5a_query, q5b_query, q5c_query
import sqlite3

if 'cell_count_df' not in st.session_state:
    st.session_state.cell_count_df = pd.read_csv('data/cell-count.csv')

if 'sqlite_init' not in st.session_state:
    init_db(st.session_state.cell_count_df)
    st.session_state.sqlite_init = True

sqlite_conn = sqlite3.connect("demo_db.sqlite")
sqlite_cursor = sqlite_conn.cursor()

def main():
    st.set_page_config(page_title="Teiko Technical Interview", layout="wide")
    
    # Sidebar
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to", ["Home", "Python Tasks", "Database Tasks", "More about Leopold"])

    if section == 'Home':
        show_home()
    elif section == "Python Tasks":
        show_python()
    elif section == "Database Tasks":
        show_database()
    elif section == "More about Leopold":
        show_leopold()

def display_question(question_title, question_text):
    st.header(question_title)
    with st.expander('See full question'):
        st.write(question_text)

def show_home():
    st.title("Teiko Technical Interview")
    st.write("This is Leopold Marx's submission to a technical interview for Teiko that was assigned Saturday, May 31st, 2025. This website is Streamlit-based developed for a technical interview project. It includes a database schema, statistical analysis, and visualizations. It also demonstrates technical knowledge in deploying a website. This website is hosted on my home server via a Docker Container.")
    

def show_python():
    st.header("Python Tasks")

    # QUESTION 1
    display_question('Question 1', """Please write a Python program to convert cell count in cell-count.csv to relative frequency (in percentage) of total cell count for each sample. Total cell count of each sample is the sum of cells in the five populations of that sample. Please return an output file in CSV format with cell count and relative frequency of each population of each sample per line. The output file should have the following columns:
* sample: the sample id as in column sample in cell-count.csv
* total_count: total cell count of sample
* population: name of the immune cell population (e.g. b_cell, cd8_t_cell, etc.)
* count: cell count
* percentage: relative frequency in percentage""")

    relative_frequency = st.session_state.cell_count_df.copy()

    relative_frequency['total_count'] = relative_frequency['b_cell'] + \
                                        relative_frequency['cd8_t_cell'] + \
                                        relative_frequency['cd4_t_cell'] + \
                                        relative_frequency['nk_cell'] + \
                                        relative_frequency['monocyte']

    melted_rf = pd.melt(relative_frequency
                        , id_vars=['sample']
                        , value_vars=['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
                        , var_name='population'
                        , value_name='count')
    
    melted_rf = melted_rf.merge(relative_frequency, how='left', on='sample')
    melted_rf['percentage'] = melted_rf['count'] / melted_rf['total_count']

    q1_result = melted_rf[['sample', 'total_count', 'population', 'count', 'percentage']]

    with st.expander('See code'):
        st.code("""
relative_frequency = cell_count_df.copy()

relative_frequency['total_count'] = relative_frequency['b_cell'] + \\
                                    relative_frequency['cd8_t_cell'] + \\
                                    relative_frequency['cd4_t_cell'] + \\
                                    relative_frequency['nk_cell'] + \\
                                    relative_frequency['monocyte']

melted_rf = pd.melt(relative_frequency
                    , id_vars=['sample']
                    , value_vars=['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
                    , var_name='population'
                    , value_name='count')

melted_rf = melted_rf.merge(relative_frequency, how='left', on='sample')
melted_rf['percentage'] = melted_rf['count'] / melted_rf['total_count']

q1_result = melted_rf[['sample', 'total_count', 'population', 'count', 'percentage']]""", language='python')
    
    q1_result['percentage'] = q1_result['percentage']*100
    st.dataframe(q1_result, hide_index=True, column_config={
        'percentage':st.column_config.NumberColumn(
            'percentage',
            format='%.2f%%'
        )
    })

    # QUESTION 2
    display_question('Question 2', '''Among patients who have treatment tr1, we are interested in comparing the differences in cell population relative frequencies of melanoma patients who respond (responders) to tr1 versus those who do not (non-responders), with the overarching aim of predicting response to treatment tr1. Response information can be found in column response, with value y for responding and value n for non-responding. Please only include PBMC (blood) sample.

a. For each immune cell population, please generate a boxplot of the population relative frequencies comparing responders versus non-responders.

b. Which cell populations are significantly different in relative frequencies between responders and non-responders? Please include statistics to support your conclusion.'''
    )

    st.subheader('2a')

    with st.expander('See code'):
        st.code("""
# filter treatment, condition, and sample_type
tr1_rf = melted_rf[melted_rf['treatment'] == 'tr1'].reset_index(drop=True)
tr1_rf_melanoma = tr1_rf[tr1_rf['condition'] == 'melanoma'].reset_index(drop=True)
tr1_rf_melanoma_pbmc = tr1_rf_melanoma[tr1_rf_melanoma['sample_type'] == 'PBMC'].reset_index(drop=True)

# creates two columns for streamlit
selection, plot_col = st.columns([1, 4])

pop = selection.radio('Select a population', options=['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte'])

# generates plotly boxplot for a specific population 
tr1_rf_melanoma_pbmc_pop = tr1_rf_melanoma_pbmc[tr1_rf_melanoma_pbmc['population'] == pop]
fig = px.box(tr1_rf_melanoma_pbmc_pop, x="response", y="percentage")
fig.update_layout(title_text=f'Population: {pop}')
plot_col.plotly_chart(fig)

# statistics for 2b
response_group = tr1_rf_melanoma_pbmc_pop[tr1_rf_melanoma_pbmc_pop['response'] == 'y'][pop].values
non_response_group = tr1_rf_melanoma_pbmc_pop[tr1_rf_melanoma_pbmc_pop['response'] == 'n'][pop].values
_, levene_p_value = levene(response_group, non_response_group)
equal_variance = levene_p_value >= 0.05
_, ttest_p_value = ttest_ind(response_group, non_response_group, equal_var=equal_variance)

with plot_col.expander('Detailed Statistics for 2b'):
    detailed_stats = pd.DataFrame(
        [
            ['Levene Variance Test p value', round(levene_p_value, 4)]
            , ['Equal Variance', equal_variance]
            , ['Independent t-test used', 'standard t-test' if equal_variance else "Welch's t-test"]
            , ['t-test p value', round(ttest_p_value, 4)]
            , ['N Total', len(tr1_rf_melanoma_pbmc_pop.index)]
            , ['N Response', len(response_group)]
            , ['N Non-Response', len(non_response_group)]
        ]
        , columns=['Description', 'Value']
    )
    st.dataframe(detailed_stats, hide_index=True)""", language='python')

    st.header('Cell Population Response Boxplot')

    # filter treatment, condition, and sample_type
    tr1_rf = melted_rf[melted_rf['treatment'] == 'tr1'].reset_index(drop=True)
    tr1_rf_melanoma = tr1_rf[tr1_rf['condition'] == 'melanoma'].reset_index(drop=True)
    tr1_rf_melanoma_pbmc = tr1_rf_melanoma[tr1_rf_melanoma['sample_type'] == 'PBMC'].reset_index(drop=True)

    # creates two columns for streamlit
    selection, plot_col = st.columns([1, 4])

    pop = selection.radio('Select a population', options=['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte'])

    # generates plotly boxplot for a specific population 
    tr1_rf_melanoma_pbmc_pop = tr1_rf_melanoma_pbmc[tr1_rf_melanoma_pbmc['population'] == pop]
    fig = px.box(tr1_rf_melanoma_pbmc_pop, x="response", y="percentage")
    fig.update_layout(title_text=f'Population: {pop}')
    plot_col.plotly_chart(fig)

    # statistics for 2b
    response_group = tr1_rf_melanoma_pbmc_pop[tr1_rf_melanoma_pbmc_pop['response'] == 'y']
    non_response_group = tr1_rf_melanoma_pbmc_pop[tr1_rf_melanoma_pbmc_pop['response'] == 'n']
    _, levene_p_value = levene(response_group[pop].values, non_response_group[pop].values)
    equal_variance = levene_p_value >= 0.05
    _, ttest_p_value = ttest_ind(response_group[pop].values, non_response_group[pop].values, equal_var=equal_variance)

    with plot_col.expander('Detailed Statistics for 2b'):
        detailed_stats = pd.DataFrame(
            [
                ['Levene Variance Test p value', round(levene_p_value, 4)]
                , ['Equal Variance', equal_variance]
                , ['Indedpendent t-test used', 'standard t-test' if equal_variance else "Welch's t-test"]
                , ['t-test p value', round(ttest_p_value, 4)]
                , ['# Samples', len(tr1_rf_melanoma_pbmc_pop.index)]
                , ['# Samples Response', len(response_group[pop].values)]
                , ['# Samples Non-Response', len(non_response_group[pop].values)]
                , ['Unique Subjects', len(tr1_rf_melanoma_pbmc_pop.subject.unique())]
                , ['Unique Subjects Response', len(response_group.subject.unique())]
                , ['Unique Subjects Non-Response', len(non_response_group.subject.unique())]
            ]
            , columns=['Description', 'Value']
        )
        st.dataframe(detailed_stats, hide_index=True)

    st.subheader('2b')
    st.write("""
After filtering treatment to "tr1", condition to "melanoma", and sample type to "PBMC", we have a total of 9 samples (6 response and 3 non-response) for 6 unique subjects (4 response and 2 non-response). It is generally recommended to have 30+ samples (ideally 30+ subjects) in each category before we can start making statistical inferences.

If we ignore the 30+ observations recommendation for the purposes of a technical interview, the t-tests can be used to determine if there is a significant difference between the two groups. We can see the results of running t-tests for each population under the "Detailed Statistics for 2b" expansion above. The relative frequency for "cd4_t_cell" and "monocyte" populations are statistically different (t-test p-value < 0.05) between response and non-response groups. 
             
I came to this conclusion by first performing a Levene Variance test to determine if the two groups have significantly different variances. If the groups have significatly different variances, it's recommended to perform the Welch's t-test over the standard t-test. Since all populations resulted in equal variances, I performed the standard t-test.
""")

def display_query_and_results(query):
    st.code(query, language='sql')
    st.write(pd.read_sql(query, sqlite_conn))

def show_database():
    st.header("Database Tasks")


    display_question("Database Question 1", """How would you design a database to capture the type of information and data in cell-count.csv? Imagine that you’d have hundreds of project, thousands of sample and various types of analytics you’d want to perform, including the example analysis of responders versus non-responders comparisons above. Please provide a rough prototype schema.""")

    st.write("""Please see the ER Diagram below created in Lucid Chart. Adding additional metrics like `date_remission` in `subject_condition` or more attributes in the `subject` table like `weight`, `ethnicity`, and/or `height` could be valuable for more complex analysis.
             
The `cell-count.csv` file provided had multiple samples from a given patient but only allowed one condition or treatment to be reported. I improved the format of the data by allowing the database to assign multiple treatments and conditions to each subject. This allows for more complex analysis of treatment effectiveness if there is some interaction between multiple treatments or conditions.""")
    st.image('Teiko ER Diagram.png')

    st.header("Database Question 2")
    with st.expander('See full question'):
        st.write("""What would be some advantages in capturing this information in a database?""")
    
    st.write('''Where do I start! Here are a couple of bullet points:
             
* Databases allow data to scale to incredible sizes, larger than what could fit on one computer alone.
* Creating databases usually implies there is an ETL process to load the database. Implementing ETL processes ensures more reliable data than manually updating databases.
* Data Integrity can be ensured with foreign keys, forced datatypes, and constraints.
* Querying in SQL allows for a strong and diverse uses of the database. Allowing it to be a central repository for all data requests.
* Modular expansion like adding new cell types, other biomarkers, project, etc.
* Security measures can be implemented to protect patient's HIPAA data.
* Much more!''')
    
    display_question('Database Question 3', """Based on the schema you provide in (1), please write a query to summarize the number of subject available for each condition.""")

    st.write('Rather than writing queries against a hypothetically database, I decided to build this exact schema in SQLite. The queries below actually query the database and display the results. I imported the `cell-count.csv` data into the SQLite database. At the bottom of this page, there is a section where you can write your own query against this database.')
    
    display_query_and_results(q3_query)

    st.write("Note: Subjects with no recorded condition (None/Null) are considered 'healthy.'")

    display_question('Database Question 4', """Please write a query that returns all melanoma PBMC sample at baseline (time_from_treatment_start is 0) from patients who have treatment tr1.""")

    display_query_and_results(q4_query)

    display_question('Database Question 5', """Please write queries to provide these following further breakdowns for the sample in (4):

a. How many sample from each project

b. How many responders/non-responders

c. How many males, females""")

    st.subheader('a.')
    display_query_and_results(q5a_query)

    st.subheader('b.')
    display_query_and_results(q5b_query)

    st.subheader('c.')
    display_query_and_results(q5c_query)

    st.header('Run your own query')
    query_text = st.text_area('Please write your own query!', height=340)
    if st.button('Run Query!'):
        st.write(pd.read_sql(query_text, sqlite_conn))

def show_leopold():
    st.header("Leopold Marx")
    st.markdown('''<div style="position: relative; width: 100%; height: 0; padding-top: 129.4118%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAEMIjzac_w/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAEMIjzac_w&#x2F;view?utm_content=DAEMIjzac_w&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">Leopold Graphic Resume</a> by Leopold Marx''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
