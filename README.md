# API Endpoint for DW-TAP Project

### Deploy as a Container (requires Docker on the host)

Build:
```shell
docker build -t tap-api:latest .
```

Run:
```shell
docker run -p 8080:80 -d tap-api:latest
```

Inside the container, flask app will run on port `80`.  On the host, you can use any available port, e.g, `8080`, like shown above.  

For a simple test (showing info about the endpoint), navigate to the following URL in your browser (running on the host):
```
http://localhost:8080
``` 

For a more comprehensive test (with HSDS connection and spatial + vertical interpolations), navigate to this URL:
```
http://localhost:8080/v1/timeseries/windspeed?height=67.00m&lat=40.7888&lon=-74.0059&start_date=20110302&stop_date=20110303&vertical_interpolation=nearest&spatial_interpolation=idw
```
This should produce a json output with `timestamp` and `windspeed` values.

For other examples of working queries, refer to the file: `dw-tap-api.postman_collection.json` (look for `raw` attributes). This file can be used by the Postman app (e.g., installed locally, on a laptop), which will cycle through all documented queries and show their status.

### Build & Run Natively (without a container)

```shell
conda env create
conda activate dw-tap-api
python api.py --development
```

### Running Modes

Notice the `--development` flag in the command above -- it makes the endpoint run on port `8080`; for short, you can run: `python api.py -d`. 

*Development* is the default mode (run if no flag is specified). In contrast, you can run the endpoint in the *Production* mode using: `python api.py --production` or `python api.py -p` -- this is what is used in the container deployment described above (to see the details, check the end of `Dockerfile`).

To see how these production and development modes are configured, refer to `config.json` and see what `host` and `port` values are specified.  
