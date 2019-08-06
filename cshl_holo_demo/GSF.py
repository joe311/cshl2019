import numpy as np
from collections import namedtuple
from numpy.fft import fft2, ifft2, fftshift, ifftshift

pi = np.pi


class GSFresult(
    namedtuple('GSFresult', ['phase', 'target_fields', 'lenses', 'algorithm', 'errors', 'correlations', 'exported_z'])):
    """
    Storage class for GSF results
    Namedtuple doesn't support default args :(
    """

    def __new__(cls, phase, target_fields=None, lenses=None, algorithm=None, errors=None, correlations=None, exported_z=None):
        return super(GSFresult, cls).__new__(cls, phase, target_fields, lenses, algorithm, errors, correlations, exported_z)
        # TODO make this more introspective?, also easier to replace


def GS_FFT(target_amplitude, iterations=30, replace_middle=True):
    # simple GS FFT propagator
    assert target_amplitude.shape[0] == target_amplitude.shape[1]
    ini_amplitude = np.random.rand(*target_amplitude.shape)
    slm_field = ini_amplitude

    corrs = []
    for i in range(iterations):
        target_field = fftshift(fft2(fftshift(slm_field)))

        x = np.abs(target_field)
        corrs.append(np.corrcoef(x.ravel(), target_amplitude.ravel())[0, 1])
        if i == iterations - 1:
            export_target_field = np.abs(target_field.copy())
        target_field = np.abs(target_amplitude) * np.exp(1j * np.angle(target_field))
        slm_field = fftshift(ifft2(fftshift(target_field)))
        slm_field = ini_amplitude * np.exp(1j * np.angle(slm_field))

    if replace_middle:  # replace middle of export field, there's always a high intensity pixel there from the fft
        export_target_field[int(export_target_field.shape[0] / 2), int(export_target_field.shape[1] / 2)] = 0

    return GSFresult(phase=np.angle(slm_field) + pi, target_fields=[export_target_field], correlations=corrs,
                     algorithm='GSF_2D')


def GSF_Zlens(target_amplitude, Z=0, wavelength=960, *args, **kwargs):
    res = GS_FFT(target_amplitude, *args, **kwargs)
    if Z != 0:
        lens1 = lens(res.phase.shape, res.phase.shape[1] / 2, Z, wavelength)
        res = res._replace(phase=(res.phase + lens1) % (2 * pi))
        res = res._replace(lenses=[lens1])
    return res


def GSF_2D_compatibility_wrapper(target_amplitudes, Zs=None, *args, **kwargs):
    """
    Provides a wrapper with the same interface as the 3D GSF, to simplify calling
    :param target_amplitudes: list with a single target_pattern
    :param Zs: list with a single target Z
    """
    if Zs is None:
        Zs = [0]
    assert len(target_amplitudes) == 1 and len(Zs) == 1
    return GSF_Zlens(target_amplitudes[0], Zs[0], *args, **kwargs)


def lens(ini_field_shape, side_length, z, wavelength, focal_length=1, m=1):
    # m = refractive index
    # focal length should come from system, in um
    # wavelength in nm
    # wavelength /= 1000. #to convert to um
    z = z / 10  # previous there was a factor 10 scaling applied for Z calibration, moving that here instead
    dx = side_length / ini_field_shape[1]  # should it be 1 or 0 of the shape?
    x = np.linspace(-side_length / 2, side_length / 2 - dx, ini_field_shape[1])
    xp, yp = np.meshgrid(x, x)

    clens = - (pi * m) / (wavelength * focal_length ** 2) * -z * (xp ** 2 + yp ** 2)  # minus Z to match the system
    return np.fmod(clens, 2 * pi)
