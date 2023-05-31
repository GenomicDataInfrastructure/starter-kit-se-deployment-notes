#!/bin/bash

curl --request POST \
	--url http://localhost:8010/v1/tasks \
	--header 'Accept: application/json' \
	--header 'Authorization: Bearer eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyN' \
	--header 'Content-Type: application/json' \
	--data '{
  "description": "Demonstrates handling single http file input. Will output some nice looking JSON to stdout.",
  "inputs": [
    {
      "url": "htsget://bearer:<UserToken>@htsget.gdi.nbis.se/reads/s3/https:/gdi.nbis.se/datasets/gdi000000003/c5773f41d17d27bd53b1e6794aedc32d7906e779_elixir-europe.org/gdi-heilsa/v9RYU2.g.vcf.gz", 
      "path": "/tes/volumes/input",
      "type": "FILE"
    }
  ],
  "executors": [
    {
      "image": "alpine",
      "command": [
        "md5sum",
        "/tes/volumes/input"
      ]
    }
  ]
}'
