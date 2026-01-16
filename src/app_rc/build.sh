mv ./archive/*.py ./app/

mpy-cross ./app/control.py
mpy-cross ./app/parser.py
mpy-cross ./app/microdot.py

mv ./app/control.py ./archive/
mv ./app/parser.py ./archive/
mv ./app/microdot.py ./archive/
