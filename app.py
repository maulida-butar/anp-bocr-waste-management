import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- 1. CONSTANTS & DEFAULT DATA ---

RANDOM_INDEX = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
MERITS = ("Benefits", "Opportunities", "Costs", "Risks")
ALTERNATIVES = ("A1 - Calcium Hydroxide", "A2 - Indigenous Bacteria", "A3 - Sludge to Fertilizer")

DEFAULT_SECTOR_INTENSITIES = {
    "Metal Button": {
        "A1 - Calcium Hydroxide": {"Benefits": 0.50, "Opportunities": 0.40, "Costs": 0.60, "Risks": 0.40},
        "A2 - Indigenous Bacteria": {"Benefits": 0.80, "Opportunities": 0.70, "Costs": 0.30, "Risks": 0.20},
        "A3 - Sludge to Fertilizer": {"Benefits": 0.30, "Opportunities": 0.40, "Costs": 0.80, "Risks": 0.60},
    },
    "Automotive": {
        "A1 - Calcium Hydroxide": {"Benefits": 0.60, "Opportunities": 0.50, "Costs": 0.50, "Risks": 0.30},
        "A2 - Indigenous Bacteria": {"Benefits": 0.70, "Opportunities": 0.80, "Costs": 0.40, "Risks": 0.30},
        "A3 - Sludge to Fertilizer": {"Benefits": 0.40, "Opportunities": 0.40, "Costs": 0.70, "Risks": 0.50},
    },
    "Electronics": {
        "A1 - Calcium Hydroxide": {"Benefits": 0.80, "Opportunities": 0.70, "Costs": 0.40, "Risks": 0.20},
        "A2 - Indigenous Bacteria": {"Benefits": 0.60, "Opportunities": 0.60, "Costs": 0.50, "Risks": 0.40},
        "A3 - Sludge to Fertilizer": {"Benefits": 0.50, "Opportunities": 0.60, "Costs": 0.60, "Risks": 0.40},
    },
}

# --- 2. CORE MATH FUNCTIONS ---

def normalize(vector):
    arr = np.asarray(vector, dtype=float)
    total = float(np.sum(arr))
    return arr / total if total > 0 else arr

def ratio_matrix_from_scores(scores):
    score_arr = np.asarray(list(scores), dtype=float)
    return score_arr[:, None] / score_arr[None, :]

def eigenvector_priority(matrix):
    arr = np.asarray(matrix, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eig(arr)
    
    principal_index = int(np.argmax(eigenvalues.real))
    lambda_max = float(eigenvalues[principal_index].real)
    vector = np.abs(eigenvectors[:, principal_index].real)
    priorities = normalize(vector)
    
    n = arr.shape[0]
    ci = (lambda_max - n) / (n - 1) if n > 2 else 0.0
    ri = RANDOM_INDEX.get(n, 1.0)
    cr = ci / ri if ri != 0 else 0.0
    
    return priorities, cr

def evaluate_sector(sector_data, merit_weights):
    local_priorities = {}
    sector_crs = {}
    
    for merit in MERITS:
        scores = [sector_data[alt][merit] for alt in ALTERNATIVES]
        matrix = ratio_matrix_from_scores(scores)
        priorities, cr = eigenvector_priority(matrix)
        
        local_priorities[merit] = priorities
        sector_crs[merit] = cr
    
    eps = 1e-12
    benefit = np.maximum(local_priorities["Benefits"], eps)
    opportunity = np.maximum(local_priorities["Opportunities"], eps)
    cost = np.maximum(local_priorities["Costs"], eps)
    risk = np.maximum(local_priorities["Risks"], eps)

    # Calculate individual components for visualization
    b_component = benefit ** merit_weights[0]
    o_component = opportunity ** merit_weights[1]
    c_component = cost ** merit_weights[2]
    r_component = risk ** merit_weights[3]

    raw_multiplicative = (b_component * o_component) / (c_component * r_component)
    normalized_multiplicative = normalize(raw_multiplicative)
    
    return normalized_multiplicative, sector_crs, local_priorities

# Function to generate Excel file in memory
def to_excel(df_results, df_cr):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_results.to_excel(writer, sheet_name='Decision Matrix')
        df_cr.to_excel(writer, sheet_name='Consistency Ratios')
    processed_data = output.getvalue()
    return processed_data


# --- 3. STREAMLIT UI SETUP ---

st.set_page_config(page_title="ANP-BOCR Decision Support", layout="wide")
st.title("LCA-Informed ANP-BOCR Decision Support")

# Tooltip explanations
with st.expander("ℹ️ **Methodology & Formula Overview**"):
    st.markdown("""
    This tool employs the **Analytic Network Process (ANP)** within a **Benefits, Opportunities, Costs, and Risks (BOCR)** framework.
    
    The final strategic priority is calculated using the multiplicative BOCR synthesis formula:
    
    $$S_i = \\frac{B_i^{w_B} \\cdot O_i^{w_O}}{C_i^{w_C} \\cdot R_i^{w_R}}$$
    
    Where:
    *   $B_i, O_i, C_i, R_i$ = Local priorities for alternative *i*.
    *   $w_B, w_O, w_C, w_R$ = Global weights defined in the sidebar.
    
    *Note: Costs and Risks act as denominators; lower costs/risks lead to a higher final score.*
    """)

# --- 4. SIDEBAR: DYNAMIC BOCR WEIGHTS ---
st.sidebar.header("Global BOCR Weights")
st.sidebar.markdown("Adjust priorities to perform real-time sensitivity analysis.")

raw_b = st.sidebar.slider("Benefits Weight (wB)", 0.0, 1.0, 0.40, help="Higher weight favors strategies with strong immediate positive outcomes.")
raw_o = st.sidebar.slider("Opportunities Weight (wO)", 0.0, 1.0, 0.20, help="Higher weight favors strategies with long-term potential or indirect advantages.")
raw_c = st.sidebar.slider("Costs Weight (wC)", 0.0, 1.0, 0.10, help="Higher weight penalizes expensive strategies heavily.")
raw_r = st.sidebar.slider("Risks Weight (wR)", 0.0, 1.0, 0.30, help="Higher weight penalizes risky or uncertain strategies heavily.")

total_weight = raw_b + raw_o + raw_c + raw_r
if total_weight == 0:
    st.sidebar.error("Weights cannot all be zero!")
    st.stop()

w_b, w_o, w_c, w_r = raw_b/total_weight, raw_o/total_weight, raw_c/total_weight, raw_r/total_weight
merit_weights = np.array([w_b, w_o, w_c, w_r])

st.sidebar.markdown("### Normalized Weights Used:")
st.sidebar.code(f"B: {w_b:.2f} | O: {w_o:.2f} | C: {w_c:.2f} | R: {w_r:.2f}")

st.sidebar.divider()
st.sidebar.caption("📋 **Reproducibility Note:** Weights and sector-specific inputs are based on literature data; results are parameterized for cross-sector demonstration, not field-validated for all industries.")

# --- 5. DATA PROCESSING ---
results = {}
cr_records = {}
local_priorities_records = {}

for sector, data in DEFAULT_SECTOR_INTENSITIES.items():
    final_scores, sector_crs, local_p = evaluate_sector(data, merit_weights)
    results[sector] = final_scores
    cr_records[sector] = sector_crs
    local_priorities_records[sector] = local_p

df_results = pd.DataFrame(results, index=ALTERNATIVES)

# Dynamic Annotation Generation for Metal Button
mb_top_alt = df_results['Metal Button'].idxmax()
mb_top_score = df_results['Metal Button'].max()
dynamic_annotation = f"**Observation:** In the Metal Button sector, **{mb_top_alt}** is the dominant strategy under current weights, achieving a score of **{mb_top_score:.2f}**."

if mb_top_alt == 'A2 - Indigenous Bacteria' and (w_c > 0.5 or w_r > 0.5):
    dynamic_annotation += " Notice how A2 remains top-ranked even with heavy penalization on Costs or Risks, demonstrating extreme robustness."

st.info(dynamic_annotation)

# --- 6. VISUALIZATION: BAR CHARTS ---
st.subheader("Priority Scores & Component Analysis")

col_bar1, col_bar2 = st.columns(2)

with col_bar1:
    st.markdown("**Multiplicative Priority Scores Across Sectors**")
    fig, ax = plt.subplots(figsize=(6, 4))
    df_results.T.plot(kind="bar", ax=ax, width=0.7)
    ax.set_ylabel("Normalized Priority Score")
    ax.set_xlabel("Industrial Sector")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0)
    ax.legend(title="Strategies", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

with col_bar2:
    st.markdown("**Metal Button: Underlying Component Strengths (Unweighted)**")
    # Prepare data for stacked bar of local priorities
    mb_locals = pd.DataFrame(local_priorities_records['Metal Button'], index=ALTERNATIVES)
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    # We plot B and O as positive bars, and C and R as negative bars (burdens)
    mb_locals[['Benefits', 'Opportunities']].plot(kind='bar', stacked=True, ax=ax2, color=['#2ca02c', '#1f77b4'])
    (-mb_locals[['Costs', 'Risks']]).plot(kind='bar', stacked=True, ax=ax2, color=['#d62728', '#ff7f0e'])
    
    ax2.set_ylabel("Local Priority (B/O positive, C/R negative)")
    ax2.set_xlabel("Strategy")
    ax2.axhline(0, color='black', linewidth=1)
    plt.xticks(rotation=15, ha='right')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig2)


# --- 7. FINAL TABLES & EXPORT ---
st.divider()
col_tab1, col_tab2 = st.columns([2, 1])

with col_tab1:
    st.subheader("Final Decision Matrix")
    st.dataframe(df_results.style.highlight_max(axis=0, color='lightgreen'))
    
with col_tab2:
    st.subheader("Consistency Ratios (CR)")
    st.markdown("All matrices must have $CR < 0.10$.")
    df_cr = pd.DataFrame(cr_records)
    st.dataframe(df_cr.style.format("{:.4f}").map(lambda x: "color: red" if x >= 0.10 else "color: green"))

# Excel Export functionality
st.markdown("### Export Results")
excel_data = to_excel(df_results, df_cr)
st.download_button(
    label="📥 Download Full Report (Excel)",
    data=excel_data,
    file_name='anp_bocr_full_report.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
