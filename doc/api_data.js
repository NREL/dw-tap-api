define({ "api": [
  {
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "optional": false,
            "field": "varname1",
            "description": "<p>No type.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "varname2",
            "description": "<p>With type.</p>"
          }
        ]
      }
    },
    "type": "",
    "url": "",
    "version": "0.0.0",
    "filename": "./apidoc-template/main.js",
    "group": "/Users/dduplyak/repos/tap-endpoint/apidoc-template/main.js",
    "groupTitle": "/Users/dduplyak/repos/tap-endpoint/apidoc-template/main.js",
    "name": ""
  },
  {
    "type": "get",
    "url": "/timeseries/winddirection",
    "title": "Request winddirection estimates",
    "version": "1.0.0",
    "name": "GetWinddirection",
    "group": "Wind_Direction",
    "description": "<p>Request wind direction estimates for a particular site, for a specified height, and corresponding to the given time interval. <code>Nearest-neighbor</code> is used for both spatial and vertical interpolations.</p>",
    "sampleRequest": [
      {
        "url": "tap-api.nrel.gov/v1/timeseries/winddirection?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101"
      }
    ],
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "JSON",
            "description": "<p>JSON with <code>timestamp</code> and <code>winddirection</code> series</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Example output on success:",
          "content": "{\"timestamp\":{\"0\":\"2011-03-02 00:00:00\",\"1\":\"2011-03-02 01:00:00\",\"2\":\"2011-03-02 02:00:00\",\n\"3\":\"2011-03-02 03:00:00\",\"4\":\"2011-03-02 04:00:00\",\"5\":\"2011-03-02 05:00:00\"},\n\"winddirection\":{\"0\":188.9596252441,\"1\":183.7189788818,\"2\":193.1125793457,\"3\":184.4605865479,\"4\":200.0836181641,\"5\":215.415512085}}",
          "type": "json"
        }
      ]
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "height",
            "description": "<p>Height (in meters) for which the wind direction estimates are requested; notation: <code>XXm</code>, where XX is an integer of float</p>"
          },
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "lat",
            "description": "<p>Latitude (in degrees) for a particular site</p>"
          },
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "lon",
            "description": "<p>Longitude (in degrees) for a particular site</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "start_date",
            "description": "<p>Beginning of the time interval in the format: YYYYMMDD</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "stop_date",
            "description": "<p>End of the time interval in the format: YYYYMMDD</p>"
          }
        ]
      }
    },
    "filename": "./api.py",
    "groupTitle": "Wind_Direction"
  },
  {
    "type": "get",
    "url": "/timeseries/windspeed",
    "title": "Request windspeed estimates",
    "version": "1.0.0",
    "name": "GetWindspeed",
    "group": "Wind_Speed",
    "description": "<p>Request windspeed estimates for a particular site, for a specified height, and corresponding to the given time interval.</p>",
    "sampleRequest": [
      {
        "url": "tap-api.nrel.gov/v1/timeseries/windspeed?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101&vertical_interpolation=linear&spatial_interpolation=idw"
      }
    ],
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "JSON",
            "description": "<p>JSON with <code>timestamp</code> and <code>windspeed</code> series</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Example output on success:",
          "content": "{\"timestamp\":{\"0\":\"2011-03-02 00:00:00\",\"1\":\"2011-03-02 01:00:00\",\"2\":\"2011-03-02 02:00:00\",\n\"3\":\"2011-03-02 03:00:00\",\"4\":\"2011-03-02 04:00:00\",\"5\":\"2011-03-02 05:00:00\"},\n\"windspeed\":{\"0\":3.5925824239,\"1\":5.440796747,\"2\":4.8400592119,\"3\":5.4325136517,\"4\":4.9044365704,\"5\":5.2218727909}}",
          "type": "json"
        }
      ]
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "height",
            "description": "<p>Height (in meters) for which the windspeed estimates are requested; notation: <code>XXm</code>, where XX is an integer of float</p>"
          },
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "lat",
            "description": "<p>Latitude (in degrees) for a particular site</p>"
          },
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "lon",
            "description": "<p>Longitude (in degrees) for a particular site</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "start_date",
            "description": "<p>Beginning of the time interval in the format: YYYYMMDD</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "stop_date",
            "description": "<p>End of the time interval in the format: YYYYMMDD</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "vertical_interpolation",
            "description": "<p>Method used for vertical interpolation; allowed: <code>nearest</code>, <code>linear</code>, <code>neutral_power</code>, <code>stability_power</code></p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "spatial_interpolation",
            "description": "<p>Method used for spatial interpolation; allowed: <code>nearest</code>, <code>linear</code>, <code>cubic</code>, <code>idw</code></p>"
          }
        ]
      }
    },
    "filename": "./api.py",
    "groupTitle": "Wind_Speed"
  }
] });
