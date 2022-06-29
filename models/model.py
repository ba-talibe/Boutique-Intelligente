import os
import sys
import cv2 
import numpy as np
from tensorflow.compat.v2.train import Checkpoint
from tensorflow import convert_to_tensor, float32, function
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt




class Model:
    def __init__(self, checkpoint_path, config_file, label_map_file) -> None:
        self.configs = config_util.get_configs_from_pipeline_file(config_file)
        self.detection_model = model_builder.build(model_config=self.configs['model'], is_training=False)
        self.category_index = label_map_util.create_category_index_from_labelmap(label_map_file)
        # Restore checkpoint
        #self.checkpoints = tf.compat.v2.train.Checkpoint(model=self.detection_model)
        self.checkpoints = Checkpoint(model=self.detection_model)
        self.checkpoints.restore(os.path.join(checkpoint_path, 'ckpt-3')).expect_partial()

    #@tf.function
    @function
    def detect_fn(self, image):
        image, shapes = self.detection_model.preprocess(image)
        prediction_dict = self.detection_model.predict(image, shapes)
        return self.detection_model.postprocess(prediction_dict, shapes)
        
    def get_predictions(self, image, display=False):
        baseDir = os.path.dirname(image)
        img = cv2.imread(image)
        image_np = np.array(img)
        print("image path : ", image)
        #kick refactoring for imports time optimisation 
        #input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32) 
        input_tensor = convert_to_tensor(np.expand_dims(image_np, 0), dtype=float32) 
        detections = self.detect_fn(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                    for key, value in detections.items()}
        detections['num_detections'] = num_detections
        print(self.my_pred(detections=detections))
        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)


        label_id_offset = 1
        image_np_with_detections = image_np.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'] + label_id_offset,
            detections['detection_scores'],
            self.category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=1,
            min_score_thresh=0.3,
            agnostic_mode=False)

        output_filename = os.path.join(baseDir, f"{os.path.basename(image)}out.jpeg") 
        cv2.imwrite(output_filename, cv2.cvtColor(image_np_with_detections, cv2.COLOR_BGR2RGB)) 
        if display:
            cv2.imshow("window", cv2.cvtColor(image_np_with_detections, cv2.COLOR_BGR2RGB))
        return self.my_pred(detections=detections), output_filename

    def my_pred(self, image=None, detections=None):
        if detections is None:
            baseDir = os.path.dirname(image)
            img = cv2.imread(image)
            image_np = np.array(img)
            #kick refactoring for impoclearrtation time optimisation 
            #input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32) 
            input_tensor = convert_to_tensor(np.expand_dims(image_np, 0), dtype=float32)
            detections = self.detect_fn(input_tensor)

            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                        for key, value in detections.items()}
            detections['num_detections'] = num_detections

        labels = {
            0 : "nescafe",
            1 : "nido",
            2 : "bridel",
            3 : "eau",
        }

        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
        detections_classes = detections['detection_classes']
        detections_score = detections['detection_scores']
        detected_classes = []
        for _ in range(5):
            curr_index = np.argmax(detections_score)
            if detections_score[curr_index] < 0.8:
                continue
            detected_classe = detections_classes[curr_index]
            label = labels[detected_classe]
            detected_classes.append(
                {
                    "index" : curr_index,
                    "label" : label,
                    "score" : detections_score[curr_index]
            }
            )
            detections_classes = np.delete(detections_classes, curr_index)
            detections_score = np.delete(detections_score, curr_index)
        return detected_classes


           

if __name__ == '__main__':
    imagePath = sys.argv[1]
    CHECKPOINT_PATH = os.path.join(os.getcwd(), "models", "current_model")
    CONFIG_FILE = os.path.join(CHECKPOINT_PATH, "pipeline.config")
    LABEL_MAP = os.path.join(CHECKPOINT_PATH, "label_map.pbtxt")
    model = Model(CHECKPOINT_PATH, CONFIG_FILE, LABEL_MAP)
    print(model.get_predictions(imagePath, display=True))