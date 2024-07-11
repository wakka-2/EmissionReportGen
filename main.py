import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from fpdf import FPDF

# Step 1: Get User Input

#Validating numerical input using a function with try-except logic
def input_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")

def input_float(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = float(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a float.")

def get_user_input():
    #Strip function removes leading and trailing white spaces
    company = input("Enter company name: ").strip()
    year = input_int("Enter year: ", min_value=1900, max_value=2100)
    electricity_bill = input_float("Enter monthly electricity bill (in euros): ", min_value=0)
    gas_bill = input_float("Enter monthly gas bill (in euros): ", min_value=0)
    fuel_bill = input_float("Enter monthly fuel bill for transportation (in euros): ", min_value=0)
    waste_generated = input_float("Enter monthly waste generated (in kg): ", min_value=0)
    waste_recycled = input_float("Enter waste recycled (in percentage): ", min_value=0, max_value=100)
    employee_travel = input_float("Enter employee travel per month (in km): ", min_value=0)
    fuel_efficiency = input_float("Enter fuel efficiency of the vehicles used for business travel (liters per 100 km): ", min_value=0.1)

    return {
        "Company": company,
        "Year": year,
        "Electricity_Bill": electricity_bill,
        "Gas_Bill": gas_bill,
        "Fuel_Bill": fuel_bill,
        "Waste_Generated": waste_generated,
        "Waste_Recycled": waste_recycled,
        "Employee_Travel": employee_travel,
        "Fuel_Efficiency": fuel_efficiency
    }

def collect_data():
    data = []
    #Avoiding zero number of companies and negative values
    num_companies = input_int("Enter the number of companies: ", min_value=1)
    for _ in range(num_companies):
        data.append(get_user_input())
    return pd.DataFrame(data)

# Step 2: Cauculating CO2
def analyze_data(df):
    df['Energy_CO2'] = (
        (df['Electricity_Bill'] * 12 * 0.0005) + 
        (df['Gas_Bill'] * 12 * 0.00553) + 
        (df['Fuel_Bill'] * 12 * 2.32)
    )
    df['Waste_CO2'] = df['Waste_Generated'] * 12 * (0.57 - df['Waste_Recycled'] / 100)
    df['Travel_CO2'] = df['Employee_Travel'] * 12 / (df['Fuel_Efficiency'] * 2.31)
    
    df['Total_CO2'] = df['Energy_CO2'] + df['Waste_CO2'] + df['Travel_CO2']
    
    return df

# Step 3: Visualization
def generate_visualizations(df, pdf):
    sns.set_theme(style="whitegrid")

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Carbon Footprint Analysis', fontsize=16)

    # Plot total CO2 emissions by company
    sns.barplot(ax=axes[0, 0], x="Company", y="Total_CO2", data=df)
    axes[0, 0].set_title('Total CO2 Emissions by Company')
    axes[0, 0].set_xlabel('Company')
    axes[0, 0].set_ylabel('CO2 Emissions (kg/year)')

    # Plot CO2 emissions by source
    df_melted = df.melt(id_vars=["Company", "Year"], value_vars=["Energy_CO2", "Waste_CO2", "Travel_CO2"], 
                        var_name="CO2_Source", value_name="CO2_Emissions")
    sns.barplot(ax=axes[0, 1], x="Company", y="CO2_Emissions", hue="CO2_Source", data=df_melted)
    axes[0, 1].set_title('CO2 Emissions by Source for Each Company')
    axes[0, 1].set_xlabel('Company')
    axes[0, 1].set_ylabel('CO2 Emissions (kg/year)')
    axes[0, 1].legend(title='CO2 Source')

    # Plot energy CO2 emissions
    sns.boxplot(ax=axes[1, 0], x="Company", y="Energy_CO2", data=df)
    axes[1, 0].set_title('Energy CO2 Emissions Distribution')
    axes[1, 0].set_xlabel('Company')
    axes[1, 0].set_ylabel('Energy CO2 Emissions (kg/year)')

    # Plot waste CO2 emissions
    sns.lineplot(ax=axes[1, 1], x="Year", y="Waste_CO2", hue="Company", data=df)
    axes[1, 1].set_title('Waste CO2 Emissions Over Time')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Waste CO2 Emissions (kg/year)')
    axes[1, 1].legend(title='Company')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the figure to a temporary file
    plt.savefig('visualization.png')
    plt.close()

    # Add the image to the PDF
    pdf.add_page()
    pdf.image('visualization.png', x=10, y=10, w=190)

# Step 4: Report Generation with Suggestions
# ... (existing code for generating suggestions and reports)

def generate_pdf_report(df):
    # Initialize PDF
    pdf = FPDF()
    
    # Add cover page
    pdf.add_page()
    pdf.set_font("Times", 'B', 16)
    pdf.multi_cell(0, 10, "Carbon Footprint Report", 0, 'C')
    pdf.ln(10)

    pdf.set_font("Times", size=12)

    # Add the data and suggestions to the PDF
    for index, row in df.iterrows():
        pdf.add_page()
        pdf.set_font("Times", 'B', 14)
        pdf.multi_cell(0, 10, f"Company: {row['Company']} ({row['Year']})", 0, 'L')
        pdf.ln(5)
        pdf.set_font("Times", size=12)
        pdf.multi_cell(0, 10, f"Monthly Electricity Bill: {row['Electricity_Bill']} euros", 0, 'L')
        pdf.multi_cell(0, 10, f"Monthly Gas Bill: {row['Gas_Bill']} euros", 0, 'L')
        pdf.multi_cell(0, 10, f"Monthly Fuel Bill: {row['Fuel_Bill']} euros", 0, 'L')
        pdf.multi_cell(0, 10, f"Monthly Waste Generated: {row['Waste_Generated']} kg", 0, 'L')
        pdf.multi_cell(0, 10, f"Waste Recycled: {row['Waste_Recycled']} %", 0, 'L')
        pdf.multi_cell(0, 10, f"Employee Travel: {row['Employee_Travel']} km/month", 0, 'L')
        pdf.multi_cell(0, 10, f"Fuel Efficiency: {row['Fuel_Efficiency']} liters/100 km", 0, 'L')
        pdf.multi_cell(0, 10, f"Total Estimated CO2 Emissions: {row['Total_CO2']} kg/year", 0, 'L')
        
        suggestions = generate_suggestions(row)
        if suggestions:
            pdf.ln(5)
            pdf.set_font("Times", 'B', 12)
            pdf.multi_cell(0, 10, "Suggestions to reduce CO2 emissions:", 0, 'L')
            pdf.set_font("Times", size=12)
            for suggestion in suggestions:
                pdf.multi_cell(0, 10, f"  - {suggestion}")

    # Add summary page
    pdf.add_page()
    pdf.set_font("Times", 'B', 16)
    pdf.multi_cell(0, 10, "Summary:", 0, 'L')
    pdf.ln(5)
    total_emissions = df['Total_CO2'].sum()
    pdf.multi_cell(0, 10, f"Total CO2 Emissions for all companies: {total_emissions} kg/year", 0, 'L')
    avg_emissions = df['Total_CO2'].mean()
    pdf.multi_cell(0, 10, f"Average CO2 Emissions per company: {avg_emissions} kg/year", 0, 'L')

    # Add visualizations
    generate_visualizations(df, pdf)

    # Save the PDF
    pdf_file = "carbon_footprint_report.pdf"
    pdf.output(pdf_file)

    print(f"PDF report generated successfully: {pdf_file}")

# Step 4: Report Generation with Suggestions
def generate_suggestions(row):
    suggestions = []
    
    if row['Electricity_Bill'] > 100:
        suggestions.append("Consider investing in energy-efficient appliances and lighting to reduce electricity usage.")
    
    if row['Gas_Bill'] > 50:
        suggestions.append("Explore options for better insulation and more efficient heating systems to lower gas usage.")
    
    if row['Fuel_Bill'] > 100:
        suggestions.append("Encourage carpooling or the use of public transportation to decrease fuel consumption.")
    
    if row['Waste_Generated'] > 100:
        suggestions.append("Implement waste reduction strategies and increase recycling efforts.")
    
    if row['Waste_Recycled'] < 50:
        suggestions.append("Enhance recycling programs and educate employees on proper recycling practices.")
    
    if row['Employee_Travel'] > 1000:
        suggestions.append("Promote remote work or virtual meetings to reduce the need for business travel.")
    
    if row['Fuel_Efficiency'] > 10:
        suggestions.append("Invest in more fuel-efficient vehicles or consider alternative fuel vehicles.")
    
    return suggestions


def main():
    df = collect_data()
    df = analyze_data(df)
    generate_pdf_report(df)

if __name__ == "__main__":
    main()
