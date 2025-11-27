# Secodary_Analysis_pipeline 
🧬 QC & Alignment Pipeline
Overview

This repository provides a simple bioinformatics pipeline for performing read quality control (Trimmomatic) and sequence alignment (BWA-MEM2) with integrated logging and error handling.

⚙️ Features

✅ Quality Control: Runs Trimmomatic
 to assess sequencing read quality

🧩 Read Alignment: Uses BWA-MEM2
 for efficient alignment to a reference genome

🧠 Structured Logging: All pipeline events (start, success, failure) are recorded to timestamped log files

🚨 Robust Error Handling: Captures and reports failures with informative messages

📁 Organized Outputs: Stores results and logs in structured directories for easy downstream processing

🧰 Requirements

Ensure the following tools and libraries are installed in your environment of choice i.e. conda or docker;

System Tools

Trimmomatic

bwa-mem2

python >= 3.8

Python Packages
pip install -r requirements.txt


Typical requirements.txt:

logging


(Note: The built-in logging module is part of the Python standard library, so no installation is required.)



🚀 Usage

To run the pipeline:

python pipeline.py


By default, the script will:

Run FastQC on the input FASTQ file

Align reads using BWA-MEM2

Store all results in the output/ directory

Save logs in the logs/ directory

🧩 Example Command Flow

The following steps are executed internally:

Step	Description	Tool	Output
1	Perform quality control	Trimmomatic	output/Trimmomatic_report.html
2	Align reads to reference	BWA-MEM2	output/aligned_reads.sam
🪶 Logging & Error Handling

All major steps are logged with timestamps and severity levels (INFO, ERROR, CRITICAL).

On failure, the pipeline halts gracefully and records the error in logs/.

Example log excerpt:

2025-11-10 14:53:20,134 - INFO - Starting step: Quality Control (Trimmomatic)
2025-11-10 14:53:28,482 - INFO - ✅ Quality Control (Trimmomatic) completed successfully.
2025-11-10 14:53:29,119 - ERROR - ❌ Read Alignment (BWA-MEM2) failed with error code 1.

🧱 Extending the Pipeline

You can easily extend this pipeline to include:

Variant calling (GATK / FreeBayes)

Expression quantification (STARsolo)

Visualization and summary reporting

Just add new steps to the run_pipeline() function and use the same run_command() helper for logging and error control.

📜 License

This project is open-source and distributed under the MIT License
.

👨🏽‍🔬 Author

Developed by Kwame Papa
Bioinformatics Enthusiast | Research Pipeline Developer | Genomics Innovation Advocate
