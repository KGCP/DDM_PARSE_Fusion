import os
import hashlib
import shutil

def generate_filename_hash(filename):
    """
    Generate a hash for a filename using blake2b
    """
    hash_object = hashlib.blake2b(filename.encode(), digest_size=8)
    return hash_object.hexdigest()

def process_md_files(source_dir, output_dir):
    """
    Process all .md files in source directory and its subdirectories
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Walk through all subdirectories
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.md'):
                # Get the original filename without extension
                filename_without_ext = os.path.splitext(file)[0]

                # Generate hash for the filename
                hashed_name = generate_filename_hash(filename_without_ext)

                # Create source and destination paths
                source_path = os.path.join(root, file)
                dest_path = os.path.join(output_dir, f"{hashed_name}.md")

                # Copy the file with the new hashed name
                shutil.copy2(source_path, dest_path)
                print(f"Processed: {file} -> {hashed_name}.md")

def main():
    # Define directories
    md_file_dir = "./markdown/CS_Arxiv_MarkerOutput"
    output_dir = "./markdown"

    try:
        process_md_files(md_file_dir, output_dir)
        print("All files processed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()