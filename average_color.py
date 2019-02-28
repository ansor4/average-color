from PIL import Image, ImageDraw
import sys

def naiveAverageColor(img):
  pixels= img.load()
  width, height = img.size

  pixelArray = []
  for x in range(width):
    for y in range(height):
      pixelArray.append(pixels[x, y])

  return averageColor(pixelArray)

def averageColor(pixelArray):

  r = g = b = 0
  for p in pixelArray:
    r += p[0]
    g += p[1]
    b += p[2]

  numPixels = len(pixelArray)
  r /= numPixels
  g /= numPixels
  b /= numPixels

  return (r, g, b)

def medianCut(img, numPaletteColors):

  pixels = img.load()
  pixelArray = []
  width, height = img.size
  for x in range(width):
    for y in range(height):
      pixelArray.append(pixels[x, y])
  
  palette = recursiveModifiedMedianCutQuantization(pixelArray, numPaletteColors)
  return palette

def calculateBoxDimensions(pixelArray):

  min_r = min_b = min_g = 255
  max_r = max_b = max_g = 0

  for p in pixelArray:
    if p[0] > max_r:
      max_r = p[0]
    if p[0] < min_r:
      min_r = p[0]
    if p[1] > max_b:
      max_b = p[1]
    if p[1] < min_b:
      min_b = p[1]
    if p[2] > max_g:
      max_g = p[2]
    if p[2] < min_g:
      min_g = p[2]
  
  diff_r = max_r - min_r
  diff_g = max_g - min_g
  diff_b = max_b - min_b

  return (diff_r, diff_g, diff_b)

  
def recursiveModifiedMedianCutQuantization(pixelArray, numPaletteColors):

  if numPaletteColors <= 1:
    diff_r, diff_g, diff_b = calculateBoxDimensions(pixelArray)
    priority = len(pixelArray) * (diff_r * diff_g * diff_b)
    return [(priority, averageColor(pixelArray))]

  diff_r, diff_g, diff_b = calculateBoxDimensions(pixelArray)

  # replace with priority queue
  palette = []

  if diff_r >= diff_g and diff_r >= diff_b:
    r_sorted = sorted(pixelArray, key = lambda x : x[0])
    median = len(r_sorted) / 2
    palette.extend(recursiveModifiedMedianCutQuantization(r_sorted[:median], numPaletteColors/2))
    palette.extend(recursiveModifiedMedianCutQuantization(r_sorted[median+1:], numPaletteColors/2))
  elif diff_g >= diff_r and diff_g >= diff_b:
    g_sorted = sorted(pixelArray, key = lambda x : x[1])
    median = len(g_sorted) / 2
    palette.extend(recursiveModifiedMedianCutQuantization(g_sorted[:median], numPaletteColors/2))
    palette.extend(recursiveModifiedMedianCutQuantization(g_sorted[median+1:], numPaletteColors/2))
  elif diff_b >= diff_r and diff_b >= diff_g:
    b_sorted = sorted(pixelArray, key = lambda x : x[2])
    median = len(b_sorted) / 2
    palette.extend(recursiveModifiedMedianCutQuantization(b_sorted[:median], numPaletteColors/2))
    palette.extend(recursiveModifiedMedianCutQuantization(b_sorted[median+1:], numPaletteColors/2))

  return palette

def paintAndShowColor(new_img_name, width, height, avg_color):

  img = Image.new('RGB', (width, height), color = avg_color)
  img.show()
  img.save(new_img_name)

def paintAndShowColorPalette(new_img_name, width, height, palette):

  img = Image.new('RGB', (width, height), color = avg_color)

  xy_array = [
    [(0, 0), (width/2, height/4)], [(width/2 + 1, 0), (width, height/4)], 
    [(0, height/4), (width/2, height/2)], [(width/2 + 1, height/4), (width, height/2)], 
    [(0, height/2), (width/2, height*3/4)], [(width/2 + 1, height/2), (width, height*3/4)], 
    [(0, height*3/4), (width/2, height)], [(width/2 + 1, height*3/4), (width, height)], 
  ]

  draw = ImageDraw.Draw(img)

  for i in range(len(xy_array)):
    draw.rectangle(xy_array[i], fill=palette[i])

  img.show()
  img.save(new_img_name)

if __name__ == '__main__':

  img_path = sys.argv[1]
  img = Image.open(img_path)
  img.show()

  avg_color = naiveAverageColor(img)
  new_img_name = img_path.split("/")[-1].split(".")[0] + "_avgcolor.png"
  paintAndShowColor(new_img_name, img.size[0], img.size[1], avg_color)

  dominant_colors = medianCut(img, 8)
  colors_by_dominance = sorted(dominant_colors, key = lambda x : x[0], reverse=True)

  dom_color_img_name = img_path.split("/")[-1].split(".")[0] + "_domcolor.png"
  paintAndShowColor(dom_color_img_name, img.size[0], img.size[1], colors_by_dominance[0][1])
  
  palette = [x[1] for x in colors_by_dominance]
  palette_img_name = img_path.split("/")[-1].split(".")[0] + "_palette.png"
  paintAndShowColorPalette(palette_img_name, img.size[0], img.size[1], palette)
