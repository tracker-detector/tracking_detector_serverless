from fastapi import FastAPI, Request, HTTPException
import threading
from lib.model import get_all_available_models

app = FastAPI()


@app.get("/train/models")
def get_models():
    respone = {"status": 200, "data": []}
    for model in get_all_available_models():
        respone["data"].append(
            {
                "name": model.model_name,
                "desc": model.model_desc,
                "input_dims": model.input_dims,
            }
        )
    return respone


@app.post("/train/models/{model_name}/run/{data_name}")
async def train_model(request: Request, model_name: str, data_name: str):
    json_body = await request.json()
    batch_size = json_body.get("batchSize", 512)
    epochs = json_body.get("epochs", 10)
    for model in get_all_available_models():
        if model.model_name == model_name:
            thread = threading.Thread(
                target=model.train, args=(data_name, batch_size, epochs)
            )
            thread.start()
            return {
                "status": 200,
                "message": f"Training for model '{model_name}' with the dataset '{data_name}' started.",
            }
    raise HTTPException(
        status_code=404,
        detail={"status": 404, "message": f"The mode '{model_name}' does not exists."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
