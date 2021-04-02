#!/bin/sh
set -e

# Run mongo express
echo "Attempt to start Mongo Express Server..."
exec node ../../start_mongo_express
