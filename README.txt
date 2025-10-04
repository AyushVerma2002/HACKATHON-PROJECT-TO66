--- AI-powered Employee Role Recommendation System ---

Hackathon Project — Match employees to ideal roles using skill gap analysis, visualizations, and personalized learning paths.

# Overview

In today dynamic workforce, aligning employee skills with appropriate roles is crucial for both individual growth and organizational success. Our AI-powered system recommends suitable job roles for employees by analyzing their current skills and comparing them with job requirements.

Key Features:

🧠 Intelligent role recommendations

📉 Skill gap analysis with visual insights

🔥 Personalized learning path generation

📊 Match score distribution tracking

🗺️ Interactive employee-skill matrix

📎 PDF/CSV upload support for custom data

🧾 One-click download for reports

📁 Project Structure
.
├── app.py                     # Streamlit frontend app
├── generate_data.py          # Script to generate all datasets
├── Skills.csv                # List of all unique skills
├── Roles.csv                 # All job roles
├── Employees.csv             # Sampled employee dataset
├── EmployeeSkills.csv        # Mapping of employee → skill
├── Recommendations.csv       # Recommendations with skill matches
├── LearningPaths.json        # Personalized upskilling paths
├── job_skills.csv            # Source: job roles and required skills
├── job_postings.csv          # Source: job links and titles
├── HR_Analytics.csv          # Source: employee info and job roles

🧪 How It Works
🔹 Data Preparation (Run before using the app)

Use generate_data.py to auto-create required CSVs.

1. Skills

Extracted from job_skills.csv, cleaned and deduplicated into Skills.csv.

2. Roles

Parsed from job_postings.csv, mapped with role IDs and job links.

3. Employees

Sampled (up to 200) from HR_Analytics.csv. Assigned internal employee IDs.

4. EmployeeSkills

Randomly assigns 5 - 15 skills to each employee. Ensures at least one employee has "Python".

5. Recommendations

For every employee-role pair:

Computes match_score

Identifies matched_skills and missing_skills

6. Learning Paths (⭐ Unique Hackathon Feature!)

Auto-generates personalized upskilling resources for missing skills using curated links. Output saved as LearningPaths.json.

📊 Streamlit Dashboard (app.py)

Launch a full-featured web app to explore the system.

streamlit run app.py

🖥️ Sections in the App
1. Employee Filter + Profile

Select any employee

View current role and skills

2. Top Role Recommendations

See top 5 matching roles with scores

Upload custom CSV/PDF to test custom recommendations

3. Skill Gap Analysis

Bar chart showing matched vs missing skills

Lists of both categories

4. Match Score Distribution

Histogram of all match scores

Orange lines highlight selected employee's score

5. Employee-Skill Matrix

Heatmap for selected employees and skills

High-contrast with annotations

6. Download Reports

Full recommendation dataset

Individual employee's top recommendations

📚 Sample Learning Path Output
{
  "employee_id": "E1",
  "role_id": "R12",
  "match_score": 4,
  "learning_path": {
    "SQL": [
      "https://www.sqlbolt.com/",
      "https://mode.com/sql-tutorial/"
    ],
    "Machine Learning": [
      "https://www.coursera.org/learn/machine-learning",
      "https://scikit-learn.org/"
    ]
  }
}

🛠️ How to Run the Full Pipeline

Place your source files:

HR_Analytics.csv

job_skills.csv

job_postings.csv

Run the script:

python generate_data.py


Launch the Streamlit app:

streamlit run app.py

🌟 Highlights

🔁 Fully dynamic — refreshes recommendations on skill change

🔓 Open-ended — add custom learning resources easily

📂 Works with real datasets & custom uploads

🎨 Eye-catching charts (Seaborn + Matplotlib)

🧑‍💻 Technologies Used

Python

Pandas, Matplotlib, Seaborn

Streamlit

PDFPlumber (for PDF parsing)

JSON (for upskilling paths)

📦 Future Enhancements

✅ Integrate real-time skill update tracking

🧠 Add ML model for smarter recommendations

📊 Include proficiency levels per skill

🔗 Direct LMS integration for one-click learning

🤝 Team & Acknowledgements

Built for [Hackathon Name] by a team passionate about:

Talent development

AI & data science

Practical HR tech innovation

Thanks to open-source contributors and dataset providers.
