try:
    # Python2
    import Tkinter as tk

except ImportError:
    # Python3
    import tkinter as tk



from collections import namedtuple
import math
import sys


EPSILON = math.sqrt(sys.float_info.epsilon)
Point = namedtuple('Point', ['x', 'y'])



##########################triangulare
def earclip_triangulation(polygon):
    ear_vertex = []
    triangles = []

    polygon = [Point(*point) for point in polygon]

    if is_clockwise(polygon):
        polygon.reverse()         #ordoneaza poligonul

    point_count = len(polygon)
    for i in range(point_count):

        prev_point = polygon[i - 1]
        point = polygon[i]
        next_point = polygon[(i + 1) % point_count]

        if is_ear(prev_point, point, next_point, polygon):  #ia fiecare punct si verif daca e varf al unei urechi
            ear_vertex.append(point)

    while ear_vertex and point_count >= 3:
        ear = ear_vertex.pop(0)
        i = polygon.index(ear)

        prev_point = polygon[i - 1]
        next_point = polygon[(i + 1) % point_count]

        polygon.remove(ear)
        point_count -= 1
        triangles.append(((prev_point.x, prev_point.y), (ear.x, ear.y), (next_point.x, next_point.y)))
        if point_count > 3:
            prev_prev_point = polygon[i - 2]

            next_next_point = polygon[(i + 1) % point_count]

            groups = [
                (prev_prev_point, prev_point, next_point, polygon),
                (prev_point, next_point, next_next_point, polygon),
            ]
            for group in groups:
                p = group[1]
                if is_ear(*group):
                    if p not in ear_vertex:
                        ear_vertex.append(p)
                elif p in ear_vertex:
                    ear_vertex.remove(p)
    return triangles

#https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
def is_clockwise(polygon):
    s = 0
    polygon_count = len(polygon)
    for i in range(polygon_count):
        point = polygon[i]
        point2 = polygon[(i + 1) % polygon_count]
        s += (point2.x - point.x) * (point2.y + point.y)

    return s > 0


def is_convex(prev, point, next):
    return triangle_sum(prev.x, prev.y, point.x, point.y, next.x, next.y) < 0


def is_ear(p1, p2, p3, polygon):
    ear = contains_no_points(p1, p2, p3, polygon) and \
          is_convex(p1, p2, p3) and \
          triangle_area(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y) > 0
    return ear


def contains_no_points(p1, p2, p3, polygon):
    for pn in polygon:
        if pn in (p1, p2, p3):
            continue
        elif is_point_inside(pn, p1, p2, p3):
            return False
    return True


def is_point_inside(p, a, b, c):
    area = triangle_area(a.x, a.y, b.x, b.y, c.x, c.y)
    area1 = triangle_area(p.x, p.y, b.x, b.y, c.x, c.y)
    area2 = triangle_area(p.x, p.y, a.x, a.y, c.x, c.y)
    area3 = triangle_area(p.x, p.y, a.x, a.y, b.x, b.y)
    areadiff = abs(area - sum([area1, area2, area3])) < EPSILON
    return areadiff


def triangle_area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)


def triangle_sum(x1, y1, x2, y2, x3, y3):
    return x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)

######################################

#                  A.x,A.y,B.x,B.y,x,y
def point_check(a, b, c, d, x, y):
    if a > c:
        maxx = a
        minx = c
    else:
        maxx = c
        minx = a
    if b > d:
        maxy = b
        miny = d
    else:
        maxy = d
        miny = b
    if x >= minx and x <= maxx:
        if y >= miny and y <= maxy:
            return True
    return False


def is_intersecting(A, B, C, D):
    # Primeste 4 puncte
    # ele formeaza segmentul (a,b)---(c,d)  si segmentul (x,y)---(z,t)
    # apoi returneza true daca se intersecteaza
    L_flag = True
    if A == C or B == D or A == D or B == C:
        L_flag = False

    a, b = A
    c, d = B
    x, y = C
    z, t = D
    a1 = b - d
    b1 = c - a
    c1 = (a * d) - (c * b)
    a2 = y - t
    b2 = z - x
    c2 = (x * t) - (z * y)

    det = (a1 * b2) - (b1 * a2)
    if det != 0:
        detx = ((-c1) * b2) - ((-c2) * b1)
        x1 = detx / det
        dety = (a1 * (-c2)) - (a2 * (-c1))
        y1 = dety / det
        if point_check(a, b, c, d, x1, y1) == 1 and point_check(x, y, z, t, x1, y1) == 1:
            return True and L_flag
        else:
            return False
    else:
        detm1 = (a1 * c2) - (a2 * c1)
        detm2 = (b1 * c2) - (b2 * c1)
        if detm1 == 0 and detm2 == 0:
            if b == y:
                x2 = max(a, c)
                x3 = min(x, t)
                if x3 < x2:
                    return True and L_flag
                else:
                    return False
        else:
            return False

def is_simple(polygon):
    point_count = len(polygon)
    for i in range(point_count-1):
        for j in range(i,point_count):
            if is_intersecting(polygon[i - 1], polygon[i], polygon[j - 1], polygon[j]):
                return False
    return True


def distance(p1, p2):
    return math.sqrt(((p1.x - p2.x) ** 2) + ((p1.y - p2.y) ** 2))

def point_on_line(p1, p2, a):
    if distance(p1, a) + distance(a, p2) - distance(p1, p2) < EPSILON:
        return True
    return False

class PointInPolygon(object):
    def __init__(self, root):
        self._root = root
        self._canvas = self.createCanvas()
        self.list_of_points = [] #punctele poligonului
        self.cool_point = namedtuple('Point', ['x', 'y'])


    def createCanvas(self):
        canvas = tk.Canvas(self._root, height=1000, width=1000, bg='black')     #canvas widget h 1000 w 1000
        canvas.pack()   #adaug widgetul in fereastra
        canvas.bind("<Button 1>", self.draw_polygon)    #mouse events
        canvas.bind("<Button 3>", self.draw_point)
        self._root.bind('<Motion>', self.motion)    #afisez coordonatele
        return canvas

    def motion(self, event):
        x, y = event.x, event.y
        s = "x=%s  y=%s" % (x, y)
        self._root.title(s)

    def draw_point(self, event):

        self.cool_point.x = event.x
        self.cool_point.y = event.y

        self._canvas.create_oval(event.x, event.y, event.x, event.y, fill='white', outline='red', width=5)
        #opresc mouse events
        self._canvas.bind("<Button 1>", "")
        self._canvas.bind("<Button 3>", "")
        if len(self.list_of_points) >= 3 and is_simple(self.list_of_points):
            self.find_point()
        else:
            print("Nu e voie frate")


    def draw_polygon(self, event):

        x, y = event.x, event.y
        self._canvas.delete("all")

        self.list_of_points.append((x, y))

        # adauga punctul in lista
        numberofPoint = len(self.list_of_points)

        # afiseaza poly

        if numberofPoint > 3:
            self._canvas.create_polygon(self.list_of_points, fill='gray', outline='white', width=2)

        elif numberofPoint == 3:
            self._canvas.create_polygon(self.list_of_points, fill='gray', outline='white', width=2)

        elif numberofPoint == 2:

            self._canvas.create_line(self.list_of_points, fill="white", width=2)
        else:
            self._canvas.create_oval(x, y, x, y, fill='white', outline='white', width=2)

        #print(self.list_of_points)

    def draw_line(self, line):
        self._canvas.create_line(line, fill="green", width=3)

    def draw_triangle(self, triangle, color):
        self._canvas.create_polygon(triangle, fill='', outline=color, width=2)



    def find_point(self):

        #triangulare
        triangles = earclip_triangulation(self.list_of_points)

        #afiseaza triunghiurile
        for triangle in triangles:
            self.draw_triangle(triangle,"red")

        self.list_of_points = [Point(*point) for point in self.list_of_points]
        print(self.list_of_points)
        point_count = len(self.list_of_points)

        latura_detectata=False
        #verifica laturile poligonului
        for i in range(point_count):
            point1 = self.list_of_points[i-1]
            point2 = self.list_of_points[i]
            if point_on_line(point1, point2, self.cool_point):
                self.draw_line([point1, point2])
                print("Avem latura detectata frate", [self.list_of_points[i-1], self.list_of_points[i]])
                latura_detectata=True


        #verifica fiecare triunghi
        if latura_detectata == False:
            for triangle in triangles:
                pointA = namedtuple('Point', ['x', 'y'])
                pointB = namedtuple('Point', ['x', 'y'])
                pointC = namedtuple('Point', ['x', 'y'])

                pointA.x, pointA.y = triangle[0][0], triangle[0][1]
                pointB.x, pointB.y = triangle[1][0], triangle[1][1]
                pointC.x, pointC.y = triangle[2][0], triangle[2][1]

                if is_point_inside(self.cool_point, pointA, pointB, pointC):
                    print("Avem triunghi detectat frate ", triangle)
                    self.draw_triangle(triangle, "green")



def main():
    #creez window
    root = tk.Tk()
    #master widget
    pip = PointInPolygon(root)
    root.mainloop()


if  __name__ == '__main__':
    main()





