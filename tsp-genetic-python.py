'''
Genetic Algorithm for the Travelling Salesman Problem
'''

import random
import copy
import os
import time

from tkinter import *
from tkinter.ttk import *

list_of_cities =[]
mut_prob=0.4
population_size=40
num_generations=200
tournament_size=7

# Якщо значення істинне , найращий з кожного покоління перенесеться у наступне
elitism = True

# City class
class City(object):
    def __init__(self, name, x, y, distance_to=None):
        # Назви та координати :
        self.name = name
        self.x = self.graph_x = x
        self.y = self.graph_y = y
        # Додає екземпляр до глобального списку міст :
        list_of_cities.append(self)
        # Створює словник відстаней до всіх інших міст
        self.distance_to = {self.name:0.0}
        if distance_to:
            self.distance_to = distance_to

    def calculate_distances(self):
        for city in list_of_cities:
            tmp_dist = self.point_dist(self.x, self.y, city.x, city.y)
            self.distance_to[city.name] = tmp_dist

    # Обчислює вістань міє двома координатами
    def point_dist(self, x1,y1,x2,y2):
        return ((x1-x2)**2 + (y1-y2)**2)**(0.5)


# Route Class
class Route(object):

    def __init__(self):
        # Ініціалізує атрибут шляху рівний випадково посортованому списку міст
        self.route = sorted(list_of_cities, key=lambda *args: random.random())
        # Обраховує свою довжину:
        self.recalc_rt_len()

    def recalc_rt_len(self):
        # Обнуляємо свою довжину
        self.length = 0.0
        # Для кожного міста в атрибуті шляху:
        for city in self.route:
            # Встановлює змінну наступного міста з списку :
            next_city = self.route[self.route.index(city)-len(self.route)+1]
            # Використовує пурший атрибут відстані distance_to щоб знайти відстань до наступного міста(точки):
            dist_to_next = city.distance_to[next_city.name]

            # Додає довжину даного ребрага до загального шляху
            self.length += dist_to_next

    def pr_cits_in_rt(self, print_route=False):
        for city in self.route:
            print(city.name)

    def pr_vrb_cits_in_rt(self):
        cities_str = '|'
        for city in self.route:
            cities_str += str(city.x) + ',' + str(city.y) + '|'
        print(cities_str)

    def is_valid_route(self):
        for city in list_of_cities:
            # Допоміжна функція яка перевіряє валідність шляху
            if self.count_mult(self.route,lambda c: c.name == city.name) > 1:
                return False
        return True

    # Повертає число пройдених ребер у кінці шляху
    def count_mult(self, seq, pred):
        return sum(1 for v in seq if pred(v))


# Містить популяцію об'єктів Route()
class RoutePop(object):
    def __init__(self, size, initialise):
        self.rt_pop = []
        self.size = size
        # Якщо ми ініціалізуємо population.rt_pop:
        if initialise:
            for x in range(0,size):
                new_rt = Route()
                self.rt_pop.append(new_rt)
            self.get_fittest()

    def get_fittest(self):
        # сортування списку відповідно до довжин шляхів
        sorted_list = sorted(self.rt_pop, key=lambda x: x.length, reverse=False)
        self.fittest = sorted_list[0]
        return self.fittest


# Клас методів необхідних для  Генетичного алгоритму
class GA(object):
    def crossover(self, parent1, parent2):
        # Новий нащадок Route()
        child_rt = Route()

        for x in range(0,len(child_rt.route)):
            child_rt.route[x] = None

        # Обираємо два випадкові індекси:
        start_pos = random.randint(0,len(parent1.route))
        end_pos = random.randint(0,len(parent1.route))


        # Бере підмаршрут від одного батька і запихає його у себе :
        # Якщо початковий індекс менший індексу кіньця:
        if start_pos < end_pos:
            # Порядок поч. --> кінець.
            for x in range(start_pos, end_pos):
                child_rt.route[x] = parent1.route[x]
        # Якщо початковий індекс більший індексу кіньця:
        elif start_pos > end_pos:
            # Порядок кінець. --> почат.
            for i in range(end_pos, start_pos):
                child_rt.route[i] = parent1.route[i]


        # Проходить циклом по 2 батьку і наповнює маршрут нащадка
        # Проходить циклом по довжині 2-го батька:
        for i in range(len(parent2.route)):
            # Якщо 2 батько має місто якого ще не має :
            if not parent2.route[i] in child_rt.route:
                # Елемент встановлюється на перше пусте місце і виходить з циклу.
                for x in range(len(child_rt.route)):
                    if child_rt.route[x] == None:
                        child_rt.route[x] = parent2.route[i]
                        break
        # Повторити доки всі міста не будуть в маршруті нащадка

        # Повертає обєкт Route() нащадка
        child_rt.recalc_rt_len()
        return child_rt

    def mutate(self, route_to_mut):
        # k_mut_prob Ймовірність мутації :
        if random.random() < mut_prob:

            # Два випадкові індекси:
            mut_pos1 = random.randint(0,len(route_to_mut.route)-1)
            mut_pos2 = random.randint(0,len(route_to_mut.route)-1)

            # Якщо індекси однакові маршрут НЕ мутує
            if mut_pos1 == mut_pos2:
                return route_to_mut

            # В іншому випадку міняємо місцями елементи під індексами :
            city1 = route_to_mut.route[mut_pos1]
            city2 = route_to_mut.route[mut_pos2]

            route_to_mut.route[mut_pos2] = city1
            route_to_mut.route[mut_pos1] = city2

        # Перерахуємо довжини маршрутів
        route_to_mut.recalc_rt_len()

        return route_to_mut


    def tournament_select(self, population):
        # Нова менша популяція
        tournament_pop = RoutePop(size=tournament_size, initialise=False)

        # Наповнює популяцію випадковими значеннми (можуть бути дублікати)
        for i in range(tournament_size-1):
            tournament_pop.rt_pop.append(random.choice(population.rt_pop))
        
        # повертає найбільш придатний:
        return tournament_pop.get_fittest()

    def evolve_population(self, init_pop):
        #Створення нової популяції:
        descendant_pop = RoutePop(size=init_pop.size, initialise=True)

        # Зміщення найкращих представників (кількість об'єктів Routes() переноситься до нової популяції)
        elitismOffset = 0

        # Якщо значення істинне , встановлюєм замість першого елементу нащадка , найкращий батьківський ел.
        if elitism:
            descendant_pop.rt_pop[0] = init_pop.fittest
            elitismOffset = 1

        # Проходить через нову популяцію і наповняє її двума переможцями турніру з минулої популяції
        for x in range(elitismOffset,descendant_pop.size):
            # Два батьки:
            tournament_parent1 = self.tournament_select(init_pop)
            tournament_parent2 = self.tournament_select(init_pop)

            # Нащадок:
            tournament_child = self.crossover(tournament_parent1, tournament_parent2)

            # Наповнення популяції нащадками
            descendant_pop.rt_pop[x] = tournament_child

        # Мутує кожен маршрут  (
        for route in descendant_pop.rt_pop:
            if random.random() < mut_prob:
                self.mutate(route)

        # Оновлюємо найкращий маршрут :
        descendant_pop.get_fittest()

        return descendant_pop

class App(object):

    def __init__(self,n_generations,pop_size, graph=False):
        self.n_generations = n_generations
        self.pop_size = pop_size
        # Обраховуємо відстані між містами
        if graph:
            self.set_city_gcoords()
            # Ініціалізується вікно з своїм тайтлом
            self.window = Tk()
            self.window.wm_title("Generation 0")

            # Ініціалізується дві площини з поточним маршрутом , і з найкращим
            self.canvas_current = Canvas(self.window, height=300, width=300)
            self.canvas_best = Canvas(self.window, height=300, width=300)

            #  Ініціалізується дві назви
            self.canvas_current_title = Label(self.window, text="Best route of current gen:")
            self.canvas_best_title = Label(self.window, text="Overall best so far:")

            # Ініціалізується рядок стану
            self.stat_tk_txt = StringVar()
            self.status_label = Label(self.window, textvariable=self.stat_tk_txt, relief=SUNKEN, anchor=W)

            # Створює точки на обох полотнах
            for city in list_of_cities:
                self.canvas_current.create_oval(city.graph_x-2, city.graph_y-2, city.graph_x + 2, city.graph_y + 2, fill='blue')
                self.canvas_best.create_oval(city.graph_x-2, city.graph_y-2, city.graph_x + 2, city.graph_y + 2, fill='blue')

            # Фізично створює всі вище визначені віджети
            self.canvas_current_title.pack()
            self.canvas_current.pack()
            self.canvas_best_title.pack()
            self.canvas_best.pack()
            self.status_label.pack(side=BOTTOM, fill=X)

            # Запускає цикл головного вікна
            self.window_loop(graph)
        else:
            print("Обрахування циклу ГА")
            self.GA_loop(n_generations,pop_size, graph=graph)

    def set_city_gcoords(self):
        # Визначення змінних (границі для координат)
        min_x = 100000
        max_x = -100000
        min_y = 100000
        max_y = -100000

        #знаходимо найменше та найбільше значення координат
        for city in list_of_cities:

            if city.x < min_x:
                min_x = city.x
            if city.x > max_x:
                max_x = city.x

            if city.y < min_y:
                min_y = city.y
            if city.y > max_y:
                max_y = city.y

        # Змінюємо граф так що найлівіше місце починається на координаті(0,0)
        for city in list_of_cities:
            city.graph_x = (city.graph_x + (-1*min_x))
            city.graph_y = (city.graph_y + (-1*min_y))

        # Відновлюємо значення змінних
        min_x = 100000
        max_x = -100000
        min_y = 100000
        max_y = -100000

        # знаходимо найменше та найбільше значення координат
        for city in list_of_cities:

            if city.graph_x < min_x:
                min_x = city.graph_x
            if city.graph_x > max_x:
                max_x = city.graph_x

            if city.graph_y < min_y:
                min_y = city.graph_y
            if city.graph_y > max_y:
                max_y = city.graph_y

        # Якщо координатна пряма х довше у, встановлюємо параметр розтягнення до 300 (px).
        # Це зберігає співідношення сторін
        if max_x > max_y:
            stretch = 300 / max_x
        else:
            stretch = 300 / max_y

        # Розтягуємо всі міста так що місто з найвищими координатами опиняється на верхньому краю графіка
        for city in list_of_cities:
            city.graph_x *= stretch
            city.graph_y = 300 - (city.graph_y * stretch)


    def update_canvas(self,the_canvas,the_route,color):
        # Видаляємо всім речі з тегом 'path'
        the_canvas.delete('path')

        # Цикл через маршрут
        for i in range(len(the_route.route)):
            next_i = i-len(the_route.route)+1
            # Створює пряму від міста до міста (ребро)
            the_canvas.create_line(the_route.route[i].graph_x,
                                the_route.route[i].graph_y,
                                the_route.route[next_i].graph_x,
                                the_route.route[next_i].graph_y,
                                tags=("path"),
                                fill=color)

            # Пакує і оновлює координ площину
            the_canvas.pack()
            the_canvas.update_idletasks()

    def GA_loop(self, n_generations, pop_size, graph=False):
        # Початок відліку часу виконання алгоритму
        start_time = time.time()

        # Створення популяції
        print("Створення популяції:")
        the_population = RoutePop(pop_size, True)
        print ("Створення популяції закінчене")

        #Перевірка на наявність дубльованих міст:
        if the_population.fittest.is_valid_route() == False:
            raise NameError('Multiple cities with same name. Check cities.')

        # отримує найращу довжину першой популяції (чисто для візуалізації)
        initial_length = the_population.fittest.length

        # Створюється випадково початковий найкращий маршрут
        best_route = Route()

        if graph:
            # Оновлення графіків:
            self.update_canvas(self.canvas_current,the_population.fittest,'red')
            self.update_canvas(self.canvas_best,best_route,'green')

        # Головний цикл алгоритму (для числа генерацій)
        for x in range(1,n_generations):
            # Оновлюємо графік кожні n генерацій
            # Updates the current canvas every n generations (to avoid it lagging out, increase n)
            if x % 5 == 0 and graph:
                self.update_canvas(self.canvas_current,the_population.fittest,'red')

            # Еволюція популяції:
            the_population = GA().evolve_population(the_population)

            # Якщо знайдений коротший маршрут записуєм його в best_route
            if the_population.fittest.length < best_route.length:
                # Встановлюємо маршрут
                best_route = copy.deepcopy(the_population.fittest)
                if graph:
                    # Оновлюємо другий графік(найкращий маршрут):
                    self.update_canvas(self.canvas_best,best_route,'green')
                    # Оновлюємо лінійку статусу
                    self.stat_tk_txt.set('Initial length {0:.2f} Best length = {1:.2f}'
                                         .format(initial_length,best_route.length))
                    self.status_label.pack()
                    self.status_label.update_idletasks()

            self.clear_term()
            if graph:
                # Змінюємо тайтл вікна відповідно до останньої генерації:
                self.window.wm_title("Generation {0}".format(x))
        if graph:
            # Змінюємо тайтл вікна відповідно до останньої генерації
            self.window.wm_title("Generation {0}".format(n_generations))

            # Змінюємо графік найкращого маршруту:
            self.update_canvas(self.canvas_best,best_route,'green')
            
        # ЗУпиняємо лічильник виконання алгоритму:
        end_time = time.time()

        # Видруковуємо фінальну інформацію :
        self.clear_term()
        print('Закінчено еволюцію {0} генерацій.'.format(n_generations))
        print("Час дії алгоритму {0:.1f} секунд.".format(end_time - start_time))
        print(' ')
        print('Початкова найкраща відстань: {0:.2f}'.format(initial_length))
        print(' ----- Кінцева найкраща відстань:   {0:.2f} ----- '.format(best_route.length))
        print('Порядок проходження вершин :\n')
        best_route.pr_cits_in_rt(print_route=True)

    def window_loop(self, graph):
        # Час між повторними викликами функції (атрибуту)
        self.window.after(0, self.GA_loop(self.n_generations, self.pop_size, graph))
        self.window.mainloop()

    # Очищення консольного вікна
    def clear_term(self):
        os.system('cls' if os.name=='nt' else 'clear')

##############################
#### Declare cities here: ####
##############################

def data_uploading():
    try:
        file = open("data/Data_Lviv_Hub.in", "r", encoding="utf8")
        lines = int(file.readline())
        cities = file.readline().split()
        x_coord = [float(i) for i in file.readline().split()]
        y_coord = [float(i) for i in file.readline().split()]
        for i, li in enumerate(file.readlines(), start=1):
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Зчитування '{}': {}/{} рядок".format(file.name, i, lines))
            cur_city = {}
            for j, line in enumerate(map(float, li.split()), start=1):
                cur_city[cities[j-1]] = line
            tmp = City(cities[i-1], x_coord[i-1], y_coord[i-1], cur_city)
        band = True
    except Exception as e:
        print(e)
        band = False
    if band:
        print("Пошук найкращого можливого маршруту...")
        start_time = time.time()
        try:
            App(n_generations=num_generations, pop_size=population_size, graph=True)
        except Exception as e:
            print("\n[ERROR]: %s\n" % e)
        finally:
            print("---Шлях знайдений за  %s секунд ---" % (time.time() - start_time))
if __name__ == '__main__':
    data_uploading()


