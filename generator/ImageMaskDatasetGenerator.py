# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# ImageMaskDatasetGenerator.py

import os
import sys
import glob
import shutil
import traceback
import numpy as np

from PIL import Image, ImageOps

     
class ImageMaskDatasetGenerator:
  def __init__(self, resize=512):
    self.RESIZE = resize
    self.threshold = 100 #128
    self.ROTATION = True
    self.file_extension = ".bmp"

  def augment(self, image, output_dir, filename):
  
    if self.ROTATION:
      ANGLES = [30, 90, 120, 150, 180, 210, 240, 270, 300, 330]

      for angle in ANGLES:
        rotated_image = image.rotate(angle)
        output_filename = "rotated_" + str(angle) + "_" + filename
        rotated_image_file = os.path.join(output_dir, output_filename)
        #cropped  =  self.crop_image(rotated_image)
        rotated_image.save(rotated_image_file)
        print("=== Saved {}".format(rotated_image_file))
      
    # Create mirrored image
    mirrored = ImageOps.mirror(image)
    output_filename = "mirrored_" + filename
    image_filepath = os.path.join(output_dir, output_filename)
    #cropped = self.crop_image(mirrored)
    
    mirrored.save(image_filepath)
    print("=== Saved {}".format(image_filepath))
        
    # Create flipped image
    flipped = ImageOps.flip(image)
    output_filename = "flipped_" + filename

    image_filepath = os.path.join(output_dir, output_filename)
    #cropped = self.crop_image(flipped)

    flipped.save(image_filepath)
    print("=== Saved {}".format(image_filepath))

  def generate(self, image_dir, mask_dir, output_dir):
    self.create_resized_image(image_dir, output_dir, color=(255, 255, 255))
    self.create_resized_mask(mask_dir, output_dir,   color=(255, 255, 255))


  def create_resized_image(self, image_dir, output_dir, color=(255, 255, 255)):
    output_image_dir = os.path.join(output_dir, "images")

    if not os.path.exists(output_image_dir):
       os.makedirs(output_image_dir)

    image_files = glob.glob(image_dir + "/*.bmp")
    for image_file in image_files:
      image = Image.open(image_file)
      resized_image = self.resize_to_square(image, color)
      basename = os.path.basename(image_file)
      name     = basename.split(".")[0]
      filename = name + ".jpg"
      output_filepath = os.path.join(output_image_dir, filename)
      resized_image.save(output_filepath)
      print("=== Saved {}".format(output_filepath))
      
      self.augment(resized_image, output_image_dir, filename)


  def create_resized_mask(self, mask_dir, output_dir, color=(0, 0, 0)):
    output_mask_dir = os.path.join(output_dir, "masks")
    if not os.path.exists(output_mask_dir):
      os.makedirs(output_mask_dir)

    image_files = glob.glob(mask_dir + "/*.bmp")

    for image_file in image_files:
  
      image = Image.open(image_file)
      resized_image = self.resize_to_square(image, color)
      resized_image = resized_image.convert("L")
      resized_image = ImageOps.invert(resized_image)
      basename = os.path.basename(image_file)
      mask_pil = self.binarize(resized_image)
  
      name     = basename.split(".")[0]
      filename = name + ".jpg"

      output_filepath = os.path.join(output_mask_dir, filename)
 
      mask_pil.save(output_filepath)
      print("=== Saved {}".format(output_filepath))
      self.augment(mask_pil, output_mask_dir, filename)


  def resize_to_square(self, image, color):
     w, h  = image.size

     bigger = w
     if h > bigger:
       bigger = h
     print("---background {}".format(color))
     background = Image.new("RGB", (bigger, bigger), color)
    
     x = (bigger - w) // 2
     y = (bigger - h) // 2
     background.paste(image, (x, y))
     background = background.resize((self.RESIZE, self.RESIZE))

     return background
  
  def binarize(self, resized_image):
    mask = np.array(resized_image)
    mask[mask< self.threshold] =   0
    mask[mask>=self.threshold] = 255
    mask_pil = Image.fromarray(mask)
    return mask_pil

if __name__ == "__main__":
  try:
     image_dir = "./dataset_forsubmit/imgbmp/"
     mask_dir  = "./dataset_forsubmit/GroundTruth/"
     output_dir = "./Cervical_Cell_Nucleus_Master"
     if os.path.exists(output_dir):
       shutil.rmtree(output_dir)
     if not os.path.exists(output_dir):
       os.makedirs(output_dir)
     generator = ImageMaskDatasetGenerator()
     generator.generate(image_dir, mask_dir, output_dir)

  except:
    traceback.print_exc()
