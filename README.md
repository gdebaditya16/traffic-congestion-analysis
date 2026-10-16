# traffic-congestion-analysis
GPS-based traffic congestion analysis using Python
## Dataset and Setup

This project uses the Porto Taxi Trajectory dataset from the UCI Machine Learning Repository.

**Dataset download:** https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015

### Instructions to Run the Project

1. Clone this repository:
   bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   cd traffic-congestion-analysis
   

2. Install the required Python libraries:
   bash
   python -m pip install -r requirements.txt
   

3. Download the original dataset from the UCI Machine Learning Repository and extract it.

4. Place the original `train.csv` file in the project's `data/` directory.

5. Run the data preprocessing script to generate the cleaned GPS segment data:
   bash
   python build_clean_segments.py
   

6. Run any additional analysis scripts required to generate the CSV files used by the dashboard.

7. Start the dashboard:
   bash
   python -m streamlit run app.py
   

### Note

The original dataset and generated CSV files are not included in this GitHub repository to avoid storing large data files. Users must download the dataset and generate the required processed files locally before running the dashboard.