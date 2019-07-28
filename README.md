# LFS-events

Tool transforms program of Letní filmová škola Uherské Hradiště (https://program.lfs.cz/?&alldates=1) to CSV file. You can import CSV file into your google calendar.

## Result

![Google calendar](https://github.com/brabemi/LFS-events/blob/master/lfs.png "Google calendar")

## Setup
 
### Virtual environment
```
python3 -m venv venv
. venv/bin/activate
```

### Install requirements
```
python -m pip install -r requirements.txt
```
## Run

```
python lfs.py 
```
Creates CSV file event.csv
