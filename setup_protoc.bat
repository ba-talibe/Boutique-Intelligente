// setting up protoc
copy protoc\bin\protoc.exe C:\Windows\system32
cd models\research\ && protoc object_detection/protos/*.proto --python_out=. && copy object_detection\packages\tf2\setup.py setup.py && python setup.py build && python setup.py install
cd slim && pip install -e .

pip install protobuf matplotlib==3.2
pip uninstall opencv-python-headless -y
pip install opencv-python==4.5.1.48
pip install tensorflow --upgrade