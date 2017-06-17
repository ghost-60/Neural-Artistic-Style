# Convnet Style-Transfer

-> This document is based on the famous research paper [Gatys et al., 2015](https://arxiv.org/abs/1508.06576)

Style transfer is the technique of recomposing images in the style of other images. These were mostly created using paper by Gatys, Ecker, and Bethge demonstrating a method for restyling images using convolutional neural networks.


## Requirements
You will need the following to run the above:
  * Python3.5
  * Tensorflow
  * Keras
  * Numpy

## How to run the code
For Ubuntu users:
```
$ python3 vgg16.py <content_image_path> <style_image_path>

```
## Results
Result based on 10 iterations:
<p align = 'center'>
<img src = 'images_transfered/result.jpg' height = '246px'>
</p>


## Attributions/Thanks
  * Some code was borrowed from Justin Johnson's [Fast Neural Style](https://github.com/jcjohnson/fast-neural-style)
