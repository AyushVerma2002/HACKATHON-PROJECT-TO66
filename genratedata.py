import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import json

# =========================
# Step 1: Create Skills.csv
# =========================
# ASSUMES 'job_skills.csv' IS PRESENT
try:
    df_skills = pd.read_csv("job_skills.csv")
except FileNotFoundError:
    print("FATAL ERROR: job_skills.csv not found. Please provide this file.")
    exit()

df_skills.columns = df_skills.columns.str.strip()

# Process skills into a list
all_skills = []
for skills_str in df_skills['job_skills'].dropna():
    skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
    all_skills.extend(skills_list)

# Get unique sorted skills
unique_skills = sorted(set(all_skills))

# Guarantee "Python" appears in the unique skills list
if "Python" not in unique_skills:
    unique_skills.append("Python")

# Create a DataFrame for Skills
skills_df = pd.DataFrame({
    "skill_id": range(1, len(unique_skills) + 1),
    "skill_name": unique_skills
})

skills_df.to_csv("Skills.csv", index=False)
print(f"✅ Skills.csv created with {len(unique_skills)} unique skills.")

# =========================
# Step 2: Create Roles.csv
# =========================
# ASSUMES 'job_postings.csv' IS PRESENT
try:
    job_postings = pd.read_csv("job_postings.csv")
except FileNotFoundError:
    print("FATAL ERROR: job_postings.csv not found. Please provide this file.")
    exit()

# Ensure necessary columns are present
if 'job_link' in job_postings.columns and 'job_title' in job_postings.columns:
    roles_df = job_postings[['job_link', 'job_title']].drop_duplicates()
    roles_df['role_id'] = ['R' + str(i + 1) for i in range(len(roles_df))]
    roles_df.rename(columns={
        'job_link': 'role_external_link',
        'job_title': 'role_name'
    }, inplace=True)
    roles_df.to_csv("Roles.csv", index=False)
    print("✅ Roles.csv created.")
else:
    raise ValueError("❌ 'job_link' or 'job_title' column missing in job_postings.csv")

# =========================
# Step 3: Create Employees.csv (limit to 200 employees)
# =========================
# ASSUMES 'HR_Analytics.csv' IS PRESENT
try:
    hr_df = pd.read_csv("HR_Analytics.csv")
except FileNotFoundError:
    print("FATAL ERROR: HR_Analytics.csv not found. Please provide this file.")
    exit()

# Ensure the required columns exist
if all(col in hr_df.columns for col in ['EmpID', 'JobRole']):
    employees_df = hr_df[['EmpID', 'JobRole']].drop_duplicates()

    # Limit to 200 employees, or take all if fewer than 200
    employees_df = employees_df.sample(n=min(200, len(employees_df)), random_state=42)

    # Assign employee IDs
    employees_df['employee_id'] = ['E' + str(i + 1) for i in range(len(employees_df))]
    employees_df.rename(columns={
        'EmpID': 'original_emp_id',
        'JobRole': 'current_role'
    }, inplace=True)

    employees_df.to_csv("Employees.csv", index=False)
    print("✅ Employees.csv created with only 200 employees.")
else:
    raise ValueError("❌ 'EmpID' or 'JobRole' column missing in HR_Analytics.csv")

# =========================
# Step 4: Create EmployeeSkills.csv
# =========================
skills_df = pd.read_csv("Skills.csv")
employee_ids = employees_df['employee_id'].tolist()
skill_ids = skills_df['skill_id'].tolist()

# Assign random skills to employees
employee_skill_records = []
for emp in employee_ids:
    assigned_skills = random.sample(skill_ids, k=random.randint(5, min(15, len(skill_ids))))
    employee_skill_records += [{'employee_id': emp, 'skill_id': skill} for skill in assigned_skills]

# Guarantee at least one employee has "Python"
python_id = skills_df[skills_df['skill_name'] == "Python"]['skill_id'].values[0]
e1 = employees_df['employee_id'].iloc[0]
if not any((rec['employee_id'] == e1 and rec['skill_id'] == python_id) for rec in employee_skill_records):
    employee_skill_records.append({'employee_id': e1, 'skill_id': python_id})

employee_skills_df = pd.DataFrame(employee_skill_records)
employee_skills_df.to_csv("EmployeeSkills.csv", index=False)
print("✅ EmployeeSkills.csv created.")

# =========================
# Step 5: Create Recommendations.csv (with matched & missing skills for IDP)
# =========================
# Reloading dataframes ensures the latest files are used if this script is run sequentially
roles_df = pd.read_csv("Roles.csv")
skills_df = pd.read_csv("Skills.csv")
employee_skills_df = pd.read_csv("EmployeeSkills.csv")
job_skills_df = pd.read_csv("job_skills.csv") # Need to reload the original file to map roles

skillname_to_id = {row['skill_name']: row['skill_id'] for _, row in skills_df.iterrows()}
id_to_skillname = {row['skill_id']: row['skill_name'] for _, row in skills_df.iterrows()}

# Preprocess job skills
job_link_to_skills = {}
for _, row in job_skills_df.iterrows():
    role_skills = [s.strip() for s in str(row['job_skills']).split(",") if s.strip()]
    if "Python" not in role_skills:
        role_skills.append("Python")
    job_link_to_skills[row['job_link']] = role_skills

recommendations = []
for i, emp in enumerate(employees_df['employee_id'], 1):
    emp_skill_ids = set(employee_skills_df[employee_skills_df['employee_id'] == emp]['skill_id'])
    emp_skills = {id_to_skillname[s] for s in emp_skill_ids}

    for _, role_row in roles_df.iterrows():
        role_id = role_row['role_id']
        job_link = role_row['role_external_link']

        role_skill_names = job_link_to_skills.get(job_link, [])
        role_skills = set(role_skill_names)

        matched = emp_skills & role_skills
        missing = role_skills - emp_skills
        match_score = len(matched)

        recommendations.append({
            'employee_id': emp,
            'role_id': role_id,
            'match_score': match_score,
            'matched_skills': ", ".join(matched),
            'missing_skills': ", ".join(missing)
        })
    if i % 20 == 0:
        print(f"Processed {i}/{len(employees_df)} employees...")

recommendations_df = pd.DataFrame(recommendations)
recommendations_df.to_csv("Recommendations.csv", index=False)
print("✅ Recommendations.csv created with matched & missing skills!")

# =========================
# Step 6: Learning Path Generator (UNIQUE FEATURE 🚀)
# =========================
skill_resources = {
    "Python": ["https://www.w3schools.com/python/", "https://www.kaggle.com/learn/python"],
    "SQL": ["https://www.sqlbolt.com/", "https://mode.com/sql-tutorial/"],
    "Machine Learning": ["https://www.coursera.org/learn/machine-learning", "https://scikit-learn.org/"],
    "Excel": ["https://exceljet.net/", "https://www.udemy.com/course/excel-for-beginners/"],
    "Tableau": ["https://public.tableau.com/en-us/s/resources", "https://www.datacamp.com/courses/tableau-fundamentals"]
    # 🔹 Add more as needed
}

recommendations_with_path = []
for _, row in recommendations_df.iterrows():
    missing = [m.strip() for m in row['missing_skills'].split(",") if m.strip()]
    roadmap = {}
    for skill in missing:
        if skill in skill_resources:
            roadmap[skill] = skill_resources[skill]
        else:
            roadmap[skill] = ["No resource found (add manually)"]

    recommendations_with_path.append({
        "employee_id": row['employee_id'],
        "role_id": row['role_id'],
        "match_score": row['match_score'],
        "learning_path": roadmap
    })

# Save as JSON for easy frontend integration
with open("LearningPaths.json", "w") as f:
    json.dump(recommendations_with_path, f, indent=4)

print("✅ Learning Paths generated for each employee-role recommendation!")

# =========================
# Step 7: Visualization (These are just for local script testing)
# =========================

# 1. Employee-Skill Heatmap
pivot_df = employee_skills_df.pivot_table(
    index='employee_id', 
    columns='skill_id', 
    aggfunc='size', 
    fill_value=0
)
# Note: The Streamlit app handles the visualization. These are just for confirming the data generation.
# plt.figure(figsize=(12,6))
# sns.heatmap(pivot_df, cmap="Blues", cbar=False)
# plt.title("Employee-Skill Matrix")
# plt.show()

# 2. Match Score Distribution
# plt.figure(figsize=(8,5))
# plt.hist(recommendations_df['match_score'], bins=20, color='skyblue', edgecolor='black')
# plt.xlabel("Match Score")
# plt.ylabel("Number of Employee-Role Pairs")
# plt.title("Distribution of Match Scores")
# plt.show()

# 3. Example: Show top recommendations + roadmap
# emp = employees_df['employee_id'].iloc[0]
# emp_recs = [rec for rec in recommendations_with_path if rec['employee_id'] == emp]
# emp_recs = sorted(emp_recs, key=lambda x: x['match_score'], reverse=True)[:3]

# print(f"\n🔎 Top Recommendations & Learning Path for {emp}:")
# for rec in emp_recs:
#     print(f"Role: {rec['role_id']} | Match Score: {rec['match_score']}")
#     for skill, resources in rec['learning_path'].items():
#         print(f"  - {skill}: {', '.join(resources)}")
