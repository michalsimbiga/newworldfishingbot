import os
import sys
import glob

import dlib

if len(sys.argv) != 2:
    print(
        "Give the path to the examples/faces directory as the argument to this "
        "program. For example, if you are in the python_examples folder then "
        "execute this program by running:\n"
        "    ./train_object_detector.py ../examples/faces")
    exit()
faces_folder = sys.argv[1]

options = dlib.simple_object_detector_training_options()
options.add_left_right_image_flips = True
options.C = 5
options.num_threads = 4
options.be_verbose = True

training_xml_path = os.path.join(faces_folder, "training.xml")
testing_xml_path = os.path.join(faces_folder, "testing.xml")

dlib.train_simple_object_detector(training_xml_path, "reel_detector.svm", options)

# print("")  # Print blank line to create gap from previous output
# print("Training accuracy: {}".format(
#     dlib.test_simple_object_detector(training_xml_path, "detector.svm")))
#
# print("Testing accuracy: {}".format(
#     dlib.test_simple_object_detector(testing_xml_path, "detector.svm")))
#
# detector = dlib.simple_object_detector("detector.svm")
#
# win_det = dlib.image_window()
# win_det.set_image(detector)
#
# print("Showing detections on the images in the faces folder...")
# win = dlib.image_window()
# for f in glob.glob(os.path.join(faces_folder, "*.jpg")):
#     print("Processing file: {}".format(f))
#     img = dlib.load_rgb_image(f)
#     dets = detector(img)
#     print("Number of faces detected: {}".format(len(dets)))
#     for k, d in enumerate(dets):
#         print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
#             k, d.left(), d.top(), d.right(), d.bottom()))
#
#     win.clear_overlay()
#     win.set_image(img)
#     win.add_overlay(dets)
#     dlib.hit_enter_to_continue()
#
#
# detector1 = dlib.fhog_object_detector("detector.svm")
# detector2 = dlib.fhog_object_detector("detector.svm")
#
# detectors = [detector1, detector2]
# image = dlib.load_rgb_image(faces_folder + '/test.jpg')
# [boxes, confidences, detector_idxs] = dlib.fhog_object_detector.run_multiple(detectors, image, upsample_num_times=1, adjust_threshold=0.0)
# for i in range(len(boxes)):
#     print("detector {} found box {} with confidence {}.".format(detector_idxs[i], boxes[i], confidences[i]))
#
# images = [dlib.load_rgb_image(faces_folder + '/test.jpg')]
#
# detector2.save('pull_detector.svm')
#
# win_det.set_image(detector2)
# dlib.hit_enter_to_continue()
