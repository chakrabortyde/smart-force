import os, shutil
d = "./chromadb"
if os.path.exists(d):
    shutil.rmtree(d)
    print("Removed", d)
else:
    print("No chromadb directory found.")
