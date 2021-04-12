import rosbag
import cv2
import sys
import os
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import datetime
from multiprocessing import Process

def unix2datetime(unix_time):
    date_time = datetime.datetime.fromtimestamp(unix_time) + datetime.timedelta(hours=9)
    return date_time.strftime("%Y-%m-%dT%H.%M.%S.%f")

# arguments
bag_path = sys.argv[1]
output_dir = sys.argv[2]
target_topic = sys.argv[3]
output_suffix = sys.argv[4]

if output_suffix != "jpg" and output_suffix != "png":
    raise ValueError("You should choose image format to output to jpg or png")

# load bag file
bag = rosbag.Bag(bag_path).read_messages()
print("bag file loaded!")

def write_msg_image(msg, t):
    # convert compressed image to cv image array
    np_array = np.fromstring(msg.data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    date_time = unix2datetime(t.to_sec())
    output_path = os.path.join(output_dir, date_time+"."+output_suffix)

    # output the image
    cv2.imwrite(output_path, image)

process_list = []
# loop in each message
for topic, msg, t in bag:
    if topic==target_topic:
        process = Process(
            target=write_msg_image,
            kwargs={'msg': msg, 't': t})
        process.start()
        process_list.append(process)

for process in process_list:
    process.join()
