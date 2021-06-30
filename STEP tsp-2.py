#!/usr/bin/env python3

import sys
import math

from multiprocessing import Pool

from common import print_tour, read_input


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def divide(cities):
    N = len(cities)
    x_l, x_r = min(cities, key=lambda x: x[0])[0], max(cities, key=lambda x:x[0])[0]
    y_d, y_u = min(cities, key=lambda x: x[1])[1], max(cities, key=lambda x:x[1])[1]
    cen_x = (x_l+x_r)/2
    cen_y = (y_u+y_d)/2
    space_1, space_2, space_3, space_4 = [],[],[],[]
    for i in range(N):
        x,y = cities[i]
        if x >= cen_x and y >= cen_y:
            space_1.append([i,x,y])
        elif x <= cen_x and y >= cen_y:
            space_2.append([i,x,y])
        elif x >= cen_x and y <= cen_y:
            space_3.append([i,x,y])
        else:
            space_4.append([i,x,y])
    return space_1, space_2, space_3, space_4

def solve(cities):
    N = len(cities)
    if N==0:
        return []
    elif N==1:
        return [cities[0][0]]
    cities_ = [[x,y] for [_,x,y] in cities]

    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities_[i], cities_[j])

    current_city = 0
    unvisited_cities = set(range(1,N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city

    while True:
        swap = 0
        for i in range(len(tour)-1):
            for j in range(i+1,len(tour)):
                if j==len(tour)-1:
                    j = -1
                if dist[tour[i]][tour[i+1]] + dist[tour[j]][tour[j+1]] \
                    > dist[tour[i]][tour[j]] + dist[tour[i+1]][tour[j+1]]:
                    swap += 1
                    if j!=-1:
                        tour_before = tour[:i+1]
                        tour_cen = tour[i+1:j+1]
                        tour_end = tour[j+1:]
                        tour = tour_before+tour_cen[::-1]+tour_end
                    else:
                        tour_before = tour[:i+1]
                        tour_cen = tour[i+1:]
                        tour = tour_before + tour_cen[::-1]
        if swap==0:
            break
    tour = [cities[i][0] for i in tour]
    return tour

def find_exchange(t1,t2,cities):
    N1,N2 = len(t1),len(t2)
    D = float('inf')
    for i in range(N1):
        for j in range(N2):
            if i==N1-1:
                i = -1
            if j==N2-1:
                j = -1
            if distance(cities[t1[i]], cities[t2[j]])+distance(cities[t1[i+1]], cities[t2[j+1]])<D:
                D = distance(cities[t1[i]], cities[t2[j]])+distance(cities[t1[i+1]], cities[t2[j+1]])
                pt = [i,j]
            # elif distance(t1[i], t2[j+1])+distance(t1[i+1], t2[j])<D:
            #     D = distance(t1[i], t2[j+1])+distance(t1[i+1], t2[j])
            #     pt = [[i,j+1],[i,j]]
    return pt

if __name__ == '__main__':
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    processer = Pool(4)
    # 4領域に分割
    space_1, space_2, space_3, space_4 = divide(cities)
    # 4箇所で最短探索を並列処理
    tour1, tour2, tour3, tour4 = processer.map(solve, [space_1, space_2, space_3, space_4])
    tour = []
    #近いやつを見つける、近いやつが何番目の点かを見つけるそこで取り替える
    pt = find_exchange(tour1,tour2,cities)
    tour = tour1[:pt[0]+1]+tour2[:pt[1]+1][::-1]+tour2[pt[1]+1:][::-1]+tour1[pt[0]+1:]
    pt = find_exchange(tour,tour3,cities)
    tour = tour[:pt[0]+1]+tour3[:pt[1]+1][::-1]+tour3[pt[1]+1:][::-1]+tour[pt[0]+1:]
    pt = find_exchange(tour,tour4,cities)
    tour = tour[:pt[0]+1]+tour4[:pt[1]+1][::-1]+tour4[pt[1]+1:][::-1]+tour[pt[0]+1:]

    print_tour(tour)

    with open('output_'+sys.argv[1].split('.')[0][-1]+'.csv', mode='w') as f:
        f.write('index\n')
        for t in tour:
            f.write(str(t)+'\n')