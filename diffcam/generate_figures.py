"""
This script will load the PSF data and raw measurement for the reconstruction
that can implement afterwards.
```bash
python scripts/reconstruction_template.py --psf_fp data/psf/diffcam_rgb.png \
--data_fp data/raw_data/thumbs_up_rgb.png
```
"""

import os
import time
import pathlib as plib
import click
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from diffcam.io import load_data
from diffcam.metric import mse, psnr, ssim, lpips

from recon import Recon
from plot import plot_image

@click.command()
@click.option(
    "--psf_fp",
    type=str,
    help="File name for recorded PSF.",
)
@click.option(
    "--data_fp",
    type=str,
    help="File name for raw measurement data.",
)
@click.option(
    "--n_iter",
    type=int,
    default=500,
    help="Number of iterations.",
)
@click.option(
    "--downsample",
    type=float,
    default=4,
    help="Downsampling factor.",
)
@click.option(
    "--disp",
    default=50,
    type=int,
    help="How many iterations to wait for intermediate plot/results. Set to negative value for no intermediate plots.",
)
@click.option(
    "--flip",
    is_flag=True,
    help="Whether to flip image.",
)
@click.option(
    "--save",
    is_flag=True,
    help="Whether to save intermediate and final reconstructions.",
)
@click.option(
    "--gray",
    is_flag=True,
    help="Whether to perform construction with grayscale.",
)
@click.option(
    "--bayer",
    is_flag=True,
    help="Whether image is raw bayer data.",
)
@click.option(
    "--no_plot",
    is_flag=True,
    help="Whether to no plot.",
)
@click.option(
    "--bg",
    type=float,
    help="Blue gain.",
)
@click.option(
    "--rg",
    type=float,
    help="Red gain.",
)
@click.option(
    "--gamma",
    default=None,
    type=float,
    help="Gamma factor for plotting.",
)
@click.option(
    "--single_psf",
    is_flag=True,
    help="Same PSF for all channels (sum) or unique PSF for RGB.",
)
def reconstruction(
    psf_fp,
    data_fp,
    n_iter,
    downsample,
    disp,
    flip,
    gray,
    bayer,
    bg,
    rg,
    gamma,
    save,
    no_plot,
    single_psf,
):
    for i in range(1):
        data_fp = '../raw_data/' + str(i+1) + '_raw_rgb.png'
        psf, data = load_data(
            psf_fp=psf_fp,
            data_fp=data_fp,
            downsample=downsample,
            bayer=bayer,
            blue_gain=bg,
            red_gain=rg,
            plot=not no_plot,
            flip=flip,
            gamma=gamma,
            gray=gray,
            single_psf=single_psf,
        )

        if disp < 0:
            disp = None
        if save:
            save = os.path.basename(data_fp).split(".")[0]
            timestamp = datetime.now().strftime("_%d%m%d%Y_%Hh%M")
            save = "YOUR_RECONSTRUCTION_" + save + timestamp
            save = plib.Path(__file__).parent / save
            save.mkdir(exist_ok=False)


        _, tail = os.path.split(data_fp)
        lambdas = [0.000001, 0.000005, 0.000010, 0.000050,
                   0.000100, 0.000500, 0.001000, 0.005000,
                   0.010000, 0.050000, 0.100000, 0.500000]
        modes = ['huber', 'lasso']
        # modes = ['huber', 'nnL1',  'dct', 'ridge', 'lasso', 'nn']
        for looping_lambda in lambdas:
            for looping_mode in modes:
                start_time = time.time()
                solver = Recon(data, psf, mode=looping_mode, lambda1=looping_lambda)
                print("Mode: ", looping_mode, "Lambda: ", looping_lambda)
                print(f"setup time : {time.time() - start_time} s")
                start_time = time.time()
                # TODO : apply your reconstruction
                allout = solver.iterate() # Run APGD
                # plt.figure()
                estimate = solver.get_estimate()
                np.save('rgb_estimate.npy', estimate)
                plot_image(estimate)
                print(f"proc time : {time.time() - start_time} s")
                proc_time = time.time() - start_time
                iteration_variant = 'color_corrected_image_' + tail + '_' + looping_mode + '_' +  str(looping_lambda)+ '_proc_time_' + str(proc_time)
                iteration_variant = iteration_variant.replace('.', '_')
                local_dir = 'C:\\Users\\ludvi\\programming\\EPFL\\COM-514\\project_ours\\images\\'
                plt.savefig(local_dir + iteration_variant + '.png')
                plt.close('all')

if __name__ == "__main__":
    reconstruction()