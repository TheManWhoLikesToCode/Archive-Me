import os
import shutil
from pdf_compressor import compress

def clean_up_files():
    excluded_folders = ['src', 'docs', 'support', '.vscode', '.git']

    # Compress PDFs
    for root, dirs, files in os.walk('.'):
        # Exclude specified folders
        dirs[:] = [d for d in dirs if d not in excluded_folders]
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                compressed_file_path = file_path[:-4] + '-c.pdf'
                compress(file_path, compressed_file_path, power=4)
                os.remove(file_path)

    for item in os.listdir():
        if os.path.isdir(item) and item not in excluded_folders:
            source_path = item
            dest_path = os.path.join('docs', item)

            if not os.path.exists(dest_path):
                shutil.move(source_path, dest_path)
            else:
                for sub_item in os.listdir(source_path):
                    source_sub_item = os.path.join(source_path, sub_item)
                    dest_sub_item = os.path.join(dest_path, sub_item)

                    if os.path.isdir(source_sub_item):
                        if not os.path.exists(dest_sub_item):
                            shutil.move(source_sub_item, dest_sub_item)
                        else:
                            # Remove existing directory before moving
                            shutil.rmtree(dest_sub_item)
                            shutil.move(source_sub_item, dest_sub_item)
                    elif os.path.isfile(source_sub_item) and not os.path.exists(dest_sub_item):
                        shutil.move(source_sub_item, dest_sub_item)

                if not os.listdir(source_path):  # Check if directory is now empty
                    shutil.rmtree(source_path)  # Safe to remove

            print(f"Processed {item}")

    print("Folders merged into 'docs' successfully.")

    if os.path.exists('downloaded_content.zip'):
        os.remove('downloaded_content.zip')

    # Delete remaining folders
    for folder in os.listdir():
        if os.path.isdir(folder) and folder not in excluded_folders:
            shutil.rmtree(folder)

    print("Remaining folders deleted.")

    print("Clean-up completed.")
