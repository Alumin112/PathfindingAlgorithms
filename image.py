from PIL import Image
import numpy as np

imgs = [[(255, 255, 255) for _ in range(6)] for _ in range(3)]
img = np.array(imgs, np.uint8)
img[0][3] = (0, 0, 0)
img[0][4] = (0, 0, 0)
img[1][4] = (0, 0, 0)
img[0][5] = (48,213,200)
img[2][0] = (255,165,0)
print(type(img), img.shape, type(img.shape))
# img = img.reshape(img.shape[1], img.shape[0], img.shape[2])
# print(img)

# # im = Image.fromarray(img)
# im = Image.fromarray((img * 255).astype(np.uint8))
# im.save("g.png")
# # Image.fromarray(img).save('pxl.png')
# im = np.asarray(Image.open("pxl.png"))
Image.fromarray(img).save("pxl.png")
# print(im)

