import gradio as gr

from src import argilla_utils
from src import dataset
from src import spaces



def refresh_dataset_settings_view(
    columns,
    question_columns,
    field_columns,
    split,
    settings,
    dataset_name,
    argilla_dataset_name,
    mapping,
):
    """This is a utility function to refresh the gradio applications state variables when a new dataset is loaded."""
    columns = dataset.load_columns()
    field_columns = dataset.get_field_columns()
    question_columns = dataset.get_question_columns()
    metadata_columns = []
    vector_columns = []
    split = dataset.load_split()
    settings = None
    dataset_name = dataset.load_dataset_name()
    argilla_dataset_name = dataset.load_argilla_dataset_name()
    mapping = None
    return (
        columns,
        field_columns,
        question_columns,
        metadata_columns,
        vector_columns,
        split,
        settings,
        dataset_name,
        argilla_dataset_name,
        mapping,
    )


with gr.Blocks() as app:
    ##############################################
    # Define the app state
    ##############################################

    columns = gr.State(dataset.load_columns)
    question_columns = gr.State(dataset.get_question_columns)
    field_columns = gr.State(dataset.get_field_columns)
    split = gr.State(dataset.load_split)
    settings = gr.State(None)
    dataset_name = gr.State(dataset.load_dataset_name)
    argilla_dataset_name = gr.State(dataset.load_argilla_dataset_name)
    mapping = gr.State(None)

    state_variables = [
        columns,
        question_columns,
        field_columns,
        split,
        settings,
        dataset_name,
        argilla_dataset_name,
        mapping,
    ]

    ##############################################
    # Define the app dataset and argilla space
    ##############################################

    gr.Markdown(
        """# 🚂 Argilla Direct
        A direct connection from a Hub dataset to an Argilla dataset.
        This app allows you to create an Argilla dataset from a Hugging Face dataset. 
        You will need to load a dataset from the Hugging Face Hub, create an Argilla space, 
        define the dataset's settings, and add records to the dataset.
        """
    )

    with gr.Group():
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        dataset_name_input = gr.Textbox(
                            label="Dataset Repo ID", value=dataset.load_dataset_name()
                        )
                    with gr.Column():
                        split_input = gr.Dropdown(
                            label="Dataset Split",
                            choices=dataset.load_split_choices(),
                            allow_custom_value=True,
                            value=dataset.load_split(),
                        )
                    load_dataset_btn = gr.Button(value="1️⃣ Load Dataset")
            with gr.Column():
                argilla_space_name = gr.Textbox(
                    label="Argilla Space Name", value=f"{dataset_name.value}_argilla"
                )

                create_argilla_space_btn = gr.Button(value="2️⃣ Create Argilla Space")

    ##############################################
    # Define the Argilla dataset configuration
    ##############################################

    gr.Markdown(
        """## 3️⃣ Define Argilla Dataset
        Define the settings for the Argilla dataset including fields, questions, metadata, and vectors.
        Select the columns from the Hugging Face dataset to be used as Argilla dataset attributes.
        """
    )

    with gr.Row():
        with gr.Group():
            with gr.Column():
                # DATASET SETTINGS

                # Argilla dataset name
                argilla_dataset_name_view = gr.Textbox(
                    label="Dataset Name",
                    info="The name of the dataset in Argilla to be created or used",
                    value=dataset.load_argilla_dataset_name(),
                )
                argilla_dataset_name_view.change(
                    fn=lambda value: gr.update(
                        value=dataset.load_argilla_dataset_name()
                    ),
                    inputs=[argilla_dataset_name_view],
                    outputs=[argilla_dataset_name_view],
                )

                # Field columns
                field_columns_view = gr.Dropdown(
                    label="Field Columns",
                    info="Columns to be used as fields in the Argilla dataset",
                    choices=dataset.load_columns(),
                    multiselect=True,
                    value=dataset.get_field_columns(),
                    allow_custom_value=True,
                )
                field_columns_view.change(
                    fn=lambda value: gr.update(choices=dataset.load_columns()),
                    inputs=[field_columns_view],
                    outputs=[field_columns_view],
                )

                # Question columns
                question_columns_view = gr.Dropdown(
                    label="Question Columns",
                    info="Columns to be used as question suggestions in the Argilla dataset",
                    choices=dataset.load_columns(),
                    multiselect=True,
                    value=dataset.get_field_columns(),
                    allow_custom_value=True,
                )

                question_columns_view.change(
                    fn=lambda value: gr.update(choices=dataset.load_columns()),
                    inputs=[question_columns_view],
                    outputs=[question_columns_view],
                )

                with gr.Accordion(label="Define New Questions", open=False):
                    with gr.Group():
                        with gr.Column():
                            question_type = gr.Dropdown(
                                label="Question Type",
                                info="The type of question to be added to the Argilla dataset",
                                choices=["Text", "Label", "Rating"],
                            )
                        with gr.Column():
                            question_name = gr.Textbox(
                                label="Question Name",
                                info="The name of the question to be added to the Argilla dataset",
                            )
                        with gr.Column():
                            gr.Button(value="Add Question").click(
                                fn=lambda type, name, questions: questions
                                + [(type, name)],
                                inputs=[
                                    question_type,
                                    question_name,
                                    question_columns_view,
                                ],
                                outputs=[question_columns_view],
                            )

                with gr.Accordion(label="Define Metadata and Vectors", open=False):
                    metadata_columns_view = gr.Dropdown(
                        label="Metadata Columns",
                        info="Columns to be used as metadata in the Argilla dataset",
                        choices=dataset.load_columns(),
                        multiselect=True,
                    )
                    vector_columns_view = gr.Dropdown(
                        label="Vector Columns",
                        info="Columns to be used as vectors in the Argilla dataset",
                        choices=dataset.load_columns(),
                        multiselect=True,
                    )

                n_records = gr.Slider(1, 10000, 100, label="Number of Records")
                create_argilla_dataset_btn = gr.Button(value="Create Argilla Dataset")
                add_records_btn = gr.Button(value="Add Records to Argilla")
                delete_dataset_btn = gr.Button(value="Delete Argilla Dataset")

        with gr.Column():
            dataset_view = gr.Dataframe(
                label="Dataset Viewer",
                column_widths="20%",
                headers=columns.value,
                wrap=True,
            )
            records_view = gr.Text(label="Status", value="")

    ##############################################
    # Define the app logic
    ##############################################

    load_dataset_btn.click(
        fn=dataset.load_dataset_from_hub,
        inputs=[dataset_name_input],
        outputs=[dataset_view],
    ).then(
        fn=refresh_dataset_settings_view,
        inputs=state_variables,
        outputs=[
            columns,
            question_columns_view,
            field_columns_view,
            split_input,
            settings,
            dataset_name,
            argilla_dataset_name_view,
            mapping,
        ],
    )

    create_argilla_space_btn.click(
        fn=spaces.create_argilla_space,
        inputs=[argilla_space_name],
        outputs=[records_view],
    )

    delete_dataset_btn.click(
        fn=argilla_utils.delete_dataset,
        inputs=[argilla_dataset_name_view],
        outputs=[records_view],
    )

    create_argilla_dataset_btn.click(
        fn=argilla_utils.define_dataset_setting,
        inputs=[
            argilla_dataset_name_view,
            field_columns_view,
            question_columns_view,
            metadata_columns_view,
            vector_columns_view,
        ],
        outputs=[records_view, mapping],
    )

    add_records_btn.click(
        fn=argilla_utils.add_records,
        inputs=[argilla_dataset_name_view, mapping, n_records],
        outputs=[records_view],
    )


if __name__ == "__main__":
    app.launch()
