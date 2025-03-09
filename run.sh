#!/bin/bash
. "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mastolab && python bot.py
