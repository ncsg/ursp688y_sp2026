import os
import glob
import requests

def geocode_csv(input_file, output_file):
    """Geocode addresses for all addresses in an input CSV file with the US Census Geocoder: https://geocoding.geo.census.gov/geocoder/

    input_file: path to csv with the following columns in this order (no header row): Unique ID, Street address, City, State, ZIP 
    
    output_file: path to save results as a CSV

    Full API documentation at https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
        
    Adapted from ChatGPT 03-mini-high queried with the following:
    "write a python script to run the following api request looping through multiple input CSV files:
    curl --form addressFile=@input.csv --form benchmark=4 https://geocoding.geo.census.gov/geocoder/locations/addressbatch --output geocoderesult.csv"
    """
    # API endpoint and benchmark value.
    url = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
    benchmark_value = "4"
    
    try:
        with open(input_file, "rb") as f:
            # Prepare the multipart/form-data payload.
            files = {"addressFile": f}
            data = {"benchmark": benchmark_value}
            
            # Send the POST request.
            response = requests.post(url, files=files, data=data)
            
        # Check if the request was successful.
        if response.status_code == 200:      
            # Write the API response content to the output file.
            with open(output_file, "wb") as out_f:
                out_f.write(response.content)
            print(f"Saved results to: {output_file}")
        else:
            print(f"Error processing {input_file}: HTTP {response.status_code}")
    except Exception as e:
        print(f"An error occurred while processing {input_file}: {e}")

def geocode_csvs(input_dir, output_dir, test=False):
    """Geocode addresses for all CSV files in a directory with the US Census Geocoder: https://geocoding.geo.census.gov/geocoder/

    CSV files must be structured with the following columns in this order (no header row): Unique ID, Street address, City, State, ZIP
    """
    
    def construct_output(input_file):
        base_name = os.path.basename(input_file)
        return os.path.join(output_dir, f"geocoderesult_{base_name}")

    # Create output directory if it doesn't exist.
    os.makedirs(output_dir, exist_ok=True)
    
    # Get a list of all CSV files in the input directory.
    csv_files = sorted(glob.glob(os.path.join(input_dir, "*.csv")))
    
    if not csv_files:
        print("No CSV files found in the input directory.")
        exit()

    if test:
        print('TEST MODE: Processing only one file.')
        csv_file = csv_files[0]
        output_file = construct_output(csv_file)
        geocode_csv(csv_files[0], output_file)
    
    else:
        for csv_file in csv_files:
            print(f"Processing file: {csv_file}")
            # Construct an output file name based on the input file name.
            output_file = construct_output(csv_file)
            # Continue to next file if output already exists
            try:
                with open(output_file, 'r') as f:
                    print(f"    Already processed")
                    continue
            except FileNotFoundError:
                geocode_csv(csv_file, output_file)
                
        print("Completed all CSVs")