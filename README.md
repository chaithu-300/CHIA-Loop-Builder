# CHIA Loop-Builder Assistant

AI-powered system that generates executable CHIA loop configurations from plain-English hardware optimization objectives.

## Quick Start

### Installation
```bash
git clone https://github.com/YOUR-USERNAME/CHIA-Loop-Builder.git
cd CHIA-Loop-Builder
pip install -r requirements.txt
```

### Setup
```bash
# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### Run
```bash
uvicorn src.api.main:app --reload
# Open browser: http://127.0.0.1:8000/docs
```

## Results

Three case studies executed on ChampSim:

| Config | Workload | IPC | MPKI |
|--------|----------|-----|------|
| 1 | 429.mcf-184B | 0.09394 | 26.73 |
| 2 | 458.sjeng-1088B | 1.033 | 31.22 |
| 3 | 602.gcc-s-1850B | 0.2662 | 19.85 |

See `paper/` for full results.

## Files

- `src/` — RAG system code
- `data/` — CHIA documentation
- `results/` — Generated configs & execution logs
- `paper/` — 4-page A³ Workshop paper

## Team
B. Chaithanya (Student, Karnataka, India)
Aditya sivaji permulla 
Tamilarsi K
Thrisha KV
