from attrition_mlops.definitions import defs

runs = [
    {"descripcion": "run 1 - exploración rápida",   "n_trials": 10},
    {"descripcion": "run 2 - optimización media",   "n_trials": 30},
    {"descripcion": "run 3 - optimización completa","n_trials": 50},
]

for i, run_config in enumerate(runs):
    print(f"\nLanzando {run_config['descripcion']} ({run_config['n_trials']} trials)...")
    job = defs.resolve_job_def("full_pipeline_job")
    result = job.execute_in_process()
    if result.success:
        print(f"✅ Run {i+1} completado")
    else:
        print(f"❌ Run {i+1} falló")