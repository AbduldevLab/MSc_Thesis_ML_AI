import pandas as pd
import pyreadstat
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
# =TEXTJOIN(", ", TRUE, J2:Jxxx) - Excel formula for number of xxx rows from manual filtering to create var of interest with comma
data_files = {
    "wave1.json": BASE_DIR / "data/0053-01_TILDA_Wave1_2009-2011/0053-01_TILDA_Wave1_Data/SPSS/0053-01_TILDA_Wave1_PMF_v1.12.sav",
    "wave2.json": BASE_DIR / "data/0053-01_TILDA_Wave2_2012-2013/Data/0053-02_TILDA_Wave2_PMF_v2.7.sav",
    "wave3.json": BASE_DIR / "data/0053-01_TILDA_Wave3_2014-2015/Data/0053-04_TILDA_Wave3_PMF_v3.6.sav",
    "wave4.json": BASE_DIR / "data/0053-01_TILDA_Wave4_2016/Data/0053-05_TILDA_Wave4_PMF_v4.4.sav",
    "wave5.json": BASE_DIR / "data/0053-01_TILDA_Wave5_2018/Data/0053-06_TILDA_Wave5_PMF_v5.5.sav",
    "harmonized.json": BASE_DIR / "data/0053-06_TILDA_Harmonized_2016/Data/0053-03_TILDA_Harmonized_v1.2.dta",
}

def load_df_with_var_of_interest(var_dir="var_of_interest", data_files=data_files, verbose=False):
    dfs = {}
    var_dir = BASE_DIR / var_dir

    for json_name, data_path in data_files.items():
        json_file = var_dir / json_name

        with open(json_file, "r") as f:
            vars_list = json.load(f).get("variables_of_interest", [])

        vars_list = [str(v) for v in vars_list]
        if verbose:
            print(f"Variables of interest from {json_file.name}: {vars_list[:10]} ...")
        
        # ---------- SPSS ----------
        if data_path.suffix == ".sav":
            # metadata only (fast, avoids encoding errors)
            _, meta = pyreadstat.read_sav(data_path, metadataonly=True, encoding="latin1")
            original_rows = meta.number_rows
            original_cols = len(meta.column_names)

            # load only needed variables (fast)
            df, _ = pyreadstat.read_sav(
                data_path,
                usecols=vars_list,
                encoding="latin1",
                apply_value_formats=True,
            )

        # ---------- STATA ----------
        elif data_path.suffix == ".dta":
            df_full = pd.read_stata(data_path, convert_categoricals=True)
            original_rows, original_cols = df_full.shape
            existing_vars = [v for v in vars_list if v in df_full.columns]
            df = df_full[existing_vars]

        else:
            raise ValueError(f"Unsupported file type: {data_path.suffix}")

        # --- filter variables ---
        existing_vars = df.columns.tolist()
        missing_vars = sorted(set(vars_list) - set(existing_vars))
        if missing_vars:
            print(f"Missing variables in {data_path.name}: {missing_vars}")

        # ---------- Verbose print ----------
        if verbose:
            print(f"Data shape (Original): {original_rows} rows x {original_cols} columns")
            print(f"Data shape (Cleaned): {df.shape[0]} rows x {df.shape[1]} columns")
            print("-----------------------------------------------")

        dfs[json_name.replace(".json", "")] = df

    return dfs

if __name__ == "__main__":

    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    for json_name, path in data_files.items():
        wave_name = json_name.replace(".json", "")

        if path.suffix == ".sav":
            df, meta = pyreadstat.read_sav(path, encoding="latin1", apply_value_formats=True)
        else:
            df, meta = pyreadstat.read_dta(path, encoding="latin1")

        pd.DataFrame({
            "variable": meta.column_names,
            "label": meta.column_labels
        }).to_csv(output_dir / f"{wave_name}_variable_descriptions.csv", index=False)

        print(f"--------------- wave {path} ---------------")
        print(df.shape)
        print(df.columns[:20])
        print("Variable descriptions, csv file saved successfully -> dir=output/")

        df.to_csv(output_dir / f"{wave_name}.csv", index=False)

    dfs = load_df_with_var_of_interest(verbose=True)
