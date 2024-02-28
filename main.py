import os
import sys
import string
import random

from sanic import Sanic
from sanic.request import Request
from sanic.response import file, JSONResponse

from static.utils import models, Processor

if not os.path.exists("TEMP"):
    os.makedirs("TEMP")

STATIC_PATH: str = "static"

app = Sanic("BG-Remove-API")
app.static("static", "static")


@app.route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """
    BASH
        curl -X GET "<BASE_URL>" -s
    """
    return JSONResponse(
        body={
            "statusText": "Root Endpoint of BG-Remove-API",
        },
        status=200,
    )


@app.route("/clean", methods=["GET"])
async def clean(request: Request) -> JSONResponse:
    """
    BASH
        curl -X GET "<BASE_URL>/clean" -s
    """
    if len(os.listdir("TEMP")) == 0:
        return JSONResponse(
            body={
                "statusText": "Temp Directory is already Clean",
            },
            status=200,
        )

    for filename in os.listdir("TEMP"):
        os.remove(f"TEMP/{filename}")

    return JSONResponse(
        body={
            "statusText": "Cleaned Temp Directory",
        },
        status=200,
    )


@app.route("/remove/<model_type:str>", methods=["GET", "POST"], name="Background Removal")
async def remove(request: Request, model_type: str) -> JSONResponse:
    """
    BASH
        curl -X POST -L <BASE_URL>/remove/n -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/remove/n?rtype=json -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.json" -s
        curl -X POST -L <BASE_URL>/remove/lw -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/remove/lw?rtype=json -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.json" -s
    """
    rtype: str = "file"
    token: str = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    if request.method == "GET":
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if "rtype" in request.args:
            rtype = request.args.get("rtype")

        if rtype != "file" and rtype != "json":
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )

        return JSONResponse(
            body={"statusText": f"Background Removal Endpoint (Return Type : {rtype})"},
            status=200,
        )

    else:
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if request.files.get("file", None) is None:
            return JSONResponse(
                body={"statusText": "Invalid Key Specified for file Upload"},
                status=400,
            )

        if "rtype" in request.args:
            rtype = request.args.get("rtype")
        
        if rtype != "file" and rtype != "json":
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )

        image = Processor().decode_image(request.files.get("file").body)
        if model_type == "n":
            mask = await models[0].infer(image)
        else:
            mask = await models[1].infer(image)
        image = Processor.get_transparent_image(image, mask)

        if rtype == "json":
            return JSONResponse(
                body={
                    "statusText": "Background Removal Successful",
                    "transparentImageData": Processor.encode_image_to_base64(
                        image=image
                    ),
                },
                status=201,
            )
        elif rtype == "file":
            Processor.write_to_temp(image, f"TEMP/temp_{token}.png", True)
            return await file(
                location=f"TEMP/temp_{token}.png",
                status=201,
                mime_type="image/*",
            )
        else:
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )


@app.route("/replace/color/<model_type:str>", methods=["GET", "POST"], name="Background Color Replacement")
async def replace_color(request: Request, model_type: str) -> JSONResponse:
    """
    BASH
        curl -X POST -L <BASE_URL>/replace/color/n -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/lw -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/n?fill=164,5,99,255 -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/lw?fill=164,5,99,255 -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
    """
    rtype: str = "file"
    fill: str = "255,255,255,255"
    token: str = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    if request.method == "GET":
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if "rtype" in request.args:
            rtype = request.args.get("rtype")

        if "fill" in request.args:
            fill = request.args.get("fill")
        
        if rtype != "file" and rtype != "json":
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )  

        fill = fill.replace(" ", "").split(",")
        if len(fill) != 1 and len(fill) != 4:
            return JSONResponse(
                body={"statusText": "Invalid Fill Format Type"}, status=400
            )

        return JSONResponse(
            body={
                "statusText": f"Background Replacement Endpoint [Color] (Return Type : {rtype}, Color : {fill})"
            },
            status=200,
        )

    else:
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if request.files.get("file", None) is None:
            return JSONResponse(
                body={"statusText": "Invalid Key Specified for file Upload"},
                status=400,
            )

        if "rtype" in request.args:
            rtype = request.args.get("rtype")

        if "fill" in request.args:
            fill = request.args.get("fill")
        
        if rtype != "file" and rtype != "json":
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )

        fill = fill.replace(" ", "").split(",")
        if len(fill) != 1 and len(fill) != 4:
            return JSONResponse(
                body={"statusText": "Invalid Fill Format Type"}, status=400
            )

        color: tuple = ()
        if len(fill) == 1:
            color = (
                int(fill[0]) % 256,
                int(fill[0]) % 256,
                int(fill[0]) % 256,
                255
            )
        else:
            color = (
                int(fill[0]) % 256,
                int(fill[1]) % 256,
                int(fill[2]) % 256,
                int(fill[0]) % 256
            )

        image = Processor().decode_image(request.files.get("file").body)
        if model_type == "n":
            mask = await models[0].infer(image)
        else:
            mask = await models[1].infer(image)
        
        image = Processor.get_bg_color_replaced_image(image, mask, color)

        if rtype == "json":
            return JSONResponse(
                body={
                    "statusText": "Background Replacement Successful",
                    "colorReplacedImageData": Processor.encode_image_to_base64(
                        image=image, use_alpha=False
                    ),
                },
                status=201,
            )
        elif rtype == "file":
            Processor.write_to_temp(image, f"TEMP/temp_{token}.png", False)
            return await file(
                location=f"TEMP/temp_{token}.png",
                status=201,
                mime_type="image/*",
            )
        else:
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )


@app.route("/replace/image/<model_type:str>", methods=["GET", "POST"], name="Background Image Replacement")
async def replace_image(request: Request, model_type: str) -> JSONResponse:
    """
    BASH
        curl -X POST -L <BASE_URL>/replace/color/n -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/lw -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/n?fill=164,5,99,255 -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
        curl -X POST -L <BASE_URL>/replace/color/lw?fill=164,5,99,255 -F file=@"/<PATH>/<NAME>.<EXT>" -o "<PATH>/<NAME>.png" -s
    """
    rtype: str = "file"
    token: str = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    if request.method == "GET":
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if "rtype" in request.args:
            rtype = request.args.get("rtype")
        
        if rtype != "file" and rtype != "json":
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )  

        return JSONResponse(
            body={
                "statusText": f"Background Replacement Endpoint [Image] (Return Type : {rtype})"
            },
            status=200,
        )

    else:
        if model_type != "n" and model_type != "lw":
            return JSONResponse(
                body={
                    "statusText": "Invalid Model Type Specified. Only supports 'n' and 'lw'"
                },
                status=400,
            )

        if request.files.get("file1", None) is None:
            return JSONResponse(
                body={"statusText": "Invalid Key Specified for file1 Upload"},
                status=400,
            )
        
        if request.files.get("file2", None) is None:
            return JSONResponse(
                body={"statusText": "Invalid Key Specified for file2 Upload"},
                status=400,
            )

        filename_1: str = request.files.get("file1").name
        filename_2: str = request.files.get("file2").name

        image_1 = Processor.decode_image(request.files.get("file1").body)
        image_2 = Processor.decode_image(request.files.get("file2").body)

        if model_type == "n":
            mask = await models[0].infer(image=image_1)
        else:
            mask = await models[1].infer(image=image_1)
        mh, mw = mask.shape
        image_2 = Processor.preprocess_replace_bg_image(image_2, mw, mh)

        for i in range(3):
            image_1[:, :, i] = image_1[:, :, i] & mask
            image_2[:, :, i] = image_2[:, :, i] & (255 - mask)

        image_2 += image_1

        if rtype == "json":
            return JSONResponse(
                body={
                    "statusText": "Background Replacement Successful",
                    "bgreplaceImageData": Processor.encode_image_to_base64(
                        image=image_2, use_alpha=False
                    ),
                },
                status=201,
            )
        elif rtype == "file":
            Processor.write_to_temp(
                image_2,
                f"TEMP/{filename_1.split('.')[0]}_{filename_2.split('.')[0]}_{token}.png",
                False
            )
            return await file(
                location=f"TEMP/{filename_1.split('.')[0]}_{filename_2.split('.')[0]}_{token}.png",
                status=201,
                mime_type="image/*",
            )
        else:
            return JSONResponse(
                body={"statusText": "Invalid Return Type Specified"}, status=400
            )


if __name__ == "__main__":
    args_1: str = "--mode"
    args_2: str = "--port"
    args_3: str = "--workers"

    mode: str = "local-machine"
    port: int = 9090
    workers: int = 1

    if args_1 in sys.argv:
        mode = sys.argv[sys.argv.index(args_1) + 1]
    if args_2 in sys.argv:
        port = int(sys.argv[sys.argv.index(args_2) + 1])
    if args_3 in sys.argv:
        workers = int(sys.argv[sys.argv.index(args_3) + 1])

    if mode == "local-machine":
        app.run(host="localhost", port=port, dev=True, workers=workers)

    elif mode == "local":
        app.run(host="0.0.0.0", port=port, dev=True, workers=workers)

    elif mode == "render":
        app.run(host="0.0.0.0", port=port, single_process=True, access_log=True)

    elif mode == "prod":
        app.run(host="0.0.0.0", port=port, dev=False, workers=workers, access_log=True)

    else:
        raise ValueError("Invalid Mode")
