# Simple Chat app

### Create and activate environment

```shell
python -m venv venv
source venv/bin/activate
```

### Install requirements

```shell
pip install -r requirements.txt
```

### Create and run migrations

```shell
alembic revision --autogenerate -m 'init'
alembic upgrade head
```

