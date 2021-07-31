from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
import uuid
import shutil
import os
import json

from util.zip_files import zip_files
from model.config import Config, ConfigEncoder
from model.experiment import Experiment

app = FastAPI()

folder_loc = 'experiment-data'

exp_tracker = {}
config_tracker = {}


@app.on_event("startup")
async def startup_event():
    shutil.rmtree('./' + folder_loc, ignore_errors=True)
    os.mkdir(folder_loc)


@app.put("/create-experiment")
def create_experiment(experiment: Experiment):
    if is_experiment_name_exists(experiment.name):
        raise HTTPException(status_code=400, detail="Experiment name already exists")
    id = str(uuid.uuid1())
    exp_tracker[id] = experiment
    experiment.id = id
    return experiment


@app.put("/update-experiment")
def update_experiment(experiment: Experiment):
    if not experiment.id:
        raise HTTPException(status_code=400, detail="Update should have experiment id")
    if not is_experiment_id_exists(experiment.id):
        raise HTTPException(status_code=400, detail="No experiment with the provided ID")
    if is_experiment_name_exists(experiment.name):
        raise HTTPException(status_code=400, detail="Experiment name already exists")

    exp_tracker[experiment.id] = experiment
    return experiment


@app.get("/experiments")
def get_all_experiments():
    fin = []
    for v in exp_tracker.values():
        fin.append(v)
    return {'values': fin}


@app.post("/upload-config/{exp_id}")
async def create_upload_file(exp_id: str, threshold: float,
                             weight: UploadFile = File(...), label: UploadFile = File(...)):
    if not exp_id:
        raise HTTPException(status_code=400, detail="Should have experiment id")
    if not is_experiment_id_exists(exp_id):
        raise HTTPException(status_code=400, detail="No experiment with the provided ID")

    version = 1
    if exp_id in config_tracker:
        version = len(config_tracker[exp_id]) + 1
    else:
        version = 1

    folder_name = folder_loc + '/' + exp_id + '_V' + str(version)
    os.mkdir(folder_name)
    with open(folder_name + '/' + weight.filename, "wb") as buffer:
        shutil.copyfileobj(weight.file, buffer)

    with open(folder_name + '/' + label.filename, "wb") as buffer:
        shutil.copyfileobj(label.file, buffer)

    c = Config(weight.filename, label.filename, threshold, version)
    if exp_id in config_tracker:
        config_tracker[exp_id].append(c)
    else:
        config_tracker[exp_id] = [c]

    json_string = json.dumps(c, indent=4, cls=ConfigEncoder)
    json_file = open(folder_name + '/' + 'config.json', "w")
    json_file.write(json_string)
    json_file.close()
    return {"config": c}


@app.get("/download-config/{exp_id}", response_class=FileResponse)
async def download_config_file(exp_id: str, version: int):
    if not exp_id:
        raise HTTPException(status_code=400, detail="Should have experiment id")
    if not is_experiment_id_exists(exp_id):
        raise HTTPException(status_code=400, detail="No experiment with the provided ID")
    if not version_exists(exp_id, version):
        raise HTTPException(status_code=400, detail="Provided version doesnt exist")

    c = config_tracker[exp_id][version - 1]
    return zip_files([folder_loc + '/' + exp_id + '_V' + str(version) + '/' + c.weight,
                      folder_loc + '/' + exp_id + '_V' + str(version) + '/' + c.label,
                      folder_loc + '/' + exp_id + '_V' + str(version) + '/' + 'config.json'])


def version_exists(exp_id, version):
    if exp_id in config_tracker and config_tracker[exp_id] and len(config_tracker[exp_id]) > 0:
        return 1 <= version <= len(config_tracker[exp_id])
    return False


def is_experiment_name_exists(name: str):
    for v in exp_tracker.values():
        if v.name == name:
            return True
    return False


def is_experiment_id_exists(id: str):
    return id in exp_tracker

