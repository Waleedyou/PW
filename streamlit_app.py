import streamlit as st
import pandas as pd
import base64
import io
from datetime import datetime
import requests
from io import BytesIO
import openpyxl

# Inflation rates
inflation_rates = {
    2019: 1.8,
    2020: 1.2,
    2021: 1.8,
    2022: 6.5,
    2023: 4.1,
    2024: 3.1,
}

# Decorator to cache downloaded files
@st.cache_data()
def download_file(url):
    response = requests.get(url)
    return BytesIO(response.content)

# Decorator to cache data loading and preparation
@st.cache_data()
def load_and_prepare_data(file_info):
    dataframes = {}
    for group, url, num_sites, year in file_info:
        excel_io = download_file(url)
        df = pd.read_excel(excel_io)
        if 'Item' in df.columns and 'Units' in df.columns:
            df.set_index('Item', inplace=True)
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64'] and col != 'Units':
                    df[col] = df[col].apply(lambda x: adjust_for_inflation(x, year))
        dataframes[group] = (df, num_sites)
    return dataframes

# Adjust for inflation function
@st.cache_data()
def adjust_for_inflation(amount, from_year, to_year=datetime.now().year):
    if from_year == to_year:
        return amount
    inflation_factor = 1
    if from_year < to_year:
        for year in range(from_year, to_year):
            inflation_factor *= 1 + inflation_rates.get(year, 0) / 100
    else:
        for year in range(to_year, from_year, -1):
            inflation_factor /= 1 + inflation_rates.get(year - 1, 0) / 100
    return amount * inflation_factor

# Compare costs function
@st.cache_data()
def compare_costs(dataframes, column_type="Unit Price"):
    comparison_results = pd.DataFrame()
    for filename, (df, _) in dataframes.items():
        relevant_columns = [col for col in df.columns if column_type in col and col != 'Units']
        for column in relevant_columns:
            comparison_results[f'{filename} - {column}'] = df[column]
        if 'Units' in df.columns:
            comparison_results[f'{filename} - Units'] = df['Units']
    return comparison_results

# Safe convert to float function
@st.cache_data()
def safe_convert_to_float(value):
    try:
        return float(value.replace('$', '').replace(',', ''))
    except ValueError:
        return None

# Perform cost analysis function
@st.cache_data()
def perform_cost_analysis(comparison_df, project_counts, selected_item):
    analysis_summary = {}
    item_data = comparison_df.loc[[selected_item]]
    numeric_data = item_data.select_dtypes(include=[float, int])
    if not numeric_data.empty:
        adjusted_costs = {}
        for column in numeric_data.columns:
            project_count = project_counts.get(column.split(" - ")[0], 1)
            unit_type = comparison_df.loc[selected_item, f"{column.split(' - ')[0]} - Units"]
            if unit_type == "LS":
                adjusted_costs[column] = numeric_data[column] / project_count
            elif unit_type in ["EA", "SF", "LF"]:
                adjusted_costs[column] = numeric_data[column]
            else:
                adjusted_costs[column] = numeric_data[column] * project_count
        adjusted_df = pd.DataFrame(adjusted_costs)
        lowest_cost = adjusted_df.min().min()
        highest_cost = adjusted_df.max().max()
        average_cost = adjusted_df.mean().mean()
        analysis_summary[selected_item] = {
            'Units': comparison_df.loc[selected_item, comparison_df.columns.str.contains('- Units')].iloc[0],
            'Lowest Cost': f"${lowest_cost:.2f}",
            'Highest Cost': f"${highest_cost:.2f}",
            'Average Cost': f"${average_cost:.2f}",
        }
    else:
        analysis_summary[selected_item] = {
            'Units': "N/A",
            'Lowest Cost': "N/A",
            'Highest Cost': "N/A",
            'Average Cost': "N/A",
        }
    return analysis_summary

# Export to Excel function
@st.cache_data()
def export_to_excel(cost_analysis, filename, estimated_costs, third_person_sites, selected_item):
    summary_df = pd.DataFrame.from_dict(cost_analysis, orient='index').reset_index().rename(columns={'index': 'Item'})
    estimated_costs_df = pd.DataFrame({
        'Item': [f'Estimated Costs for {third_person_sites} sites ({selected_item})'],
        'Lowest Cost': [f'${estimated_costs[0]:.2f}'],
        'Highest Cost': [f'${estimated_costs[1]:.2f}'],
        'Average Cost': [f'${estimated_costs[2]:.2f}'],
        'Units': [cost_analysis[selected_item]['Units']]
    })
    summary_df = pd.concat([summary_df, estimated_costs_df], ignore_index=True)
    excel_bytes_io = io.BytesIO()
    with pd.ExcelWriter(excel_bytes_io, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Cost Analysis", index=False)
    return excel_bytes_io.getvalue()

# Main app function
def main():
    st.title("Construction cost tool - Project delivery group")
    file_info = [
        ("Group C",
         "https://www.dropbox.com/scl/fi/d66774vj4qrwnywmh6njb/Group-C.xlsx?dl=1&rlkey=f4tkvvx1zvzguqmo7yfspvpxf", 14,
         2022),
        ("Group D",
         "https://www.dropbox.com/scl/fi/4ek2pm7gcvtbcygap1jja/Group-D.xlsx?dl=1&rlkey=rv86x5fbhk7kr2n3cmd96u1i2", 11,
         2022),
        ("Group E",
         "https://www.dropbox.com/scl/fi/mgy696s4mb73dok3qjyav/Group-E.xlsx?dl=1&rlkey=vnr922cc30p07vkaanexbf9yu", 7,
         2023),
        ("Group F",
         "https://www.dropbox.com/scl/fi/7wcxa245a7y93b3ih1kvv/Group-F.xlsx?dl=1&rlkey=axsgio64xuvgsk4cdjfifbfnh", 7,
         2023),
        ("Group G",
         "https://www.dropbox.com/scl/fi/wxx4koi1e880a15wrdd0i/Group-G.xlsx?dl=1&rlkey=w5z8wh85ncc5yijq291p90vac", 7,
         2024),
        ("Group H",
         "https://www.dropbox.com/scl/fi/0ytw64w5hliaeo6quxz3s/Group-H.xlsx?dl=1&rlkey=np616vwahrly24i8f5szpcw7m", 11,
         2024),
        ("Group I",
         "https://www.dropbox.com/scl/fi/v6nkaax417lfyyxjc0urh/Group-I.xlsx?dl=1&rlkey=tunv48mloyl4bg7m6631lwn0s", 8,
         2024)
    ]

    # Load data from Dropbox links
    dataframes = load_and_prepare_data(file_info)

    # UI for selecting items for analysis
    all_items = set()
    for df, _ in dataframes.values():
        all_items.update(df.index.tolist())

    selected_item = st.selectbox("Select an item for analysis", options=sorted(list(all_items)))

    # UI for displaying cost analysis
    project_counts = {}
    for filename, (_, num_sites) in dataframes.items():
        project_counts[filename] = num_sites

    comparison_df = compare_costs(dataframes, "Unit Price")
    cost_analysis = perform_cost_analysis(comparison_df, project_counts, selected_item)
    st.write(f"Cost Analysis Results for {selected_item}:")
    displayed_df = pd.DataFrame.from_dict(cost_analysis, orient='index').reset_index().rename(columns={'index': 'Item'})
    st.dataframe(displayed_df)

    # Additional UI components for estimating future costs
    third_person_sites = st.number_input("Enter the number of sites for the new project", min_value=1, value=1)
    future_year = st.number_input("Enter a future year for cost projection", min_value=datetime.now().year,
                                  max_value=2050, value=datetime.now().year + 1)
    quantity = st.number_input("Enter the quantity for the cost projection", min_value=1, value=1, key='quantity')

    if selected_item in cost_analysis:
        item_analysis = cost_analysis[selected_item]
        lowest_cost_per_site = safe_convert_to_float(item_analysis['Lowest Cost'])
        highest_cost_per_site = safe_convert_to_float(item_analysis['Highest Cost'])
        average_cost_per_site = safe_convert_to_float(item_analysis['Average Cost'])

        future_costs = [adjust_for_inflation(cost * third_person_sites * quantity, datetime.now().year, future_year) for
                        cost in [lowest_cost_per_site, highest_cost_per_site, average_cost_per_site] if
                        cost is not None]
        st.markdown(
            f"**Projected total costs for {future_year}** (Lowest, Highest, Average): `${future_costs[0]:.2f}`, `${future_costs[1]:.2f}`, `${future_costs[2]:.2f}`")

        excel_data = export_to_excel(cost_analysis, "cost_analysis.xlsx", future_costs, third_person_sites,
                                     selected_item)
        st.download_button(label="Download Excel file", data=excel_data, file_name="cost_analysis.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    # Background style
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("https://www.tripsavvy.com/thmb/JsEg4Eew-1-1UdNOnY_HDPA8P98=/2121x1414/filters:fill(auto,1)/GettyImages-513714245-3a40f1e3b5bf4de88289009ffed82933.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

    main()
