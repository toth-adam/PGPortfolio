from __future__ import print_function, absolute_import, division
import json
import os
import logging
from os import path
import numpy as np

# -tól -ig
learning_rate = [0.0001, 0.0005]
batch_size = [60, 150]
window_size = [20, 40]
coin_number = [5, 11]
rolling_training_steps = [40, 120]
# egyet választani
global_period = [900, 1800, 7200, 14400]

def add_packages(config, repeat=1):
    train_dir = "train_package"
    package_dir = path.realpath(__file__).replace('pgportfolio/autotrain/generate.pyc',train_dir)\
        .replace("pgportfolio\\autotrain\\generate.pyc", train_dir)\
                  .replace('pgportfolio/autotrain/generate.py',train_dir)\
        .replace("pgportfolio\\autotrain\\generate.py", train_dir)
    all_subdir = [int(s) for s in os.listdir(package_dir) if os.path.isdir(package_dir+"/"+s)]
    if all_subdir:
        max_dir_num = max(all_subdir)
    else:
        max_dir_num = 0
    indexes = []

    l_rate = None
    b_size = None
    w_size = None
    c_number = None
    r_t_steps = None
    g_period = None

    for i in range(repeat):
        max_dir_num += 1
        directory = package_dir+"/"+str(max_dir_num)
        config["random_seed"] = i

        # random értékek
        if i % 3 == 0:
            l_rate = np.random.uniform(learning_rate[0], learning_rate[1], size=1)
            b_size = np.random.randint(batch_size[0], batch_size[1], size=1)
            w_size = np.random.randint(window_size[0], window_size[1], size=1)
            c_number = np.random.randint(coin_number[0], coin_number[1], size=1)
            r_t_steps = np.random.randint(rolling_training_steps[0], rolling_training_steps[1], size=1)
            g_period = np.random.choice(global_period)
        # megnézni a configot hogy mi a tosz az elnevezések
        config["training"]["learning_rate"] = l_rate
        config["trading"]["learning_rate"] = l_rate
        config["training"]["batch_size"] = b_size
        config["input"]["window_size"] = w_size
        config["input"]["coin_number"] = c_number
        config["trading"]["rolling_training_steps"] = r_t_steps
        config["input"]["global_period"] = g_period

        os.makedirs(directory)
        indexes.append(max_dir_num)
        with open(directory + "/" + "net_config.json", 'w') as outfile:
            json.dump(config, outfile, indent=4, sort_keys=True)
    logging.info("create indexes %s" % indexes)
    return indexes

