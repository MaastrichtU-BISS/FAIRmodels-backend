# FAIRmodels-backend

## Example data of model instance with multiple versions

```json
{
  "id": "1ae914cf-a5e7-47ed-bee4-395f98e03440",
  "name": "Example Model",
  "description": "Description for this example model",
  "versions": [
    {
      "version": "0.1.0",
      "onnx_model": "[hex representation of model data]",
      "metadata_id": null,
      "update_description": null,
      "created_at": "2023-08-22 16:10:00.420326"
    },
    {
      "version": "1.0.0",
      "onnx_model": "[hex representation of model data]",
      "metadata_id": null,
      "update_description": "Major update",
      "created_at": "2023-08-22 16:11:42.127031"
    },
    {
      "version": "1.1.0",
      "onnx_model": "[hex representation of model data]",
      "metadata_id": null,
      "update_description": "A minor update",
      "created_at": "2023-08-22 16:13:59.301538"
    },
    {
      "version": "1.1.1",
      "onnx_model": "[hex representation of model data]",
      "metadata_id": null,
      "update_description": "A patch",
      "created_at": "2023-08-22 16:14:06.049009"
    }
  ]
}
```

## How to run locally?

Running the server is as simple as executing the `main.py` file with python3:

```sh
python3 main.py
```

Or running with docker:

```sh
docker compose up --build
```