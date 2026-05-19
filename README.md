# Ancient Vision Backend Server

## Installation:
Prerequisites:

MacOS 26
Homebrew [Install](https://brew.sh)

uv [Install](https://docs.astral.sh/uv/getting-started/installation/)

### Install prerequisites:
`uv install python3.11 --default`. <-- Warning! This will overwrite the default python distribution! 
`brew install wget` <-- Installs `wget`

Install MySQL
`brew install --cask firefox`

Create a `artifactdb` schema

Run the script `create_3dartifacts.sql` in the artifactdb schema

Then, run `uv run app.py` in the repository root directory


## API Usage
If you want to interface directly with the scanner, you can create your own script and add `import ancientvisionapi as api` to use the API

For example; `api.scan()` to scan an artifact with the scanner

### Known issues
Colmap fuction is being deprecated in favor of Apple's new ObjectCapture API, as it is 20 times faster and just as accurate!

Scan request timeouts and dynamic IP addresses cause instability when scanning

Loading bar time estimate for scanning is ~2 seconds off