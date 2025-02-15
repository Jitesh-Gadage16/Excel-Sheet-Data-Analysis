import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import psycopg2

# ===================== 1. PROCESS EXCEL FILE =====================
def process_holdings_file(input_file):
    """
    Extracts 'Share Name' and 'Shares Held' columns from the provided Excel file.
    
    Parameters:
    - input_file: Path to the uploaded Excel file.
    
    Returns:
    - A cleaned DataFrame with relevant data.
    """
    try:
        # Load the Excel file
        xls = pd.ExcelFile(input_file)
        df = pd.read_excel(xls, sheet_name="holdings")

        # Extract relevant data starting from row 4 onwards
        df_cleaned = df.iloc[4:, [0, 6]].copy()

        # Rename columns for clarity
        df_cleaned.columns = ["Share Name", "Shares Held"]

        # Drop any rows with missing values
        df_cleaned = df_cleaned.dropna().reset_index(drop=True)

        print("✅ Data extracted successfully!")
        return df_cleaned
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None


# ===================== 2. STORE DATA IN FIREBASE =====================
def store_data_in_firestore(df):
    """
    Stores extracted stock data into Firestore.
    
    Parameters:
    - df: DataFrame with 'Share Name' and 'Shares Held'.
    """
    try:
        # Load Firebase credentials
        cred = credentials.Certificate("firebase-key.json")  
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        for _, row in df.iterrows():
            db.collection("holdings_data").add({
                "Share Name": row["Share Name"],
                "Shares Held": int(row["Shares Held"])
            })

        print("✅ Data successfully stored in Firebase Firestore!")
    except Exception as e:
        print(f"❌ Error storing data in Firestore: {e}")


# ===================== 3. STORE DATA IN POSTGRESQL =====================
# def store_data_in_postgres(df):
#     """
#     Stores extracted stock data into PostgreSQL.
    
#     Parameters:
#     - df: DataFrame with 'Share Name' and 'Shares Held'.
#     """
#     try:
       
#         DB_HOST = "your_host_here"  # e.g., "localhost" or "batyr.db.elephantsql.com"
#         DB_NAME = "stock_data"
#         DB_USER = "your_username"
#         DB_PASSWORD = "your_password"

#         conn = psycopg2.connect(
#             host=DB_HOST,
#             dbname=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD
#         )
#         cursor = conn.cursor()

#         # Insert data into PostgreSQL
#         for _, row in df.iterrows():
#             cursor.execute(
#                 "INSERT INTO holdings (share_name, shares_held) VALUES (%s, %s)",
#                 (row["Share Name"], int(row["Shares Held"]))
#             )

#         # Commit changes and close connection
#         conn.commit()
#         cursor.close()
#         conn.close()

#         print("✅ Data successfully stored in PostgreSQL!")
#     except Exception as e:
#         print(f"❌ Error storing data in PostgreSQL: {e}")


# ===================== 4. RUN THE SCRIPT =====================
if __name__ == "__main__":
    input_file = "holdings-daily-us-en-mdy.xlsx"  # Ensure the file is in the project directory

    # Extract data from Excel
    df_cleaned = process_holdings_file(input_file)

    if df_cleaned is not None:
        # Choose where to store the data (Uncomment the one you want to use)
        store_data_in_firestore(df_cleaned)  # Store in Firebase Firestore
        # store_data_in_postgres(df_cleaned)  # Store in PostgreSQL
