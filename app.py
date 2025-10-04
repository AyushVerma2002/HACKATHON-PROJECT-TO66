import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber

# =========================
# Page Title & Configuration
# =========================
st.set_page_config(page_title="Employee Role Recommendation System", layout="wide")
st.title("💡 AI-powered Employee Role Recommendation System")
st.write("Upload your data and explore recommendations, skill gaps, and match scores.")

# =========================
# Load Data
# =========================
@st.cache_data
def load_data():
    # Assuming these CSVs exist in the execution environment
    employees = pd.read_csv("Employees.csv")
    roles = pd.read_csv("Roles.csv")
    recommendations = pd.read_csv("Recommendations.csv")
    employee_skills = pd.read_csv("EmployeeSkills.csv")
    skills = pd.read_csv("Skills.csv")
    return employees, roles, recommendations, employee_skills, skills

employees_df, roles_df, recommendations_df, employee_skills_df, skills_df = load_data()

# Helper for CSV download
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')

# =========================
# Sidebar Filters & Employee Profile
# =========================
st.sidebar.header("🔎 Filter Employee")
emp_list = employees_df['employee_id'].tolist()
selected_emp = st.sidebar.selectbox("Select Employee", emp_list)

st.sidebar.subheader("👤 Employee Profile")
emp_data = employees_df[employees_df['employee_id'] == selected_emp].iloc[0]

st.sidebar.markdown(f"**Employee ID:** `{emp_data['employee_id']}`")
st.sidebar.write(f"**Original EmpID:** {emp_data['original_emp_id']}")
st.sidebar.write(f"**Current Role:** {emp_data['current_role']}")

# Show employee skills
emp_skills_ids = employee_skills_df[employee_skills_df['employee_id'] == selected_emp]['skill_id'].tolist()
emp_skills = skills_df[skills_df['skill_id'].isin(emp_skills_ids)]['skill_name'].tolist()

if emp_skills:
    st.sidebar.write("**Skills:**")
    st.sidebar.write(", ".join(emp_skills[:15]))
else:
    st.sidebar.write("No skills assigned.")

# Default recommendations for the selected employee
emp_recs = recommendations_df[recommendations_df['employee_id'] == selected_emp].sort_values(
    by="match_score", ascending=False).head(5)

# =========================
# Section 1: Top Recommendations & Custom Upload
# =========================
st.header(f"📌 Top Role Recommendations for Employee {selected_emp}")

uploaded = st.file_uploader("Upload Custom Recommendations (CSV or PDF)", type=["csv", "pdf"])

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
        st.success("✅ CSV uploaded successfully!")
        st.dataframe(df.head(20))
    elif uploaded.name.endswith(".pdf"):
        pdf_text = ""
        tables = []
        try:
            with pdfplumber.open(uploaded) as pdf:
                for page in pdf.pages:
                    pdf_text += (page.extract_text() or "") + "\n"
                    table = page.extract_table()
                    if table: tables.append(table)
            st.success("✅ PDF uploaded successfully!")
            if tables:
                df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
                st.dataframe(df.head(20))
            else:
                st.text_area("Extracted Text from PDF", pdf_text, height=300)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

st.subheader("Top 5 Recommended Roles")
st.dataframe(emp_recs[['role_id', 'match_score', 'matched_skills', 'missing_skills']])

# =========================
# Section 2: Skill Gap Analysis (Enhanced with Bar Chart)
# =========================
st.header("🎯 Skill Gap Analysis")

if not emp_recs.empty:
    # Allows selection of any of the top 5 roles
    rec_role_options = {f"{row['role_id']} (Score: {row['match_score']:.2f})": idx for idx, row in emp_recs.iterrows()}
    
    selected_rec_key = st.selectbox(
        "Select Recommended Role for Skill Gap Analysis:",
        options=list(rec_role_options.keys())
    )
    
    selected_row_index = rec_role_options.get(selected_rec_key)
    top_rec = emp_recs.loc[selected_row_index] if selected_row_index is not None else emp_recs.iloc[0]

    matched_str = top_rec['matched_skills']
    missing_str = top_rec['missing_skills']
    
    # Clean split for skills
    matched = matched_str.split(", ") if pd.notna(matched_str) and matched_str else []
    missing = missing_str.split(", ") if pd.notna(missing_str) and missing_str else []

    n_matched = len(matched)
    n_missing = len(missing)
    n_total = n_matched + n_missing
    
    if n_total > 0:
        # --- Create Eye-Catching Bar Chart ---
        role_name = roles_df[roles_df['role_id'] == top_rec['role_id']]['role_name'].iloc[0] if not roles_df[roles_df['role_id'] == top_rec['role_id']].empty else top_rec['role_id']
        
        st.subheader(f"Required Skills Breakdown for Role: {role_name}")
        st.markdown(f"**Match Score:** `{top_rec['match_score']:.2f}` (Total Required Skills: **{n_total}**)")

        fig, ax = plt.subplots(figsize=(10, 2.5))
        
        # Plot Matched Skills (Green)
        ax.barh('Skills', n_matched, color='#4CAF50', height=0.6, label=f'Matched ({n_matched})')
        
        # Plot Missing Skills (Red), stacked on Matched
        ax.barh('Skills', n_missing, left=n_matched, color='#F44336', height=0.6, label=f'Missing ({n_missing})')

        # Formatting
        ax.set_xlim(0, n_total)
        ax.set_xticks(range(0, n_total + 1, max(1, n_total // 5))) # Dynamic ticks
        ax.set_yticklabels([]) # Hide y-axis label
        ax.tick_params(axis='x', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), ncol=2, frameon=False)
        
        st.pyplot(fig)
        
        # Display skills in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### ✅ Matched Skills")
            if matched:
                st.markdown("- " + "\n- ".join(matched))
            else:
                st.write("No matched skills.")
                
        with col2:
            st.markdown("##### ❌ Missing Skills")
            if missing:
                st.markdown("- " + "\n- ".join(missing))
            else:
                st.write("No missing skills.")
    else:
        st.info(f"No skill data available for role {top_rec['role_id']}.")


# =========================
# Section 3: Match Score Distribution (Enhanced)
# =========================
st.header("📊 Match Score Distribution (Overall & Employee Context)")

fig, ax = plt.subplots(figsize=(10, 5))

# Plot overall distribution
sns.histplot(recommendations_df['match_score'], bins=20, kde=True, ax=ax, color='#2196F3', edgecolor='black', alpha=0.6)

# Highlight the current employee's scores with vertical lines
emp_scores = emp_recs['match_score'].tolist()
for score in emp_scores:
    ax.axvline(score, color='#FF5722', linestyle='--', linewidth=2) # Orange highlight

ax.set_xlabel("Match Score", fontsize=12)
ax.set_ylabel("Number of Employee-Role Pairs", fontsize=12)
ax.set_title("Distribution of Match Scores Across All Pairs (Employee Scores Highlighted)", fontsize=14)

# Create a manual legend since ax.axvline doesn't automatically combine labels well
legend_elements = [
    plt.Line2D([0], [0], color='#2196F3', lw=4, label='Overall Distribution', alpha=0.6),
    plt.Line2D([0], [0], color='#FF5722', linestyle='--', lw=2, label=f'{selected_emp} Top Scores')
]
ax.legend(handles=legend_elements)

st.pyplot(fig)

# =========================
# Section 4: Employee-Skill Matrix (Interactive - High Contrast)
# =========================
st.header("✨ Employee-Skill Matrix (Interactive - High Contrast)")

# --- Prepare data for heatmap ---
skill_map = skills_df.set_index('skill_id')['skill_name'].to_dict()
all_skill_names = sorted(skill_map.values())
all_employee_ids = employees_df['employee_id'].tolist()

pivot_df = employee_skills_df.pivot_table(
    index='employee_id',
    columns='skill_id',
    aggfunc='size',
    fill_value=0
)
pivot_df.columns = pivot_df.columns.map(lambda x: skill_map.get(x, x))
pivot_df = pivot_df.fillna(0) 

# --- Interactive Filters ---
col_heatmap_1, col_heatmap_2 = st.columns(2)

with col_heatmap_1:
    selected_employees = st.multiselect(
        "Select Employees to View:",
        options=all_employee_ids,
        default=[selected_emp] # Default to the currently selected employee
    )

with col_heatmap_2:
    # FIX: Change default selection to the skills the selected employee actually has, 
    # ensuring some cells show '1' if the employee has any skills.
    selected_skills = st.multiselect(
        "Select Skills to Track:",
        options=all_skill_names,
        default=emp_skills[:10] # Default to first 10 skills of the selected employee
    )

# --- Apply Filters ---
if selected_employees and selected_skills:
    
    # Filter by selected employees
    pivot_df_filtered = pivot_df.loc[pivot_df.index.intersection(selected_employees)]
    
    # Filter by selected skills
    skill_cols_to_use = [s for s in selected_skills if s in pivot_df_filtered.columns]
    
    if skill_cols_to_use:
        pivot_df_filtered = pivot_df_filtered[skill_cols_to_use]
        
        # --- Generate Eye-Catching Heatmap ---
        fig_width = max(8, len(skill_cols_to_use) * 1.5)
        fig_height = max(5, len(selected_employees) * 0.5)
        
        plt.figure(figsize=(fig_width, fig_height))
        
        # Use 'magma' for vibrant contrast, and annot=True for direct visibility
        sns.heatmap(
            pivot_df_filtered, 
            cmap="magma", # Changed to vibrant magma colormap
            vmin=0, 
            vmax=1, 
            annot=True, # Show 0/1 in cells
            fmt='g', # Format as general number
            annot_kws={"size": 10, "color": "white"}, # Annotate in white for contrast
            cbar_kws={'label': 'Skill Presence (1=Yes, 0=No)', 'ticks': [0.1, 0.9]}, # Adjust ticks for clarity
            linewidths=0.5, 
            linecolor='lightgray',
            yticklabels=True
        )
        
        plt.title("Employee-Skill Matrix (High-Contrast View)", fontsize=16)
        plt.ylabel("Employee ID", fontsize=12)
        plt.xlabel("Skill Name", fontsize=12)
        plt.yticks(rotation=0)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(plt.gcf())
    else:
        st.warning("Please select at least one valid skill to generate the heatmap.")
else:
    st.info("Select employees and skills above to generate the interactive matrix.")


# =========================
# Section 5: Download Recommendations
# =========================
st.header("⬇️ Download Data")

recs_csv = convert_df_to_csv(recommendations_df)

st.download_button(
    "Download All Recommendations Data (CSV)",
    data=recs_csv,
    file_name="All_Recommendations_Data.csv",
    mime="text/csv"
)
st.download_button(
    f"Download {selected_emp}'s Top Recommendations (CSV)",
    data=convert_df_to_csv(emp_recs),
    file_name=f"{selected_emp}_Top_Recommendations.csv",
    mime="text/csv"
)
