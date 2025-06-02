import sqlite3
import pandas as pd

def init_db(cell_count_df):
    sqlite_conn = sqlite3.connect("demo_db.sqlite")
    sqlite_cursor = sqlite_conn.cursor()
    schema_sql = """
    -- Project table
    DROP TABLE IF EXISTS project;
    CREATE TABLE project (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        project_description TEXT
    );

    INSERT INTO project (project_name, project_description)
    VALUES ('prj1', 'Project 1'),('prj2', 'Project 2'),('prj3', 'Project 3');

    -- subject table
    DROP TABLE IF EXISTS subject;
    CREATE TABLE subject (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        sex TEXT CHECK(sex IN ('F', 'M')),
        date_of_birth DATE,
        FOREIGN KEY (project_id) REFERENCES project(project_id)
    );

    INSERT INTO subject (project_id, sex, date_of_birth)
    VALUES (1, 'F', '1955-05-01') --70 years
    , (1, 'F', '1960-05-01')
    , (1, 'M', '1950-05-01')
    , (1, 'F', '1965-05-01')
    , (1, 'M', '1948-05-01')
    , (2, 'M', '1980-05-01')
    , (2, 'F', '1945-05-01')
    , (2, 'F', '1995-05-01')
    , (2, 'M', '1953-05-01')
    , (2, 'M', '1963-05-01')
    , (2, 'F', '1970-05-01')
    , (3, 'F', '1975-05-01')
    , (3, 'M', '1975-05-01')
    ;

    -- condition table
    DROP TABLE IF EXISTS condition;
    CREATE TABLE condition (
        condition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        condition_name TEXT NOT NULL
    );

    INSERT INTO condition (condition_name)
    VALUES ('melanoma'), ('lung')
    ;

    -- Subject-Condition table (join table)
    DROP TABLE IF EXISTS subject_condition;
    CREATE TABLE subject_condition (
        subject_id INTEGER,
        condition_id INTEGER,
        date_diagnosed DATE,
        date_remission DATE,
        FOREIGN KEY (subject_id) REFERENCES subject(subject_id),
        FOREIGN KEY (condition_id) REFERENCES condition(condition_id),
        PRIMARY KEY (subject_id, condition_id)
    );

    INSERT INTO subject_condition (subject_id, condition_id, date_diagnosed)
    VALUES (1, 1, '2025-04-30')
    , (3, 1, '2025-04-30')
    , (4, 2, '2025-04-30')
    , (8, 1, '2025-04-30')
    , (9, 1, '2025-04-30')
    , (10, 2, '2025-04-30')
    , (11, 2, '2025-04-30')
    , (12, 1, '2025-04-30')
    , (13, 1, '2025-04-30')
    ;

    -- treatment table
    DROP TABLE IF EXISTS treatment;
    CREATE TABLE treatment (
        treatment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        treatment_name TEXT NOT NULL,
        treatment_description TEXT
    );

    INSERT INTO treatment (treatment_name, treatment_description)
    VALUES ('tr1', 'Treatment 1'), ('tr2', 'Treatment 2');

    -- Subject-treatment table (join table)
    DROP TABLE IF EXISTS subject_treatment;
    CREATE TABLE subject_treatment (
        subject_id INTEGER,
        treatment_id INTEGER,
        response TEXT CHECK(response IN ('y', 'n')),
        FOREIGN KEY (subject_id) REFERENCES subject(subject_id),
        FOREIGN KEY (treatment_id) REFERENCES treatment(treatment_id),
        PRIMARY KEY (subject_id, treatment_id)
    );

    INSERT INTO subject_treatment (subject_id, treatment_id, response)
    VALUES (1,1,'y')
    , (3,1,'n')
    , (4,2,'y')
    , (8,1,'y')
    , (9,1,'y')
    , (10,1,'n')
    , (11,1,'n')
    , (12,1,'n')
    , (13,1,'y')
    ;

    -- sample table
    DROP TABLE IF EXISTS sample;
    CREATE TABLE sample (
        sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        sample_type TEXT,
        time_from_treatment_start INTEGER,
        FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
    );

    -- Cell Types table
    DROP TABLE IF EXISTS cell_type;
    CREATE TABLE cell_type (
        cell_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_type_name TEXT NOT NULL,
        cell_type_description TEXT
    );

    INSERT INTO cell_type (cell_type_name, cell_type_description)
    VALUES ('b_cell', 'b_cell')
    , ('cd8_t_cell', 'cd8_t_cell')
    , ('cd4_t_cell', 'cd4_t_cell')
    , ('nk_cell', 'nk_cell')
    , ('monocyte', 'monocyte')
    ;

    -- Cell Counts table
    DROP TABLE IF EXISTS cell_count;
    CREATE TABLE cell_count (
        sample_id INTEGER NOT NULL,
        cell_type_id INTEGER NOT NULL,
        cell_count INTEGER,
        PRIMARY KEY (sample_id, cell_type_id),
        FOREIGN KEY (sample_id) REFERENCES sample(sample_id),
        FOREIGN KEY (cell_type_id) REFERENCES cell_type(cell_type_id)
    );
    """
    
    sample = []
    cell = []
    for i,r in cell_count_df.iterrows():
        subject_id = int(r['subject'][3:])
        if not pd.isna(r['time_from_treatment_start']):
            sample.append([subject_id, r['sample_type'], r['time_from_treatment_start']])

        cell.append([i+1, 1, r['b_cell']])
        cell.append([i+1, 2, r['cd8_t_cell']])
        cell.append([i+1, 3, r['cd4_t_cell']])
        cell.append([i+1, 4, r['nk_cell']])
        cell.append([i+1, 5, r['monocyte']])

    insert_sample_query = f"""
    INSERT INTO sample (subject_id, sample_type, time_from_treatment_start)
    VALUES {','.join(f"({s[0]}, '{s[1]}', {s[2]})" for s in sample)}
    """

    insert_cell_query = f"""
    INSERT INTO cell_count (sample_id , cell_type_id, cell_count)
    VALUES {','.join(f"({c[0]}, {c[1]}, {c[2]})" for c in cell)}
    """

    sqlite_cursor.executescript(schema_sql)
    sqlite_cursor.executescript(insert_sample_query)
    sqlite_cursor.executescript(insert_cell_query)
    sqlite_conn.commit()

q3_query = """
select
    c.condition_name
    , count(distinct s.subject_id) as unique_patients
    , count(distinct case when st.response = 'y' then st.subject_id end) as responders
    , count(distinct case when st.response = 'n' then st.subject_id end) as non_responders
    , round(avg(strftime('%Y %m %d',date('now')) - strftime('%Y %m %d',s.date_of_birth)),2) average_age
from condition c
left join subject_condition sc
    on sc.condition_id = c.condition_id
left join subject s
    on s.subject_id = sc.subject_id
left join subject_treatment st
    on s.subject_id = st.subject_id
left join treatment t
    on t.treatment_id = st.treatment_id
group by c.condition_name"""

q4_query = """
select sa.sample_id
    , su.subject_id
    , sa.sample_type
    , c.condition_name
    , t.treatment_name
    , sa.time_from_treatment_start
    , ct.cell_type_name
    , cc.cell_count
from sample sa
left join subject su
    on sa.subject_id = su.subject_id
left join subject_condition sc
    on su.subject_id = sc.subject_id
left join condition c
    on sc.condition_id = c.condition_id
left join subject_treatment st
    on st.subject_id = su.subject_id
left join treatment t
    on st.treatment_id = t.treatment_id
left join cell_count cc
    on cc.sample_id = sa.sample_id
left join cell_type ct
    on cc.cell_type_id = ct.cell_type_id
where sa.sample_type = 'PBMC'
    and c.condition_name = 'melanoma'
    and t.treatment_name = 'tr1'
    and sa.time_from_treatment_start = 0
"""

q5a_query = """
select p.project_name
    , count(distinct sa.sample_id) num_sample
    , count(distinct su.subject_id) num_subject
from sample sa
left join subject su
    on sa.subject_id = su.subject_id
left join subject_condition sc
    on su.subject_id = sc.subject_id
left join condition c
    on sc.condition_id = c.condition_id
left join subject_treatment st
    on st.subject_id = su.subject_id
left join treatment t
    on st.treatment_id = t.treatment_id
left join cell_count cc
    on cc.sample_id = sa.sample_id
left join cell_type ct
    on cc.cell_type_id = ct.cell_type_id
left join project p
    on su.project_id = p.project_id
where sa.sample_type = 'PBMC'
    and c.condition_name = 'melanoma'
    and t.treatment_name = 'tr1'
    and sa.time_from_treatment_start = 0
group by p.project_name
"""

q5b_query = """
select st.response
    , count(distinct sa.sample_id) num_sample
    , count(distinct su.subject_id) num_subject
from sample sa
left join subject su
    on sa.subject_id = su.subject_id
left join subject_condition sc
    on su.subject_id = sc.subject_id
left join condition c
    on sc.condition_id = c.condition_id
left join subject_treatment st
    on st.subject_id = su.subject_id
left join treatment t
    on st.treatment_id = t.treatment_id
left join cell_count cc
    on cc.sample_id = sa.sample_id
left join cell_type ct
    on cc.cell_type_id = ct.cell_type_id
left join project p
    on su.project_id = p.project_id
where sa.sample_type = 'PBMC'
    and c.condition_name = 'melanoma'
    and t.treatment_name = 'tr1'
    and sa.time_from_treatment_start = 0
group by st.response
"""

q5c_query = """
select su.sex
    , count(distinct sa.sample_id) num_sample
    , count(distinct su.subject_id) num_subject
from sample sa
left join subject su
    on sa.subject_id = su.subject_id
left join subject_condition sc
    on su.subject_id = sc.subject_id
left join condition c
    on sc.condition_id = c.condition_id
left join subject_treatment st
    on st.subject_id = su.subject_id
left join treatment t
    on st.treatment_id = t.treatment_id
where sa.sample_type = 'PBMC'
    and c.condition_name = 'melanoma'
    and t.treatment_name = 'tr1'
    and sa.time_from_treatment_start = 0
group by su.sex
"""
# sqlite_conn = sqlite3.connect("demo_db.sqlite")
# sqlite_cursor = sqlite_conn.cursor()
# if 'sqlite_init' not in st.session_state:
#     init_db()
#     st.session_state.sqlite_init = True