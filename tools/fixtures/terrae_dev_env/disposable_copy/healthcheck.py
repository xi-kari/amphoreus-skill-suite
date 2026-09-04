from pathlib import Path
required = ['README.md', 'runtime.txt', 'requirements.lock', 'healthcheck.py']
missing = [name for name in required if not Path(name).is_file()]
print('TERRAE_FIXTURE_HEALTH=' + ('PASS' if not missing else 'FAIL'))
print('MISSING=' + ','.join(missing))
raise SystemExit(0 if not missing else 1)
