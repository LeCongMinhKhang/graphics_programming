import numpy as np
import cv2
import colorsys

import logging

logger = logging.getLogger(__name__)


# def get_bounding_box(frame):
#   """
#   :param frame: the picture of an object
#   :return: the bounding box of the object
#   """
#   frame_height, frame_width, _ = frame.shape
#   top, bot, right, left = None, None, None, None
#   for col in range(frame_width):
#     for row in range(frame_height):
#       pixel = frame[col, row]
#       if pixel[3] != 0:
#         if top is None or top < row:
#           top = row
#         if bot is None or bot > row:
#           bot = row
#         if right is None or right < col:
#           right = col
#         if left is None or left > col:
#           left = col
#   print(top, bot, right, left)
#   return top, bot, right, left


def get_bounding_box(frame, threshold=0):
  """
  :param frame: (h, w, 4) RGBA image of an object, top row first
  :param threshold: pixels with alpha <= threshold are considered background
  :return: (top, bot, right, left) pixel indices (inclusive), or None if the object is empty
  """
  mask = frame[:, :, 3] > threshold
  rows = np.flatnonzero(mask.any(axis=1))  # y indices containing the object
  cols = np.flatnonzero(mask.any(axis=0))  # x indices containing the object
  if rows.size == 0:
    logger.debug("no object pixels found in frame")
    return None

  top, bot = int(rows[0]), int(rows[-1])
  left, right = int(cols[0]), int(cols[-1])
  return top, bot, right, left


# def bounding_box(frame_width, frame_height, top, bot, right, left):
#   frame = np.zeros((frame_height, frame_width, 4))
#   return


def draw_bounding_box(image, bbox, color=(0, 255, 0), thickness=2, label=None):
  """
  Draw a bounding box in place on <image>.

  :param image: (h, w, 3|4) uint8 image, top row first
  :param bbox: (top, bot, right, left) as returned by get_bounding_box, or None
  :param color: box color, in the same channel order as <image>
  :param label: optional text drawn above the box
  :return: <image>, for chaining
  """
  if bbox is None:
    return image
  top, bot, right, left = bbox
  if image.shape[2] == 4 and len(color) == 3:
    color = (*color, 255)  # opaque alpha, otherwise the box may be invisible

  cv2.rectangle(image, (left, top), (right, bot), color, thickness)
  if label is not None:
    # keep the text inside the image when the box touches the top edge
    y = top - 6 if top > 16 else bot + 16
    cv2.putText(image, str(label), (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
  return image


def generate_colors(n, saturation=0.8, value=0.95):
  return np.array(
    [colorsys.hsv_to_rgb(i / n, saturation, value) for i in range(n)], dtype=np.float32
  )


def build_overlay(size, bboxes_by_name, colors):
  w, h = size
  overlay = np.zeros((h, w, 4), dtype=np.uint8)  # fully transparent
  for (name, bbox), color in zip(bboxes_by_name, colors):
    c = (*(int(v * 255) for v in color), 255)
    draw_bounding_box(overlay, bbox, color=c, label=name)  # your existing function
  return overlay
