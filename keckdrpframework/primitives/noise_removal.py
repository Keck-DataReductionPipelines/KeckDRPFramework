"""
Created on Jul 8, 2019

@author: skwok
"""

import numpy as np
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive


class NoiseRemoval(BasePrimitive):
    """
    Simnple noise removal.
    This is an example for a primitive.
    The configuration for this primitive is in the auxiliary configuration file fits2png.cfg.
    """

    def __init__(self, action, context):
        """
        Initializes the superclass and retrieves the configuration parameters or sets defaults.
        """
        BasePrimitive.__init__(self, action, context)
        cfg = self.config.fits2png
        self.sigmas = eval(cfg.get("DEFAULT", "denoise_sigmas"))
        self.sizes = cfg.get("DEFAULT", "denoise_sizes")

    def _denoise(self, _img, size=3, sigmas=3):
        """
        Finds mean and std.
        For pixels outside mean +/- std *3, finds median and replace pixel
        Returns new image
        """

        def f(x, y):
            x = max(min(w, x), 0)
            y = max(min(h, y), 0)
            return medf(_img[y : y + size, x : x + size])

        medf = np.median
        h, w = _img.shape
        mean0 = np.mean(_img)
        std0 = np.std(_img)
        std1 = std0 * sigmas
        # print ("mean", mean0- std1, mean0+std1)
        idc = np.vstack((np.argwhere(_img > (mean0 + std1)), np.argwhere(_img < (mean0 - std1))))
        out = np.copy(_img)
        half = size // 2
        for a, b in idc:
            out[a, b] = f(b - half, a - half)
        return out

    def _perform(self):
        sigmas, sizes = self.sigmas, self.sizes
        args = self.action.args
        self.logger.debug(f"noise removal sigmas={sigmas}, sizes={sizes}")
        img = args.img

        for a, b in zip(sizes, sigmas):
            img = self._denoise(img)

        out_args = Arguments(name=args.name, img=img)
        return out_args
