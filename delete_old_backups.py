import os
import datetime
import logging
import argparse
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_backup_files(backup_dir: str) -> List[Tuple[str, datetime.datetime]]:
    """Scan backup directory and return list of backup files with creation dates."""
    backup_files = []
    for root, _, files in os.walk(backup_dir):
        for file in files:
            if file.endswith('.bak'):  # Assuming .bak extension for backup files
                file_path = os.path.join(root, file)
                creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                backup_files.append((file_path, creation_time))
    return backup_files

def identify_old_backups(backup_files: List[Tuple[str, datetime.datetime]], age_threshold: int) -> List[str]:
    """Identify backups that are older than the age threshold."""
    current_time = datetime.datetime.now()
    old_backups = [
        file_path for file_path, creation_time in backup_files
        if (current_time - creation_time).days > age_threshold
    ]
    return old_backups

def delete_backups(backups_to_delete: List[str], dry_run: bool = False) -> None:
    """Delete the specified backup files."""
    for file_path in backups_to_delete:
        if dry_run:
            logging.info(f"Would delete: {file_path}")
        else:
            try:
                os.remove(file_path)
                logging.info(f"Deleted: {file_path}")
            except OSError as e:
                logging.error(f"Error deleting {file_path}: {e}")

def generate_report(deleted_backups: List[str], remaining_backups: List[Tuple[str, datetime.datetime]]) -> None:
    """Generate a report of the deletion operation."""
    logging.info("--- Deletion Report ---")
    logging.info(f"Number of backups deleted: {len(deleted_backups)}")
    logging.info(f"Total size of deleted backups: {sum(os.path.getsize(f) for f in deleted_backups) / (1024*1024):.2f} MB")
    logging.info(f"Number of remaining backups: {len(remaining_backups)}")
    logging.info(f"Oldest remaining backup: {min(creation_time for _, creation_time in remaining_backups)}")
    logging.info(f"Newest remaining backup: {max(creation_time for _, creation_time in remaining_backups)}")

def main(backup_dir: str, age_threshold: int, dry_run: bool) -> None:
    logging.info(f"Starting backup cleanup process for {backup_dir}")
    logging.info(f"Age threshold: {age_threshold} days")
    logging.info(f"Dry run: {dry_run}")

    all_backups = get_backup_files(backup_dir)
    logging.info(f"Total backups found: {len(all_backups)}")

    old_backups = identify_old_backups(all_backups, age_threshold)
    logging.info(f"Backups identified for deletion: {len(old_backups)}")

    delete_backups(old_backups, dry_run)

    remaining_backups = [b for b in all_backups if b[0] not in old_backups]
    generate_report(old_backups, remaining_backups)

    logging.info("Backup cleanup process completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete old backup files.")
    parser.add_argument("backup_dir", help="Directory containing backup files")
    parser.add_argument("--age", type=int, default=30, help="Age threshold in days (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actually deleting files")
    args = parser.parse_args()

    main(args.backup_dir, args.age, args.dry_run)