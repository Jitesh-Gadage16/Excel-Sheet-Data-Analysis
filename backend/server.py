from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
MASTER_FILE = os.path.join(UPLOAD_FOLDER, "master_holdings.xlsx")

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            # Read the newly uploaded Excel file
            df_new = pd.read_excel(file_path, sheet_name="holdings")

            # Extract "Share Name", "Shares Held", and "Weight"
            df_new = df_new.iloc[4:, [0, 6, 7]].copy()
            df_new.columns = ["Share Name", "Shares Held", "Weight"]
            df_new = df_new.dropna().reset_index(drop=True)

              # **Check and convert "Weight" to float**
            df_new["Weight"] = pd.to_numeric(df_new["Weight"], errors="coerce")

            # **Sort the new file based on "Weight" in descending order (highest first)**
            df_new = df_new.sort_values(by="Weight", ascending=True)

            # Generate a new column name for "Shares Held"
            new_column_name = f"Shares Held ({pd.Timestamp.now().strftime('%Y-%m-%d')})"

            # Load or create the master dataset
            if os.path.exists(MASTER_FILE):
                df_master = pd.read_excel(MASTER_FILE)
            else:
                df_master = pd.DataFrame(columns=["Share Name"])

            # Merge the sorted new data with the master dataset
            df_merged = pd.merge(df_master, df_new.drop(columns=["Weight"]), on="Share Name", how="outer")
            df_merged = df_merged.rename(columns={"Shares Held": new_column_name})

            # Save the updated master file
            df_merged.to_excel(MASTER_FILE, index=False)

            return jsonify({"message": "File uploaded, sorted & merged by Weight!", "updated_file": MASTER_FILE})
        

        except Exception as e:
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500


@app.route("/get_master_data", methods=["GET"])
def get_master_data():
    if not os.path.exists(MASTER_FILE):
        return jsonify({"message": "No data available"}), 404

    df_master = pd.read_excel(MASTER_FILE)
    data_json = df_master.to_dict(orient="records")  # Convert DataFrame to JSON

    return jsonify({"data": data_json})  # Send JSON response

if __name__ == "__main__":
    app.run(debug=True, port=5000)
