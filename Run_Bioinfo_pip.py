import os
import subprocess
import logging
from datetime import datetime

# -------------------------------
# 1️⃣ Configure Dynamic Directories
# -------------------------------

# Use the user's home directory for stable, cross-platform paths
HOME = os.path.expanduser("~")

# Create a cache folder for the pipeline
BASE_PIPELINE_DIR = os.path.join(HOME, ".bio_pipeline")
os.makedirs(BASE_PIPELINE_DIR, exist_ok=True)

# Logs folder inside pipeline directory
log_dir = os.path.join(BASE_PIPELINE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(
    log_dir,
    f"pipeline_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Console handler for real-time logging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


# -------------------------------
# 2️⃣ Helper Function to Run Commands
# -------------------------------
def run_command(cmd, step_name):
    """Run shell commands with logging and error handling."""
    logging.info(f"Starting step: {step_name}")
    logging.info(f"Command: {cmd}")

    try:
        subprocess.run(cmd, shell=True, check=True)
        logging.info(f"✅ {step_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ {step_name} failed with error code {e.returncode}")
        logging.error(str(e))
        raise RuntimeError(f"{step_name} failed. See log for details.")


# -------------------------------
# 3️⃣ Trimmomatic Pipeline (Dynamic Paths)
# -------------------------------
def run_trimmomatic_pipeline(fastq_dir):
    """Run Trimmomatic on paired-end reads dynamically."""

    trim_dir = os.path.join(fastq_dir, "trimmed")
    os.makedirs(trim_dir, exist_ok=True)

    # Dynamically locate Trimmomatic
    trimmomatic_path = subprocess.getoutput("which trimmomatic")

    if not trimmomatic_path:
        raise FileNotFoundError("Trimmomatic not found in environment PATH")

    trimmomatic_jar = os.path.join(
        os.path.dirname(os.path.dirname(trimmomatic_path)),
        "share/trimmomatic/trimmomatic.jar"
    )

    adapters = os.path.join(
        os.path.dirname(trimmomatic_jar),
        "adapters",
        "TruSeq3-PE.fa"
    )

    slidingwindow = "4:20"
    minlen = "50"

    for file in os.listdir(fastq_dir):
        if file.endswith("_1.fastq"):
            sample = file.replace("_1.fastq", "")

            fwd = os.path.join(fastq_dir, f"{sample}_1.fastq")
            rev = os.path.join(fastq_dir, f"{sample}_2.fastq")

            out_fwd = os.path.join(trim_dir, f"{sample}_1_paired.fastq")
            out_fwd_unpaired = os.path.join(trim_dir, f"{sample}_1_unpaired.fastq")
            out_rev = os.path.join(trim_dir, f"{sample}_2_paired.fastq")
            out_rev_unpaired = os.path.join(trim_dir, f"{sample}_2_unpaired.fastq")

            cmd = [
                "java", "-jar", trimmomatic_jar, "PE", "-threads", "4",
                fwd, rev,
                out_fwd, out_fwd_unpaired,
                out_rev, out_rev_unpaired,
                f"ILLUMINACLIP:{adapters}:2:30:10",
                f"SLIDINGWINDOW:{slidingwindow}",
                f"MINLEN:{minlen}"
            ]

            logging.info(f"Running Trimmomatic for sample: {sample}")
            subprocess.run(cmd, check=True)
            logging.info(f"Finished trimming sample: {sample}")

    logging.info("✅ All Trimmomatic steps completed.\n")
    return trim_dir


# -------------------------------
# 4️⃣ Downstream Pipeline
# -------------------------------
def run_pipeline(trim_dir, reference_genome):

    # Collect paired trimmed FASTQ files only
    paired = sorted([f for f in os.listdir(trim_dir) if f.endswith("_paired.fastq")])

    samples = {}

    # Group files by sample name
    for f in paired:
        sample = f.replace("_1_paired.fastq","").replace("_2_paired.fastq","")
        samples.setdefault(sample, []).append(f)

    for sample, files in samples.items():
        try:
            fwd = os.path.join(trim_dir, [f for f in files if "_1_paired.fastq" in f][0])
            rev = os.path.join(trim_dir, [f for f in files if "_2_paired.fastq" in f][0])
        except IndexError:
            logging.error(f"Missing paired trimmed files for sample {sample}. Skipping.")
            continue

        output_sam = os.path.join(trim_dir, f"{sample}.sam")

        bwa_cmd = f"bwa-mem2 mem {reference_genome} {fwd} {rev} > {output_sam}"
        run_command(bwa_cmd, f"BWA alignment for sample {sample}")



# -------------------------------
# 5️⃣ Main Execution (Dynamic Paths)
# -------------------------------
if __name__ == "__main__":

    # User-configurable DATA directory under home
    DATA_DIR = os.path.join(HOME, "bio_data")
    os.makedirs(DATA_DIR, exist_ok=True)

    FASTQ_DIR = os.path.join(DATA_DIR, "fastq")
    REF_DIR = os.path.join(DATA_DIR, "reference")

    os.makedirs(FASTQ_DIR, exist_ok=True)
    os.makedirs(REF_DIR, exist_ok=True)

    # User places FASTQ and reference genome in these folders
    REF_GENOME = os.path.join(REF_DIR, "reference.fasta")

    try:
        logging.info("===================================")
        logging.info("🔬 Starting Bioinformatics Pipeline")
        logging.info("===================================")

        trim_output_dir = run_trimmomatic_pipeline(FASTQ_DIR)

        run_pipeline(
            #input_fastq=trim_output_dir,
            reference_genome=REF_GENOME,
            trim_dir=trim_output_dir
        )

        logging.info("✅ All steps completed successfully!")
        logging.info("===================================")

    except Exception as e:
        logging.critical(f"Pipeline terminated due to a critical error: {e}")
        exit(1)


