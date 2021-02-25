import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
from scipy.ndimage.filters import gaussian_filter1d as gf1d

plt.style.use('ggplot')


def plot_fps(): 
    data = pd.read_csv('fps_data.csv')
    for col in data.columns: 
        p = plt.plot(gf1d(data[col], sigma = 5), label = col)
        plt.plot(data[col], alpha = 0.2, color = p[0].get_color())

    plt.legend()
    plt.title('FPS per Tracking method', weight = 'bold')
    plt.show()

def plot_fps_hist(): 
    data = pd.read_csv('fps_data.csv')
    for col in data.columns: 
        sns.kdeplot(data[col], label = col)
    plt.legend()
    plt.title('FPS KDE', weight = 'bold')
    plt.show()

if __name__ == "__main__": 

    plot_fps()
    plot_fps_hist()