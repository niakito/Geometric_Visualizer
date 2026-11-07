''''
Geometric Algorithm Visualizer
Voronoi, Delaunay, Convex Hull

    Input:  
     · pointset: A set of points, where each point p = (x,y) represents the 2D coordinates. 
     · algorithm: String specifying the algorithm to execute (VOR, DEL, CH)
     
    Output:
     · A visual representation of the chosen algorithm applied to the input points.
'''


# libraries
import cv2 as cv
import numpy as np
from typing import Literal

# point type
type Point = tuple[int, int]


# algorithms implementation

def convex_hull(vertex, display):
    hull = cv.convexHull(vertex)
    cv.polylines(display, [hull], isClosed=True, color=(0, 255, 0), thickness=2)


def voronoi(display, subdiv):
    facets, centers = subdiv.getVoronoiFacetList([])

    for fc in facets:
        facet_pts = np.array(fc, dtype=np.int32).reshape((-1, 1, 2))
        
        # fill the polygon w an aleatory color
        color = np.random.randint(50, 230, size=3).tolist()
        cv.fillConvexPoly(display, facet_pts, color)
        
        cv.polylines(display, [facet_pts], isClosed=True, color=(255, 255, 255), thickness=2)


def delaunay(display, subdiv, width, height):
    triangles = subdiv.getTriangleList()
    pts = np.array(triangles, dtype=np.int32).reshape(-1, 2) # n rows & 2 columns (n tuples)

    # verify that each vertex is contained within the canva
    for t in triangles:
        pts = np.array(t, dtype=np.int32).reshape(3, 2) # 3 vertex, 2 coordinates f.each one

        inside = True
        for p in pts:
            if p[0] < 0 or p[0] >= width or p[1] < 0 or p[1] >= height:
                inside = False
                break

        if inside:
            cv.polylines(display, [pts], isClosed=True, color=(130, 230, 210), thickness=2)


# main block
def visualizer(pointset: list[Point], algorithm: Literal["CH", "VOR", "DEL"]) -> None:

    # create canvas to display the results
    height, width = 600, 600
    canvas = np.zeros((height, width, 3), dtype=np.uint8)

    # initialize subdiv2D
    subdiv = cv.Subdiv2D((0, 0, width, height))
    for pnt in pointset:
        subdiv.insert(pnt)

    
    if algorithm == "CH":
        # convert list to numpy array, to match opencv point format (N, 1, 2) & int32
        points = np.array(pointset, dtype=np.int32).reshape((-1, 1, 2))
        convex_hull(points, canvas)
        
    if algorithm == "VOR":
        voronoi(canvas, subdiv)
    
    elif algorithm == "DEL":
        delaunay(canvas, subdiv, width, height)


    # draw the set of points on the canvas
    point_color = (230, 130, 150)
    for pnt in pointset:
        cv.circle(canvas, pnt, radius=4, color=point_color, thickness=-1)

    cv.imshow("Visualizer", canvas)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    np.random.seed(42)
    sample_points = [(int(x), int(y)) for x, y in np.random.randint(50, 550, size=(25, 2))]
    visualizer(sample_points, "DEL")