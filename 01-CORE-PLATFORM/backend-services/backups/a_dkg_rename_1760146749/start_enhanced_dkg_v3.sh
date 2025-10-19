
#!/bin/bash
cd /Users/wXy/dev/Projects/aia
export DKG_V3_ENHANCED=true
export KNOWLEDGE_ATOMS_TARGET=5000
python3 -m aia.analytics.udkg_v3_intelligence_system --port 8003 --enhanced
