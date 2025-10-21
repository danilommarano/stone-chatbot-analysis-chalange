from huggingface_hub import upload_folder

upload_folder(
    folder_path=".",  # raiz do seu projeto local
    repo_id="danilommarano/stone-chatbot-analysis-chalange",  # seu Space ou model repo
    repo_type="space",  # muito importante!
    commit_message="Atualização do projeto local para o Space",
)
