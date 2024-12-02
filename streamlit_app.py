import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置字体大小和样式
plt.rcParams.update({'font.size': 12})

# 数据计算函数
def calculate_energy(power, time_per_10sqm):
    return power * (time_per_10sqm / 60)

def calculate_transport_energy(weight_per_10sqm, distance_per_10sqm):
    tkm = (weight_per_10sqm / 1000) * distance_per_10sqm
    simapro_energy_per_tkm = 0.0087
    return tkm * simapro_energy_per_tkm

def calculate_commute_distance(commute_distance, workers_per_10sqm, car_ratio, public_transport_ratio):
    total_distance = commute_distance * 2 * workers_per_10sqm  # round trip
    car_distance = total_distance * car_ratio
    public_transport_distance = total_distance * public_transport_ratio
    return car_distance, public_transport_distance

def calculate_heating_energy(building_energy_standard, building_area, annual_production, area_per_10sqm):
    total_heating_energy = building_energy_standard * building_area  # GJ/year
    unit_heating_energy = total_heating_energy / annual_production  # GJ/m²
    return unit_heating_energy * area_per_10sqm

def calculate_lighting_energy(lighting_standard, building_area, annual_production, area_per_10sqm):
    total_lighting_energy = lighting_standard * building_area  # kWh/year
    unit_lighting_energy = total_lighting_energy / annual_production  # kWh/m²
    return unit_lighting_energy * area_per_10sqm

def main():
    st.title("Technosphere Inputs Management")
    st.header("Energy Consumption Calculator for Equipment")

    # Initialize session state to store equipment details
    if 'equipment_list' not in st.session_state:
        st.session_state.equipment_list = []

    # Equipment selection
    equipment_options = [
        "Lifting Machine",
        "Industrial Wood Cutting",
        "Electric Nail Gun",
        "Gantry Nailer",
        "Fixed Hoisting",
        "Forklift Transport"
    ]
    st.subheader("Add Equipment")
    selected_equipment = st.selectbox("Select Equipment:", equipment_options)

    if selected_equipment == "Forklift Transport":
        weight_per_10sqm = st.number_input("Weight per 10m² (kg):", min_value=0.0, step=0.1)
        distance_per_10sqm = st.number_input("Transport Distance per 10m² (m):", min_value=0.0, step=0.1)
        if st.button("Add Equipment", key=f"add_{selected_equipment}"):
            st.session_state.equipment_list.append({
                'name': selected_equipment,
                'weight_per_10sqm': weight_per_10sqm,
                'distance_per_10sqm': distance_per_10sqm
            })
    else:
        power = st.number_input("Power (kW):", min_value=0.0, step=0.1)
        time_per_10sqm = st.number_input("Time per 10m² (minutes):", min_value=0.0, step=0.1)
        if st.button("Add Equipment", key=f"add_{selected_equipment}"):
            st.session_state.equipment_list.append({
                'name': selected_equipment,
                'power': power,
                'time_per_10sqm': time_per_10sqm
            })

    # Display added equipment
    if st.session_state.equipment_list:
        st.subheader("Equipment List")
        total_energy = 0.0
        for idx, equipment in enumerate(st.session_state.equipment_list):
            if equipment['name'] == "Forklift Transport":
                st.text(f"{idx + 1}. {equipment['name']} - Weight: {equipment['weight_per_10sqm']} kg, Distance: {equipment['distance_per_10sqm']} m")
                energy = calculate_transport_energy(equipment['weight_per_10sqm'], equipment['distance_per_10sqm'])
                total_energy += energy
                st.text(f"  Energy Consumption for 10m²: {energy:.4f} kWh")
            else:
                st.text(f"{idx + 1}. {equipment['name']} - Power: {equipment['power']} kW, Time: {equipment['time_per_10sqm']} minutes")
                energy = calculate_energy(equipment['power'], equipment['time_per_10sqm'])
                total_energy += energy
                st.text(f"  Energy Consumption for 10m²: {energy:.2f} kWh")

        # Display total energy consumption for equipment section
        st.session_state.total_energy = total_energy
        st.subheader("Total Energy Consumption for Equipment")
        st.text(f"Total Energy: {total_energy:.2f} kWh")

    # Section for calculating commute emissions
    st.header("Commute Emission Calculator for Workers")
    commute_distance = st.number_input("Commute Distance (one way, km):", value=10.0, min_value=0.0, step=0.1)
    car_ratio = st.slider("Percentage of Workers Using Car:", min_value=0, max_value=100, value=80) / 100
    public_transport_ratio = st.slider("Percentage of Workers Using Public Transport:", min_value=0, max_value=100, value=20) / 100
    workers_per_10sqm = st.number_input("Number of Workers per 10m² (including management):", value=2.4, min_value=0.0, step=0.1)

    car_distance, public_transport_distance = calculate_commute_distance(commute_distance, workers_per_10sqm, car_ratio, public_transport_ratio)

    # Store commute distances for later use
    st.session_state.car_distance = car_distance
    st.session_state.public_transport_distance = public_transport_distance

    # Display total commute data
    st.subheader("Total Commute Data for Workers")
    st.text(f"Total Commute Distance for Workers Using Car: {car_distance:.2f} km")
    st.text(f"Total Commute Distance for Workers Using Public Transport: {public_transport_distance:.2f} km")

    # Section for calculating factory energy emissions
    st.header("Factory Energy Emission Calculator")
    building_energy_standard = st.number_input("Building Energy Standard (GJ/m²/year):", value=0.75, min_value=0.0, step=0.01)
    lighting_standard = st.number_input("Lighting Standard (kWh/m²/year):", value=18.0, min_value=0.0, step=0.1)
    building_area = st.number_input("Building Area (m²):", value=14000, min_value=0, step=1)
    annual_production = st.number_input("Annual Production (m²):", value=360000, min_value=0, step=1)
    area_per_10sqm = 10.0

    heating_energy_per_10sqm = calculate_heating_energy(building_energy_standard, building_area, annual_production, area_per_10sqm)
    lighting_energy_per_10sqm = calculate_lighting_energy(lighting_standard, building_area, annual_production, area_per_10sqm)

    # Store factory energy emissions for later use
    st.session_state.heating_energy_per_10sqm = heating_energy_per_10sqm
    st.session_state.lighting_energy_per_10sqm = lighting_energy_per_10sqm

    # Display factory energy emissions
    st.subheader("Factory Energy Emissions per 10m²")
    st.text(f"Heating Energy Consumption for 10m²: {heating_energy_per_10sqm:.4f} GJ")
    st.text(f"Lighting Energy Consumption for 10m²: {lighting_energy_per_10sqm:.4f} kWh")

    # Section for material emissions
    st.header("Material Input for Emissions Calculation")
    st.subheader("Material Inputs (per 10m²)")
    pine_wood = st.number_input("Pine Wood Material (kg):", value=0.04, min_value=0.0, step=0.01)
    pine_wood_comment = st.text_input("Pine Wood Comment:")
    adhesive = st.number_input("Adhesive (kg):", value=0.15, min_value=0.0, step=0.01)
    adhesive_comment = st.text_input("Adhesive Comment:")
    finish_coat = st.number_input("Finish Coat (kg):", value=0.17, min_value=0.0, step=0.01)
    finish_coat_comment = st.text_input("Finish Coat Comment:")
    nails = st.number_input("Iron Nails (kg):", min_value=0.0, step=0.01)
    nails_comment = st.text_input("Iron Nails Comment:")

    # Store material inputs for later use
    st.session_state.material_inputs = {
        "Pine Wood": (pine_wood, pine_wood_comment),
        "Adhesive": (adhesive, adhesive_comment),
        "Finish Coat": (finish_coat, finish_coat_comment),
        "Iron Nails": (nails, nails_comment)
    }

    # Display material inputs summary
    st.subheader("Material Inputs Summary per 10m²")
    st.text(f"Pine Wood Material: {pine_wood:.2f} kg - {pine_wood_comment}")
    st.text(f"Adhesive: {adhesive:.2f} kg - {adhesive_comment}")
    st.text(f"Finish Coat: {finish_coat:.2f} kg - {finish_coat_comment}")
    st.text(f"Iron Nails: {nails:.2f} kg - {nails_comment}")

    # Confirm button to view results
    if st.button("Confirm and View Results"):
        st.subheader("Summary of Calculations")

        # Create a summary dataframe for better visualization
        summary_data = {
            "Category": [
                "Total Equipment Energy Consumption (kWh)",
                "Total Heating Energy Consumption for 10m² (GJ)",
                "Total Lighting Energy Consumption for 10m² (kWh)",
                "Total Commute Distance for Workers Using Car (km)",
                "Total Commute Distance for Workers Using Public Transport (km)",
                "Pine Wood Material (kg)",
                "Adhesive (kg)",
                "Finish Coat (kg)",
                "Iron Nails (kg)"
            ],
            "Value": [
                round(st.session_state.total_energy, 2),
                round(st.session_state.heating_energy_per_10sqm, 4),
                round(st.session_state.lighting_energy_per_10sqm, 4),
                round(st.session_state.car_distance, 2),
                round(st.session_state.public_transport_distance, 2),
                round(st.session_state.material_inputs["Pine Wood"][0], 2),
                round(st.session_state.material_inputs["Adhesive"][0], 2),
                round(st.session_state.material_inputs["Finish Coat"][0], 2),
                round(st.session_state.material_inputs["Iron Nails"][0], 2)
            ],
            "Comment": [
                "",
                "",
                "",
                "",
                "",
                st.session_state.material_inputs["Pine Wood"][1],
                st.session_state.material_inputs["Adhesive"][1],
                st.session_state.material_inputs["Finish Coat"][1],
                st.session_state.material_inputs["Iron Nails"][1]
            ]
        }
        summary_df = pd.DataFrame(summary_data)

        # Style the summary table for better visualization
        styled_summary_df = summary_df.style.set_properties(**{
            'background-color': '#f9f9f9',
            'color': '#333333',
            'border-color': 'black',
            'border-width': '1px',
            'border-style': 'solid'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]}], overwrite=False
        ).highlight_max(axis=0, color='lightgreen').set_caption("<b>Summary of Calculations for Energy Consumption, Commute, and Materials</b>")

        st.write(styled_summary_df)

        # Data Visualizations
        st.header("Visual Representation of Results")

        # Energy Consumption Visualization
        st.subheader("Energy Consumption (kWh and GJ)")
        energy_data = {
            "Category": ["Equipment Energy (kWh)", "Heating Energy (GJ)", "Lighting Energy (kWh)"],
            "Value": [st.session_state.total_energy, st.session_state.heating_energy_per_10sqm * 277.78, st.session_state.lighting_energy_per_10sqm]  # Convert GJ to kWh
        }
        energy_df = pd.DataFrame(energy_data)

        fig1, ax1 = plt.subplots()
        sns.barplot(x="Category", y="Value", data=energy_df, ax=ax1, palette="viridis")
        ax1.set_ylabel("Energy Consumption (kWh)")
        ax1.set_title("Energy Consumption for Different Categories")
        for index, value in enumerate(energy_data['Value']):
            ax1.text(index, value + 5, f'{value:.2f}', ha='center')
        st.pyplot(fig1)

        # Commute Emissions Visualization
        st.subheader("Commute Distance by Transport Type")
        commute_data = {
            "Transport Type": ["Car", "Public Transport"],
            "Distance (km)": [st.session_state.car_distance, st.session_state.public_transport_distance]
        }
        commute_df = pd.DataFrame(commute_data)

        fig2, ax2 = plt.subplots()
        sns.barplot(x="Transport Type", y="Distance (km)", data=commute_df, ax=ax2, palette="magma")
        ax2.set_ylabel("Total Distance (km)")
        ax2.set_title("Commute Distance by Transport Type")
        for index, value in enumerate(commute_data['Distance (km)']):
            ax2.text(index, value + 2, f'{value:.2f}', ha='center')
        st.pyplot(fig2)

        # Material Inputs Visualization
        st.subheader("Material Inputs (kg)")
        material_data = {
            "Material": ["Pine Wood", "Adhesive", "Finish Coat", "Iron Nails"],
            "Quantity (kg)": [
                st.session_state.material_inputs["Pine Wood"][0],
                st.session_state.material_inputs["Adhesive"][0],
                st.session_state.material_inputs["Finish Coat"][0],
                st.session_state.material_inputs["Iron Nails"][0]
            ]
        }
        material_df = pd.DataFrame(material_data)

        fig3, ax3 = plt.subplots()
        sns.barplot(x="Material", y="Quantity (kg)", data=material_df, ax=ax3, palette="inferno")
        ax3.set_ylabel("Quantity (kg)")
        ax3.set_title("Material Inputs for 10m²")
        for index, value in enumerate(material_data['Quantity (kg)']):
            ax3.text(index, value + 0.1, f'{value:.2f}', ha='center')
        st.pyplot(fig3)

if __name__ == "__main__":
    main()
