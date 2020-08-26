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
    "group": "/Users/cphillip/Projects/dwtap/dw-tap-api/apidoc-template/main.js",
    "groupTitle": "/Users/cphillip/Projects/dwtap/dw-tap-api/apidoc-template/main.js",
    "name": ""
  },
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
    "filename": "./doc/main.js",
    "group": "/Users/cphillip/Projects/dwtap/dw-tap-api/doc/main.js",
    "groupTitle": "/Users/cphillip/Projects/dwtap/dw-tap-api/doc/main.js",
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
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "username",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "password",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "api_key",
            "description": "<p>Optional attribute of the HSDS credentials. If one of <code>username</code>, <code>password</code>, and <code>api_key</code> is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access</p>"
          }
        ]
      }
    },
    "filename": "./api.py",
    "groupTitle": "Wind_Direction"
  },
  {
    "type": "get",
    "url": "/windrose",
    "title": "Request windrose estimates",
    "version": "1.0.0",
    "name": "GetWindrose",
    "group": "Wind_Rose",
    "description": "<p>Convenience function that convolves wind direction and wind speed to create a wind rose as output.</p>",
    "sampleRequest": [
      {
        "url": "tap-api.nrel.gov/v1/windrose?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101"
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
            "description": "<p>with percentage observations in each of 8 radial segments (N, NE, E, SE, S, SW, W, NW) and each of 4 wind speed classes (11-14 mps, 8-11 mps, 5-8 mps, less than 5 mps) and all together (&quot;All&quot;)</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Example output on success:",
          "content": "{\"11-14 m/s\": [77.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5], \"8-11 m/s\": [57.5, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.0], \"5-8 m/s\": [40.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0], \"< 5 m/s\": [20.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5], \"All\": [5.0,10.0,50.0,35.0,0.0] }",
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
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "username",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "password",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "api_key",
            "description": "<p>Optional attribute of the HSDS credentials. If one of <code>username</code>, <code>password</code>, and <code>api_key</code> is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access</p>"
          }
        ]
      }
    },
    "filename": "./api.py",
    "groupTitle": "Wind_Rose"
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
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "username",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "password",
            "description": "<p>Optional attribute of the HSDS credentials</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "api_key",
            "description": "<p>Optional attribute of the HSDS credentials. If one of <code>username</code>, <code>password</code>, and <code>api_key</code> is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access</p>"
          }
        ]
      }
    },
    "filename": "./api.py",
    "groupTitle": "Wind_Speed"
  }
] });
