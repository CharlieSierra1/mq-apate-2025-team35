import pandas as pd

def extract_top25(input_file="./25432108/Assassin.csv", output_file="Assassin_top25.csv"):
    # Read the CSV
    df = pd.read_csv(input_file)

    # Take top 25 rows
    top25 = df.head(100)

    # Save to new CSV
    top25.to_csv(output_file, index=False)

    print(f"Top 25 rows saved to {output_file}")

if __name__ == "__main__":
    extract_top25()
