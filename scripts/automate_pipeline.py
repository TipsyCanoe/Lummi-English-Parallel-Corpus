import subprocess

print("\n🔄 Running normalization...")
subprocess.run(['python3', 'scripts/normalize_csv.py'])

print("\n🔄 Merging normalized data into main corpus...")
subprocess.run(['python3', 'scripts/merge_corpus.py'])

print("\n✅ Pipeline completed successfully!")
