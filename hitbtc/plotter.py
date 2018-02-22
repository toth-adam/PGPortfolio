import matplotlib.pyplot as plt
import numpy as np

'''
###########################
###      Plot stuff     ###
###########################
'''


def plot_data(pairs, trades, window_size):
    figure = plt.figure()
    half_window = int(window_size / 2)
    order_types = ['buy', 'sell']
    plot_matrix = int(str(len(pairs)) + "21")

    for i, pair in enumerate(pairs):
        for y, side in enumerate(order_types):
            fig = figure.add_subplot((plot_matrix + i * 2 + y))
            fig.set_title(pair + ' ' + side)

            plot_points = _one_pair_side_plot(pair, side, window_size, trades)
            fig.plot([ind for ind in range(-half_window, half_window)], [el for el in plot_points], 'ro')

    plt.ylabel('Relative Price')
    plt.xlabel('Time Offset')
    plt.axis([-half_window - 10, half_window + 10, 0.97, 1.03])
    plt.show()


def _one_pair_side_plot(pair, side, window_size, trades):
    plot_points = []
    half_window = int(window_size/2)
    for i in range(-half_window, half_window):
        average_list = []
        for el in trades[pair][side]:
            if i < el['offset'] < i + 1:
                average_list.append(el['rp'])

        b = np.array(average_list)
        if len(b) > 0:
            plot_points.append(b.mean())
        else:
            plot_points.append(0.98)

    return plot_points
