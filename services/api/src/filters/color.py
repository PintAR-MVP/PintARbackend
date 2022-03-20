from colour import Color

import traceback

from .filter import ScoreFilter

def rgb_to_xyz(rgb):
  r, g, b = rgb

  if ( r > 0.04045 ):
    r = ( ( r + 0.055 ) / 1.055 ) ** 2.4
  else:
    r = r / 12.92

  if ( g > 0.04045 ):
    g = ( ( g + 0.055 ) / 1.055 ) ** 2.4
  else:
    g = g / 12.92

  if ( b > 0.04045 ):
    b = ( ( b + 0.055 ) / 1.055 ) ** 2.4
  else:
    b = b / 12.92

  r = r * 100
  g = g * 100
  b = b * 100

  x = r * 0.4124 + g * 0.3576 + b * 0.1805
  y = r * 0.2126 + g * 0.7152 + b * 0.0722
  z = r * 0.0193 + g * 0.1192 + b * 0.9505

  return x, y, z

def xyz_to_lab(xyz):
  x, y, z = xyz

  x = x / 96.4221
  y = y / 100.0
  z = z / 82.5211

  if ( x > 0.008856 ):
    x = x ** ( 1/3 )
  else:
    x = ( 7.787 * x ) + ( 16 / 116 )

  if ( y > 0.008856 ):
    y = y ** ( 1/3 )
  else:
    y = ( 7.787 * y ) + ( 16 / 116 )

  if ( z > 0.008856 ):
    z = z ** ( 1/3 )
  else:
    z = ( 7.787 * z ) + ( 16 / 116 )

  l = ( 116 * y ) - 16
  a = 500 * ( x - y )
  b = 200 * ( y - z )

  return l, a, b

def rgb_to_lab(rgb):
  return xyz_to_lab(rgb_to_xyz(rgb))

def delta_e(lab1, lab2):
  l1, a1, b1 = lab1
  l2, a2, b2 = lab2
  return ((l1-l2)**2.0 + (a1-a2)**2.0 + (b1-b2)**2.0) ** 0.5

def color_similarity_score(color1, color2):
  de = delta_e(rgb_to_lab(Color(color1).rgb), rgb_to_lab(Color(color2).rgb)) / 100.0

  if de < 0.0:
    de = 0.0

  if de > 1.0:
    de = 1.0

  return 1.0 - de

class ColorFilter(ScoreFilter):
  def __init__(self, config):
    self.config = config

  def score(self, products):
    try:
      scores = []
      for product in products:
        color_score = color_similarity_score(product["color"], self.config["color"])

        scores.append(color_score)

      return scores
    except:
      traceback.print_exc()

      return [0.0] * len(products)
