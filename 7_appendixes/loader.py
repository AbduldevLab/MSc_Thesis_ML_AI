import pandas as pd
import pyreadstat
from pathlib import Path
import json

data_files = {
    "wave1.json": "data/0053-01_TILDA_Wave1_2009-2011/0053-01_TILDA_Wave1_Data/SPSS/0053-01_TILDA_Wave1_PMF_v1.12.sav",
    "wave2.json": "data/0053-01_TILDA_Wave2_2012-2013/Data/0053-02_TILDA_Wave2_PMF_v2.7.sav",
    "wave3.json": "data/0053-01_TILDA_Wave3_2014-2015/Data/0053-04_TILDA_Wave3_PMF_v3.6.sav",
    "wave4.json": "data/0053-01_TILDA_Wave4_2016/Data/0053-05_TILDA_Wave4_PMF_v4.4.sav",
    "wave5.json": "data/0053-01_TILDA_Wave5_2018/Data/0053-06_TILDA_Wave5_PMF_v5.5.sav",
    "harmonized.json": "data/0053-06_TILDA_Harmonized_2016/Data/0053-03_TILDA_Harmonized_v1.2.dta",
}


def load_df_with_var_of_interest(
    var_dir="var_of_interest", data_files=data_files, verbose=False
):
    dfs = {}
    var_dir = Path(var_dir)

    for json_name, data_path in data_files.items():
        file = var_dir / json_name
        with open(file, "r") as f:
            vars_list = json.load(f).get("variables_of_interest")
            if verbose:
                print(f"Variables of interest from {file.name}: {vars_list[:10]} ...")

        if data_path.endswith(".sav"):
            df_full, meta = pyreadstat.read_sav(
                data_path, encoding="latin1", apply_value_formats=True
            )
            df, _ = pyreadstat.read_sav(
                data_path,
                usecols=vars_list,
                encoding="latin1",
                apply_value_formats=True,
            )
        else:
            df_full = pd.read_stata(data_path, convert_categoricals=True)
            df = pd.read_stata(data_path, convert_categoricals=True)[vars_list]

        if verbose:
            print(
                f"Data shape (Original): {df_full.shape[0]} rows x {df_full.shape[1]} columns"
            )
            print(f"Data shape (Cleaned): {df.shape[0]} rows x {df.shape[1]} columns")
            print("-----------------------------------------------")

        dfs[file.stem] = df

    return dfs


if __name__ == "__main__":
    for json_name, path_str in data_files.items():
        path = Path(path_str)
        wave_name = json_name.replace(".json", "")
        if path_str.endswith(".sav"):
            # SPSS
            df, meta = pyreadstat.read_sav(
                path, encoding="latin1", apply_value_formats=True
            )

        else:  # Stata .dta file
            df, meta = pyreadstat.read_dta(path, encoding="latin1")

        pd.DataFrame(
            {"variable": meta.column_names, "label": meta.column_labels}
        ).to_csv(Path("output") / f"{wave_name}_variable_descriptions.csv", index=False)

        print(f"--------------- wave {path} ---------------")
        print(df.shape)
        print(df.columns[:20])
        print(
            "Variable/Feature descriptions, csv file saved successfully -> dir=output/"
        )
        df.to_csv((Path("output") / f"{wave_name}.csv"), index=False)

    dfs = load_df_with_var_of_interest(verbose=True)
