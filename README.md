# sync-async-test

Fiddling around with `asyncio` and `gunicorn` WSGI worker.

## INSTALL GUIDE

<details>
<summary>Create Python virtual environment</summary>

- For `Python 3` installation, consult the following [link](https://www.python.org/downloads/)

Once done, open a new terminal in the directory `sync-async-test` and type the following command to create the python virtual environment.

```sh
python -m venv .venv
```

In the same terminal, activate the `.venv` previously created as follow, or as shown in [HowTo](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments), and install the project's dependencies.

- **Windows**

```sh
.venv\Scripts\activate
pip install -U -r requirements.txt
```

- **Unix** or **MacOS**

```sh
source .venv/bin/activate
pip install -U -r requirements.txt
```
</details>

## RUN GUIDE

You may want to run the following processes in a separated shell prompt.

### WSGI

Run the WSGI with the following command.

```sh
gunicorn fastap_server:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### ASYNCHRONOUS CLIENTS

Run the asynchronous clients with the following command.

```sh
python3 async_clients.py
```