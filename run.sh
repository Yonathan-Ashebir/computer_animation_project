#!/bin/bash
source .venv/bin/activate
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT