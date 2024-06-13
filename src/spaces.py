from huggingface_hub import duplicate_space


def create_argilla_space(target_argilla_space):
    duplicate_space(
        from_id="argilla/argilla-template-space",
        to_id=target_argilla_space,
        private=False,
        exist_ok=True,
    )
    return target_argilla_space
