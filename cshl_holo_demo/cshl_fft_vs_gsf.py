import numpy as np
from skimage import io
from holographics_temp import GSF_3D
from numpy.fft import fft2, ifft2
from matplotlib import pyplot as plt, gridspec

compute_size = (256, 256)
im1 = np.zeros(compute_size)
im1[130:135, 132:135] = 255
# im1 = io.imread('sample_images/face2.jpg').mean(axis=2)
im1 = io.imread('sample_images/michael-orger.jpg').mean(axis=2)

imfft = fft2(im1)
res = GSF_3D.GS_3D([im1], [0], iterations=5)

# frameplayer = Frameplayer()
# pattern = res.phase
# pattern -= pattern.min()
# pattern = ((pattern / pattern.max() * 100) % 255).astype(np.uint8)
# f = Frame(holograms=[pattern.T], duration=200.0)
# frameplayer.loadframes([f])
# frameplayer.playframes()


cmap = plt.cm.Greys_r
plt.figure(figsize=(10, 6))
gs = gridspec.GridSpec(2, 4, wspace=.1, hspace=.1, left=.05, right=.95)
plt.subplot(gs[0, 0])
plt.axis('off')
plt.imshow(im1, cmap=cmap)
plt.title('Image')

plt.subplot(gs[0, 1])
plt.axis('off')
plt.imshow(np.angle(imfft), cmap)
plt.title('FFT phase')

plt.subplot(gs[0, 2])
plt.axis('off')
plt.imshow(np.abs(ifft2(imfft)), cmap)
plt.title('inverse FFT + FFT')

plt.subplot(gs[0, 3])
plt.axis('off')
plt.imshow(np.abs(ifft2(np.exp(1j * np.angle(imfft)))), cmap)
plt.title('inverse FFT + FFT (phase only)')

# GS
plt.subplot(gs[1, 0])
plt.axis('off')
plt.imshow(im1, cmap)
plt.title('Image')

plt.subplot(gs[1, 1])
plt.axis('off')
plt.imshow(res.phase, cmap)
plt.title('GS phase')

plt.subplot(gs[1, 2])
plt.axis('off')

plt.subplot(gs[1, 3])
plt.axis('off')
plt.imshow(res.target_fields[0], cmap)
plt.title('GS computed target (phase only)')

plt.show()
