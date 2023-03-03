from tkinter import *
import tkinter.font as font
from PIL import ImageTk, Image
from Map_functions import generate_maps # Funkcja generująca mapy

WIDTH = 900 # Szerokość okna
HEIGHT = 600    # Wysokość okna
SEED = 0    # Ziarno na podstawie którego wykonywana jest generacja
POINTS_NUM = 1024   # Ilość losowych punktów wchodząca w diagram woronoja
BLEND = True    # Zacieranie się granic biomów w mapie
maps = {'ALL MAPS'  : 'all_maps.png',   # Słownik zawierający nazwy odpowiadających plików z mapami
        'FINAL'     : '6_final_map.png',
        'SEA & BIOMES': '5_biomes_sea_map.png',
        'SEA'       : '4_sea_map.png',
        'BIOMES'    : '3_biomes_map.png',
        'BLURRED'   : '2_blurred_map.png',
        'REGIONS'   : '1_voronoi_map.png',
        'VORONOI'   : '0_3_voronoi.png',
        'RELAXED POINTS'   : '0_2_relaxed.png',
        'POINTS'   : '0_1_points.png',}
points = {'TINY' : 256,   # Słownik zawierający wartości ilości punktów
        'SMALL' : 512,
        'MEDIUM' : 1024,
        'LARGE' : 2048,
        'HUGE' : 4096}
blend = {'YES' : True,
        'NO': False}

def main():
    def setEntryText(text): # Funkcja ustawiająca tekst w oknie do wpisywania ziarna
        seed_input_area.delete(0, END)
        seed_input_area.insert(0, ' '+text)

    def checkSeed(seed):   # Funkcja walidująca wprowadzony seed
        try: # Jeśli seed jest poprawny wyświetla aktualną wartość
            seed_value = abs(int(seed_input_area.get()))
            seed = seed_value
            current_seed_label.config(text=f'Current seed: {seed}', fg='#000000')
            setEntryText(str(seed))
            return True, seed_value
        except ValueError:  # Jeśli seed nie jest poprawny wyświetla o tym komunikat na czerwono
            current_seed_label.config(text=f'This seed is not a number!', fg='#ff0000')
            setEntryText('0')
            return False, 0

    def seedValChange(case, seed):  # Zmiana wartości ziarna po użyciu przycisków zmieniających wartość o 1
        try:
            seed_value = abs(int(seed_input_area.get()))
            seed = seed_value
            if case == 1:
                seed += 1
            elif seed != 0:
                seed -= 1
            seed = abs(seed)
            setEntryText(str(seed))
            current_seed_label.config(text=f'Current seed: {seed}', fg='#000000')
        except ValueError:  # Jeśli seed nie jest poprawny wyświetla o tym komunikat na czerwono
            current_seed_label.config(text=f'This seed is not a number!', fg='#ff0000')
            setEntryText(' 0')

    def updateImage(file): # Wczytywanie, skalowanie i wyświetlanie mapy
        img = Image.open(file) # Wczytanie mapy
        resized_img = img.resize((HEIGHT, HEIGHT), Image.Resampling.LANCZOS)  # Zmiana rozmiaru mapy
        new_map = ImageTk.PhotoImage(resized_img)
        canvas_map.image = new_map
        canvas_map.itemconfig(visible_map, image=new_map)

    def selectMap():    # Wybranie mapy po wcisnięciu adekwatnego przycisku radio
        updateImage(maps[cur_map.get()])
        current_map_label.config(text=f'Current map: {cur_map.get()}')

    def selectPoints(): # Wybranie ilości punktów po wciśnięciu adekwatnego przycisko radio
        global POINTS_NUM
        POINTS_NUM = points[cur_points.get()]
        current_points_label.config(text=f'Current number of points: {cur_points.get()}')

    def selectBlend():  # Zmiana mieszania się granic biomów po wciśnięciu adekwatnego przycisku radio
        global BLEND
        BLEND = blend[cur_blend.get()]
        current_blend_label.config(text=f'Biome blend: {cur_blend.get()}')

    def generateMap(seed):  # Generacja mapy po wciśnięciu przycisku
        is_correct, seed_value = checkSeed(seed)
        global SEED
        SEED = seed_value
        if is_correct:
            generate_maps(SEED, POINTS_NUM, BLEND)
            updateImage('6_final_map.png')
            cur_map.set('FINAL')
            current_map_label.config(text=f'Current map: {cur_map.get()}')
            current_gen_map_label.config(text=f'Current generated map seed: {SEED}')
            cur_points.set(cur_points.get())
            selectBlend()

    ### TWORZENIE UI ###
    generate_maps(SEED, POINTS_NUM, BLEND)  # Wygenerowanie pierwszej mapy podczas uruchomienia

    window = Tk()
    window.title('MAP GENERATOR JAKUB OSTROWSKI')   # Ustawienie tytułu okna
    window.geometry(str(WIDTH)+'x'+str(HEIGHT))  # Ustawienie rozmiarów okna

    small_font = font.Font(size=8, weight="bold")   # Pomniejszona i pogrubiona czcionka dla przycisków

    canvas_map = Canvas(window, width=HEIGHT, height=HEIGHT)  # Obszar do wyświetlania map
    canvas_map.place(x=0, y=0)   # Ustawienie obszaru do wyświetlania map po lewym górnym rogu
    img = Image.open('6_final_map.png') # Wczytanie mapy
    resized_img = img.resize((HEIGHT, HEIGHT), Image.Resampling.LANCZOS)  # Zmiana rozmiaru mapy
    new_img = ImageTk.PhotoImage(resized_img)
    visible_map = canvas_map.create_image(0, 0, anchor=NW, image=new_img)   # Wyświetlenie mapy

    Label(window, text="Seed:").place(relx=0.7, y=20)   # Etykieta z namisem "Seed:"
    seed_input_area = Entry(window, width=10)   # Obszar do wpisywania wartości seed
    seed_input_area.insert(0, ' 0') # Wprowadzenie startowej wartości seed
    seed_input_area.place(relx=0.79, y=17)
    current_seed_label = Label(window, text=f'Current seed: {SEED}')  # Etykieta wyświetlająca aktualną wartość seed
    current_seed_label.place(relx=0.7, y=50)
    minus_seed_button = Button(window, text="-", command=lambda:seedValChange(0, SEED), font=small_font)  # Przycisk do zmniejszania wartości seed
    minus_seed_button.place(relx=0.75, y=15)
    plus_seed_button = Button(window, text="+", command=lambda: seedValChange(1, SEED), font=small_font)   # Przycisk do zwiększania wartości seed
    plus_seed_button.place(relx=0.9, y=15)

    gen_button = Button(window, text="GENERATE MAP", command=lambda: generateMap(SEED))    # Przycisk do generowania mapy
    gen_button.place(relx=0.75, y=545)
    current_gen_map_label = Label(window, text=f'Current generated map seed: {SEED}')  # Etykieta wyświetlająca seed aktualnie wygenerowanej mapy
    current_gen_map_label.place(relx=0.70, y=580)

    cur_points = StringVar()    # Zmienna służąca do zapamiętania ustawionej ilości punktów
    starting = 190
    for (text, file) in points.items():   # Tworzenie radio przycisków do wybierania ilości punktów
        Radiobutton(window, text=text, variable=cur_points, value=text, command=lambda: selectPoints()).place(relx=0.70, y=starting)
        starting += 20
    current_points_label = Label(window, text=f'Current number of points: {cur_points.get()}')  # Etykieta wyświetlająca ilość wybranych punktów
    cur_points.set('MEDIUM')    # Ustawienie podstawowej wartości jako MEDIUM
    current_points_label.place(relx=0.70, y=170)

    cur_map = StringVar()   # Zmienna służąca do zapamiętania ustawionego typu mapy
    starting = 320
    for (text, file) in maps.items():   # Tworzenie radio przycisków do wyświetlania pojedynczych map
        Radiobutton(window, text=text, variable=cur_map, value=text, command=lambda: selectMap()).place(relx=0.70, y=starting)
        starting += 20
    cur_map.set('FINAL')    # Ustawienie podstawowego typu jako FINAL
    current_map_label = Label(window, text=f'Current map: {cur_map.get()}')  # Etykieta wyświetlająca typ wyświetlanej mapy
    current_map_label.place(relx=0.70, y=300)

    cur_blend = StringVar() # Zmienna służąca do zapamiętania czy należy mieszać granice biomów
    Radiobutton(window, text='YES', variable=cur_blend, value='YES', command=lambda: selectBlend()).place(relx=0.7, y=120)
    Radiobutton(window, text='NO', variable=cur_blend, value='NO', command=lambda: selectBlend()).place(relx=0.7, y=140)
    cur_blend.set('YES')    # Ustawienie podstawowego typu jako 'YES'
    current_blend_label = Label(window, text=f'Biome blend: {cur_blend.get()}') # Etykieta wyświetlająca aktualną opcję mieszania się biomów
    current_blend_label.place(relx=0.7, y=100)

    window.resizable(width=False, height=False) # Zablokowanie możliwości zmiany rozmiarów okna

    window.mainloop()


if __name__ == "__main__":
    main()