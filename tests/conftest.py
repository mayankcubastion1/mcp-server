import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
os.environ.setdefault("HRMS_API_BASE_URL", "https://devxnet2api.cubastion.net/api/v2")
