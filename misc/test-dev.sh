#!/bin/bash

curl -X GET -H "Content-Type: application/json" -d @test.json https://dw-tap-dev.stratus.nrel.gov/batch
