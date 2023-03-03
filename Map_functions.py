import numpy as np
from noise import snoise3
from matplotlib import pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from skimage.draw import polygon

SIZE = 512  # Rozmiar mapy (pixele SIZExSIZE)

def relax(points, size, k=10):  # Relaksacja punktów (bardziej równomierne rozłożenie pomiędzy sobą aby uniknąć małych, nieregularnych regionów)
    new_points = points.copy()  # Kopia punktów
    for _ in range(k):
        vor = Voronoi(new_points)   # Stworzenie nowych punktów woronoja
        new_points = [] # Lista przechowująca nowe wyśrodkowane punkty
        for _, region in enumerate(vor.regions):
            if len(region) == 0 or -1 in region:    # Pominięcie regionów które są styczne z granicami mapy
                continue
            poly = np.array([vor.vertices[i] for i in region])
            center = poly.mean(axis=0)  # Obliczenie środka regionu
            new_points.append(center)   # Dodanie nowego punktu
        new_points = np.array(new_points).clip(0, size) # Obcięcie punktów które wykraczają poza granice mapy
    return new_points

def gen_voronoi_map(vor, size): # Tworzenie siatki z wartościami regionów
    voronoi_map = np.zeros((size, size))    # Stworzenie pustej siatki
    for i, region in enumerate(vor.regions):
        if (len(region) == 0) or (-1 in region):    # Pominięcie regionów stycznych z granicami mapy lub wykraczającymi
            continue
        x, y = np.array([vor.vertices[i][::-1] for i in region]).T  # Współrzędne wierzchołków
        polygon_x, polygon_y = polygon(x, y)    # Rozpiętości pionowych i poziomych współrzędnych regionu
        in_borders = np.where((0 <= polygon_x) & (polygon_x < size) & (0 <= polygon_y) & (polygon_y < size))    # Zależność określająca zawieranie się w granicach mapy
        polygon_x, polygon_y = polygon_x[in_borders], polygon_y[in_borders] # Ograniczenie obszarów do granic mapy
        voronoi_map[polygon_x, polygon_y] = i
    return voronoi_map

def noise_map(size, seed, scale=100., octaves=6, persistence=0.5, lacunarity=2.0):  # Funkcja generująca siatkę z szumem
    return np.array([[
        snoise3(
            x/scale,
            y/scale,
            seed,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity
        ) for x in range(size)] for y in range(size)])

def blure_boundaries(vor_map, disp, size, seed):    # Funkcja mieszająca granice regionów
    map_noise = noise_map(size, seed, 100.)
    noise = np.dstack([map_noise, map_noise])
    noise = np.indices((size, size)).T + disp*noise
    noise = noise.clip(0, size-1).astype('int')
    blurred_vor_map = vor_map[noise[:,:,0], noise[:,:,1]]
    return blurred_vor_map.T

def add_color(blurred_map, points, biomes): # Funkcja nanosząca biomy w zależności od wygenerowanych wartości regionów
    biomes_map = np.empty(blurred_map.shape+(3,))
    val = blurred_map/points
    biomes_map[val < 0.1] = biomes['TAIGA']
    biomes_map[(val >= 0.1) & (val < 0.2)] = biomes['FOREST']
    biomes_map[(val >= 0.2) & (val < 0.3)] = biomes['BEACH']
    biomes_map[(val >= 0.3) & (val < 0.4)] = biomes['SAND']
    biomes_map[(val >= 0.4) & (val < 0.5)] = biomes['GREEN']
    biomes_map[(val >= 0.5) & (val < 0.65)] = biomes['GREENY']
    biomes_map[(val >= 0.65) & (val < 0.8)] = biomes['MOUNTAIN']
    biomes_map[val >= 0.8] = biomes['SNOW']
    return biomes_map.astype(int)

def add_sea(biomes_map, size, scale, seed, octaves, sea_col):  # Funkcja dodająca wody do mapy biomów
    height_map = noise_map(size, seed, scale, octaves)  # Wygenerowanie mapy wysokości
    biomes_sea_map = biomes_map.copy()
    biomes_sea_map[height_map < 0] = sea_col    # Zakolorowanie mapy biomów kolorem wody w miejscach poniżej poziomu wody
    return height_map, biomes_sea_map.astype(int)

def add_height(biomes_sea_map, height_map): # Funkcja przyciemniająca barwy mapy w zależności od wysokości
    detail_map = biomes_sea_map*(1-0.1*(abs(height_map[..., np.newaxis])//0.1))
    return detail_map.astype(int)

def save_single_map(map_to_save, file_name, size=(10, 10), case=0): # Funkcja zapisująca grafikę mapy
    plt.figure(figsize=size)
    if case == 1:
        plt.imshow(map_to_save, origin='lower', cmap='Blues_r')
    else:
        plt.imshow(map_to_save, origin='lower')
    plt.axis('off')
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()

def save_points_plot(points, file_name, size=(10,10), case=0):  # Funkcja zapisująca grafikę wykresu z punktami
    plt.figure(figsize=size)
    if case == 1:
        voronoi_plot_2d(points, show_vertices=False)    # Diagram woronoja
        plt.gcf().set_size_inches(size)
    else:
        plt.scatter(points[:, 0], points[:, 1]) # Wykres punktowy
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()


def generate_maps(SEED, POINTS_NUM, BLEND): # Funkcja generująca mapę, wraz z grafikami komponentów na nią składającymi się
    # Wygenerowanie losowych punktów
    points = np.random.randint(0, SIZE, (POINTS_NUM, 2))
    save_points_plot(points, '0_1_points.png')

    # Rozłożenie 'wylosowanych' punktów
    points_relaxed = relax(points, SIZE, 2)
    save_points_plot(points_relaxed, '0_2_relaxed.png')

    # Stworzenie diagramu woronoja z rozłożonych punktów
    vor = Voronoi(points_relaxed)
    save_points_plot(vor, '0_3_voronoi.png', case=1)

    # Stworzenie mapy na podstawie diagramu woronoja
    voronoi_map = gen_voronoi_map(vor, SIZE)
    save_single_map(voronoi_map, '1_voronoi_map.png')

    # Mieszanie się granic biomów w zależności czy jest zaznaczona opcja
    blurred_vor_map = blure_boundaries(voronoi_map, POINTS_NUM*0.03, SIZE, SEED) if BLEND else voronoi_map
    save_single_map(blurred_vor_map, '2_blurred_map.png')

    # Słownik zawierajacy nazwy z kolorami biomów
    biomes = {  'TAIGA':[51, 102, 0],
                'BEACH':[238, 214, 175],
                'FOREST':[51, 204, 51],
                'SAND':[255, 255, 102],
                'GREEN':[36, 143, 36],
                'GREENY':[191, 255, 128],
                'MOUNTAIN':[155,155,155],
                'SNOW':[255,255,255],
                'WATER':[0, 0, 179] }

    # Grafika biomów
    biomes_map = add_color(blurred_vor_map, POINTS_NUM, biomes)
    save_single_map(biomes_map, '3_biomes_map.png')

    # Grafiki wody i biomów z wodą
    height_map, biomes_sea_map = add_sea(biomes_map=biomes_map, size=SIZE, scale=100., seed=SEED, octaves=8, sea_col=biomes['WATER'])
    save_single_map(height_map>0, '4_sea_map.png', case=1)
    save_single_map(biomes_sea_map, '5_biomes_sea_map.png')

    # Grafika finalnej mapy z naniesieniem wysokości
    final_map = add_height(biomes_sea_map=biomes_sea_map, height_map=height_map)
    save_single_map(final_map, '6_final_map.png')

    # Grafika ze wszystkimi mapami:
    _, axes_all = plt.subplots(3, 2, figsize=(10, 10))
    axes_all[0][0].imshow(voronoi_map, origin='lower')
    axes_all[0][1].imshow(blurred_vor_map, origin='lower')
    axes_all[1][0].imshow(biomes_map, origin='lower')
    axes_all[1][1].imshow(height_map>0, cmap='Blues', origin='lower')
    axes_all[2][0].imshow(biomes_sea_map, origin='lower')
    axes_all[2][1].imshow(final_map, origin='lower')
    [ax.set_axis_off() for ax in axes_all.ravel()]
    plt.subplots_adjust(left=0, right=0.52, wspace=0, hspace=0.05)
    plt.savefig('all_maps.png', bbox_inches='tight')
    plt.close()