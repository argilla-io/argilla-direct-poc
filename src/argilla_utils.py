import argilla_sdk as rg
from datasets import load_dataset

from datasets import load_dataset

from src.dataset import (
    load_split,
    is_label,
    is_rating,
    is_int,
    is_float,
    get_feature_values,
    get_feature_labels,
)

client = rg.Argilla(api_url="http://localhost:6900", api_key="owner.apikey")


def define_dataset_setting(
    dataset_name, field_columns, question_columns, metadata_columns, vector_columns
):
    split = load_split()

    fields, questions, metadata, vectors = [], [], [], []
    mapping = {}

    # Add field columns
    for column_name in field_columns:
        field_column_name = f"{column_name}_field"
        fields.append(rg.TextField(name=field_column_name))
        mapping[column_name] = field_column_name

    # Add question columns
    for column_name in question_columns:
        if isinstance(column_name, (list, tuple)):
            question_type, column_name = column_name
        elif is_label(split, column_name):
            question_type = "Label"
        elif is_rating(split, column_name):
            question_type = "Rating"
        else:
            question_type = "Text"

        question_column_name = f"{column_name}_question"
        if question_type == "Label":
            values = get_feature_values(split, column_name)
            titles = get_feature_labels(split, column_name)
            labels = {str(l): feature for l, feature in zip(values, titles)}
            questions.append(rg.LabelQuestion(name=question_column_name, labels=labels))
        elif question_type == "Rating":
            values = get_feature_values(split, column_name)
            questions.append(
                rg.RatingQuestion(name=question_column_name, values=values)
            )
        else:
            questions.append(rg.TextQuestion(name=question_column_name))

        if column_name in mapping:
            column_name = f"{column_name}__"
        mapping[column_name] = question_column_name

    # Add metadata columns
    if not metadata_columns:
        metadata_columns = []

    for column_name in metadata_columns:
        metadata_column_name = f"{column_name}_metadata"
        if is_int(split, column_name):
            metadata.append(rg.IntegerMetadataProperty(name=metadata_column_name))
        elif is_float(split, column_name):
            metadata.append(rg.FloatMetadataProperty(name=metadata_column_name))
        elif is_label:
            values = list(map(str, get_feature_values(split, column_name)))
            metadata.append(
                rg.TermsMetadataProperty(name=metadata_column_name, options=values)
            )
        mapping[column_name] = metadata_column_name

    # Add vector columns
    if not vector_columns:
        vector_columns = []

    for column_name in vector_columns:
        vectors.append(rg.VectorField(name=column_name))

    settings = rg.Settings(
        fields=fields, questions=questions, metadata=metadata, vectors=vectors
    )

    dataset = rg.Dataset(name=dataset_name, settings=settings, client=client)

    if not dataset.exists():
        dataset.create()

    return str(settings.serialize()), mapping


def add_records(argilla_dataset_name, mapping, n_records):
    split = load_split()
    df = load_dataset(load_repo_id())[split].take(n_records).to_pandas()
    dataset = client.datasets(argilla_dataset_name)
    questions = dataset.settings.questions
    for question in questions:
        if question.name in mapping.values():
            column_name = [k for k, v in mapping.items() if v == question.name][0]
            column_name = column_name.replace("__", "")
            if is_label(split, column_name):
                df[column_name] = df[column_name].apply(str)
    for source, target in mapping.items():
        if source.endswith("__"):
            df[source] = df[source.replace("__", "")]
    records = df.to_dict(orient="records")
    dataset.records.log(records, mapping=mapping)
    return f"{len(df)} records added with mapping {mapping}"


def delete_dataset(argilla_dataset_name):
    dataset = client.datasets(argilla_dataset_name)
    dataset.delete()
    return f"Dataset {argilla_dataset_name} deleted"
