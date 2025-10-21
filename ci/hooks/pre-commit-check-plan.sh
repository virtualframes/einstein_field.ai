#!/bin/bash
set -euo pipefail
python3 ci/validate_plan.py agents/jules/PLAN.md
