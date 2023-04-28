import sys
import zipfile
from multiprocessing import Pool
from tqdm import tqdm

def extract_files(args):
    file_path, extract_path, file_indices = args
    extracted_files = 0
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file_index in file_indices:
            file_name = zip_file.namelist()[file_index]
            zip_file.extract(file_name, path=extract_path)
            extracted_files += 1
    return extracted_files

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <file_path> <extract_path>')
        sys.exit(1)

    file_path = sys.argv[1]
    extract_path = sys.argv[2]

    with zipfile.ZipFile(file_path, 'r') as zip_file:
        # Get the number of files in the zip archive
        num_files = len(zip_file.namelist())

    with Pool() as pool:
        # Determine the number of CPUs available
        num_cpus = pool._processes

        # Calculate the number of files that each process will handle
        files_per_process = num_files // num_cpus

        # Calculate the remainder (i.e., the number of files that are not evenly divisible by the number of CPUs)
        remainder = num_files % num_cpus

        # Split the file indices into sublists, one for each process
        file_indices = [range(i * files_per_process + min(i, remainder), (i + 1) * files_per_process + min(i + 1, remainder)) for i in range(num_cpus)]

        # Create a list of tuples containing file path, extract path, and file indices
        files_to_extract = [(file_path, extract_path, indices) for indices in file_indices]

        # Use imap_unordered to apply the extract_files function to each tuple in the list, with a progress bar
        with tqdm(total=num_files, desc='Extracting') as pbar:
            for extracted_files in pool.imap_unordered(extract_files, files_to_extract):
                pbar.update(extracted_files)
