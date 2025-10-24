# EinsteinField.ai

This project is a multi-agent coding system.

## Quickstart

To run the example notebook locally, you can use the reproducible container.

Build the container:
```bash
docker build --file Dockerfile.reproducible --tag einsteinfield/repro:latest
```

Run the container:
```bash
docker run --rm -v $PWD:/work einsteinfield/repro:latest jules validate notebooks/research/example_reproducible.ipynb
```

## Reproducing a Provenance Run

To reproduce a provenance run, use the `jules reproduce` command with the provenance ID:
```bash
jules reproduce <provenance_id> --output-dir /tmp/replay
```
