#!/bin/bash

curl -X GET -H "Content-Type: application/json" -d @test.json localhost:8080/batch
