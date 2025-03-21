# Set environment variables
export NATS_URL=$1
unset VIRTUAL_ENV

echo "Building java tests..."

make

echo "Starting server..."

mvn verify
