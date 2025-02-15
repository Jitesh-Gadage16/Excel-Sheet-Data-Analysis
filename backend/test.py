from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
MASTER_FILE = "uploads/master_holdings.xlsx"

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
            df_new = df_new.iloc[4:, [0, 6]].copy()  # Extract only "Share Name" & "Shares Held"
            df_new.columns = ["Share Name", "Shares Held"]
            df_new = df_new.dropna().reset_index(drop=True)

            # Add a unique column name for the new data
            new_column_name = f"Shares Held ({pd.Timestamp.now().strftime('%Y-%m-%d')})"

            # Load or create the master dataset
            if os.path.exists(MASTER_FILE):
                df_master = pd.read_excel(MASTER_FILE)
            else:
                df_master = pd.DataFrame(columns=["Share Name"])

            # Merge new data with the master dataset
            df_merged = pd.merge(df_master, df_new, on="Share Name", how="outer")
            df_merged = df_merged.rename(columns={"Shares Held": new_column_name})

            # Compute the cumulative difference
            shares_columns = [col for col in df_merged.columns if "Shares Held" in col]
            if len(shares_columns) > 1:
                df_merged["Total Change in Shares"] = df_merged[shares_columns].diff(axis=1).sum(axis=1)

            # Save the updated master file
            df_merged.to_excel(MASTER_FILE, index=False)

            return jsonify({"message": "File uploaded & merged successfully!", "updated_file": MASTER_FILE})

        except Exception as e:
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
