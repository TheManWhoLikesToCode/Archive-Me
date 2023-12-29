import os
import shutil
from pdf_compressor import compress


def compress_pdfs(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                compressed_file_path = file_path[:-4] + '-c.pdf'
                compress(file_path, compressed_file_path, power=4)
                os.remove(file_path)


def clean_up_session_files(compress_files):
    current_dir = os.getcwd()

    # Determine the session_files_path based on the current directory
    if os.path.basename(current_dir) != 'backend':
        session_files_path = os.path.join(current_dir, 'backend', 'Session Files')
        docs_path = os.path.join(current_dir, 'backend', 'docs')
    else:
        session_files_path = os.path.join(current_dir, 'Session Files')
        docs_path = os.path.join(current_dir, 'docs')

    if compress_files:
        # Compress PDFs within the session files path
        compress_pdfs(session_files_path)

    for item in os.listdir(session_files_path):
        source_item_path = os.path.join(session_files_path, item)
        dest_item_path = os.path.join(docs_path, item)

        if os.path.isdir(source_item_path):
            if not os.path.exists(dest_item_path):
                shutil.move(source_item_path, dest_item_path)
            else:
                for sub_item in os.listdir(source_item_path):
                    source_sub_item = os.path.join(source_item_path, sub_item)
                    dest_sub_item = os.path.join(dest_item_path, sub_item)

                    if os.path.isdir(source_sub_item):
                        if not os.path.exists(dest_sub_item):
                            shutil.move(source_sub_item, dest_sub_item)
                        else:
                            shutil.rmtree(dest_sub_item)
                            shutil.move(source_sub_item, dest_sub_item)
                    elif os.path.isfile(source_sub_item) and not os.path.exists(dest_sub_item):
                        shutil.move(source_sub_item, dest_sub_item)

                # If the source directory is now empty, remove it
                if not os.listdir(source_item_path):
                    shutil.rmtree(source_item_path)

            print(f"Processed {item}")

    print("Folders merged into 'docs' successfully.")


def delete_session_files():
    current_dir = os.getcwd()

    # Check if the current directory ends with 'backend'. If not, append 'backend' to the path
    if os.path.basename(current_dir) != 'backend':
        session_files_path = os.path.join(current_dir, 'backend', 'Session Files')
    else:
        session_files_path = os.path.join(current_dir, 'Session Files')

    shutil.rmtree(session_files_path)
    print("Session files deleted successfully.")
