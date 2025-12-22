# sdx-survey

![Version](https://ons-badges-752336435892.europe-west2.run.app/api/badge/custom?left=Python&right=3.13)

Sdx-survey is a microservice that manages the processing of all survey responses from EQ-runner.
It is written in Python and deployed to Cloud Run in GCP. 

## Process

SDX-Survey reads encrypted survey submissions from a bucket after receiving a notification from pubsub.
It decrypts the submission and decides how to process it based on the survey id and the type of submission
(e.g. business, adhoc, feedback).

For business submissions a receipt is posted to RASRM
For Adhoc submissions a receipt is posted to SRM

Processing involves deciding what artifacts to create for the submission. Possible artifacts include:
- pck file (data format understood by legacy systems downstream)
- image file
- index file (used to provide metadata for the image file)
- idbr receipt
- json file

To create the artifacts sdx-survey may need to make calls to fellow sdx-service such as sdx-transformer
and sdx-image, and for some artifacts it can create them itself

Once created the artifacts are zipped up and sent to sdx-deliver.

Comments are extracted from business survey submissions and encrypted and stored in Datastore

On success sdx-survey will return a 200 code to inform an 'ack' to pubsub.
If any errors occur sdx-survey may return a non 200 status - this will be construed as a 'nack' and
pubsub will retry sending of the message. If there is no chance of success on a retry (such as because of bad data)
then a 200 will be returned instead and the submission will be left in the input bucket.

## Getting Started

### Prerequisites

- Python 3.13
- UV (a command line tool for managing Python environments)
- make

### Installing Python 3.13

If you don't have Python 3.13 installed, you can install it via brew:

```bash
brew install python@3.13
```

### Install UV:
   - This project uses UV for dependency management. Ensure it is installed on your system.
   - If UV is not installed, you can install it using:
```bash

curl -LsSf https://astral.sh/uv/install.sh | sh

OR 

brew install uv
```
- Use the official UV installation guide for other installation methods: https://docs.astral.sh/uv/getting-started/installation/
- Verify the installation by using the following command:
```bash
uv --version
```

### Install dependencies

This command will install all the dependencies required for the project, including development dependencies:

```bash
uv sync
```

If you ever need to update the dependencies, you can run:

```bash
uv sync --upgrade
```

## Running the service

```bash
uv run run.py
```

## Linting

```bash
make lint
```

## Formatting

```bash
make format
```

## Tests

```bash
make test
```

## License

Copyright © 2024, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.
