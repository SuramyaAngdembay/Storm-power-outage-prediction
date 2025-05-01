#!/bin/bash
#SBATCH --job-name=Power_outage_predict     # Job name
#SBATCH --output=output.txt # Output file (%j expands to jobID)
#SBATCH --error=error.txt # Error file (%j expands to jobID)
#SBATCH --partition=himem       # Partition/queue name
#SBATCH --nodes=1                        # Number of nodes
#SBATCH --mem=103G                         # Memory per node (8 GB in this example)
#SBATCH --time=140:00:00                  # Walltime (2 hour in this example)
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=20
# Execute the Python script to make a subset of the dataset

python merge.py


