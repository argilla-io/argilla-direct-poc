import os
import json

from datetime import datetime

from datasets import load_dataset

from src.constants import LOCAL_CONFIG_PATH, LOCAL_DATASET_PATH


##############################################
# Get the dataset app
##############################################


def load_dataset_from_hub(dataset_name):
    # delete the existing dataset
    if os.path.exists(LOCAL_DATASET_PATH):
        os.system(f"rm -rf {LOCAL_DATASET_PATH}")
    ds = load_dataset(dataset_name)
    ds.save_to_disk(LOCAL_DATASET_PATH)
    split = load_split()
    columns = list(ds[split].features.keys())
    df = ds[split].to_pandas()
    with open(LOCAL_CONFIG_PATH, "w") as f:
        json.dump({"columns": columns, "split": split, "name": dataset_name}, f)
    return df


##############################################
# Define the dataset app
##############################################


def load_repo_id():
    with open(LOCAL_CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config["name"]


def load_dataset_dict_json(split):
    dataset_dict_fn = "dataset_info.json"
    path = os.path.join(LOCAL_DATASET_PATH, split, dataset_dict_fn)
    with open(path, "r") as f:
        return json.load(f)


def load_dataset_name():
    dataset_dict = load_dataset_dict_json("train")
    return dataset_dict["dataset_name"]


def load_argilla_dataset_name():
    name = load_dataset_name()
    now = datetime.now()
    name = f"{name}_{now.strftime('%Y%m%d%H%M%S')}"
    return name


def load_split_choices():
    dataset_dict = load_dataset_dict_json("train")
    return list(dataset_dict["splits"].keys())


def load_split():
    return load_split_choices()[0]


def load_columns():
    dataset_dict = load_dataset_dict_json("train")
    return list(dataset_dict["features"].keys())


def get_split_features(split):
    dataset_dict = load_dataset_dict_json(split)
    return dataset_dict["features"]


def get_feature_type(split, column_name):
    features = get_split_features(split)
    return features[column_name]["_type"]


def get_feature_dtype(split, column_name):
    features = get_split_features(split)
    try:
        return features[column_name]["dtype"]
    except TypeError:
        return None


def is_field(split, column_name):
    try:
        return (
            get_feature_dtype(split, column_name) == "string"
            and get_feature_type(split, column_name) == "Value"
        )
    except KeyError:
        return False


def is_label(split, column_name):
    feature_type = get_feature_type(split, column_name)
    return feature_type == "ClassLabel"


def is_float(split, column_name):
    try:
        feature_type = get_feature_type(split, column_name)
        feature_dtype = get_feature_dtype(split, column_name)
        return feature_type == "Value" and feature_dtype.startswith("float")
    except KeyError:
        return False


def is_int(split, column_name):
    try:
        feature_type = get_feature_type(split, column_name)
        feature_dtype = get_feature_dtype(split, column_name)
        return feature_type == "Value" and feature_dtype.startswith("int")
    except KeyError:
        return False


def get_feature_labels(split, column_name):
    features = get_split_features(split)
    return features[column_name]["names"]


def get_feature_values(split, column_name):
    ds = load_dataset(load_repo_id())
    return list(set(ds[split][column_name]))


def is_rating(split, column_name):
    feature_values = get_feature_values(split, column_name)
    if not is_int(split, column_name):
        return False
    if len(feature_values) > 10:
        return False
    return True


def get_field_columns():
    split = load_split()
    columns = load_columns()
    return [column for column in columns if is_field(split, column)]


def get_question_columns():
    split = load_split()
    columns = load_columns()
    return [column for column in columns if not is_field(split, column)]


def load_dataset_df():
    split = load_split()
    ds = load_dataset(load_repo_id())
    return ds[split].to_pandas()