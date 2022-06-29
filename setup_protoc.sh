// setting up protoc
export protoc=`pwd`/protoc/bin/
apt-get install protobuf-compiler
cd models/research && protoc object_detection/protos/*.proto --python_out=. && cp object_detection/packages/tf2/setup.py . && python -m pip install . 
pip install protobuf matplotlib==3.2
pip uninstall opencv-python-headless -y
pip install opencv-python==4.5.1.48
pip install tensorflow --upgrade