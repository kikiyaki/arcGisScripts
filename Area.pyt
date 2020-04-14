import arcpy
import math
import time
import sys

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
    #Define parameter definitions
    # First parameter
		param0 = arcpy.Parameter(
			displayName="V",
			name="vol",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param0.value=5
			
		param1 = arcpy.Parameter(
			displayName="h",
			name="h",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param1.value=5
		
		param2 = arcpy.Parameter(
			displayName="delta R",
			name="Radius increment",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param2.value=5
			
		return [param0, param1, param2]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def max_height(self, points):
		"""
		Находит максимальную высоту массива точек
		:param points: массив(словарь) точек
		:return:
		"""
		max_height = -1000000.
		for x in points:
			for y in points[x]:
				if points[x][y]["height"] > max_height:
					max_height = points[x][y]["height"]
		return max_height

    def heightGrid(self, startX, startY, delta, file):
		"""
		Возвращает двумерный массив(словарь) точек вида:
		grid[i][k] = {
						"coord" : {"x" : xCoord, "y" : yCoord},
						"height" : pointHeight
					  }
		i - порядковый номер точки по оси X
		k - порядковый номер точки по оси Y

		:param startX: :param startY: начальные координаты точки, вокруг которой строится массив точек
		:param delta: промежуток между точками в градусах координат
		:param file: полный путь к файлу из которого берутся высоты
		"""
		points = {}
		
		for x in range(41):
			points[x] = {}
			for y in range(41):
				result = arcpy.GetCellValue_management(file, str(startX+delta*(x-20)) + " " + str(startY+delta*(y-20)))
				height = int(result.getOutput(0))
				point = {
					"coord" : {"x" : startX+delta*(x-20), "y" : startY+delta*(y-20)},
					"height" : height
					}
				points[x][y] = point

		return points

    def neighborsFromDict(self, points, all_points):
		"""
		Возвращает массив(словарь) точек-соседей для массива точек
		Точки для которых ищем соседей не попадают в массив соседей
		:param points: массив точек вокруг которых ищем соседей
		:param all_points: массив точек в которых ищем соседей
		:return:
		"""
		neighbors = {}
		for x in points:
			for y in points[x]:
				current_point_neighbors = self.neighbors(x, y, all_points)
				for cur_x in current_point_neighbors:
					for cur_y in current_point_neighbors[cur_x]:
						#Добавить точку-соседа только если она не входит в массив точек, вокруг которых ищем соседей
						if cur_x not in points:
							if cur_x not in neighbors:
								neighbors[cur_x] = {}
							neighbors[cur_x][cur_y] = current_point_neighbors[cur_x][cur_y]
						else:
							if cur_y not in points[cur_x]:
								if cur_x not in neighbors:
									neighbors[cur_x] = {}
								neighbors[cur_x][cur_y] = current_point_neighbors[cur_x][cur_y]


		return neighbors

    def neighbors(self, x, y, points):
		"""
		Возвращает массив(словарь) четырех точек-соседей
		:param x: порядковый номер точки по оси X
		:param y: порядковый номер точки по оси Y
		:param points: массив точек в которых ищем соседей
		"""
		neighbors = {}

		neighbors[x-1] = {}
		neighbors[x] = {}
		neighbors[x+1] = {}

		if (x-1) in points:
			if y in points[x-1]:
				neighbors[x - 1][y] = points[x - 1][y]

		if x in points:
			if (y+1) in points[x]:
				neighbors[x][y+1] = points[x][y+1]

		if (x+1) in points:
			if y in points[x+1]:
				neighbors[x+1][y] = points[x+1][y]

		if x in points:
			if y-1 in points[x]:
				neighbors[x][y-1] = points[x][y-1]

		if neighbors[x-1] == {}:
			del neighbors[x-1]
		if neighbors[x] == {}:
			del neighbors[x]
		if neighbors[x+1] == {}:
			del neighbors[x+1]
		
		return neighbors

    def filled_points(self, all_points, filled_points, total_v, delta_v):
		"""
		Возвращает массив(словарь) заполненных жидкостью точек
		:param all_points: массив всех определенных точек пространства
		:param filled_points: массив изначально заполненных точек
		:param total_v: общий объем растекаемой жидкости
		:param delta_v: объем, который вмещает одна клетка(точка)
		:return:
		"""
		max_filled_height = self.max_height(filled_points)
		neighbors = self.neighborsFromDict(filled_points, all_points)
		for x in neighbors:
			for y in neighbors[x]:
				height = neighbors[x][y]["height"]
				if total_v <= 0:
					return filled_points
				else:
					if height <= max_filled_height:
						#Заполнение точки
						if x not in filled_points:
							filled_points[x] = {}
						filled_points[x][y] = neighbors[x][y]
						del all_points[x][y]
						total_v = total_v - delta_v
		return self.filled_points(all_points, filled_points, total_v, delta_v)

    def print_points(self, points):
		"""
		Отладочная функция
		Выводит в сообщения точки в виде:
		|x-y-height|
		|0-0-1000||1-0-1200|
		|0-1-1900||1-1-1300|
		:param points:
		:return:
		"""
		max_x = 0
		max_y = 0
		for x in points:
			if x > max_x:
				max_x = x
			for y in points[x]:
				if y > max_y:
					max_y = y
		arcpy.AddMessage("Print points:+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		for x in range(0, max_x + 1):
			row = ""
			for y in range(0, max_y + 1):
				point_not_exist = True
				if x in points:
					if y in points[x]:
						point_not_exist = False
						row = \
							row \
							+ "|" \
							+ str.rjust(str(x), 3, "0") \
							+ "-" \
							+ str.rjust(str(y), 3, "0") \
							+ "-" \
							+ str.rjust(str(points[x][y]["height"]), 4, "0") \
							+ "|"
				if point_not_exist:
					row = row + "|xxx-xxx-xxxx|"
			arcpy.AddMessage(row)


    def draw_points(self, points):
		"""
		Отрисовывает точки на карте
		:param points: массив(словарь) точек
		:return:
		"""
		fc = "C:/arc/My/DB.gdb/point/points"
		cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
		for x in points:
			for y in points[x]:
				xy = (points[x][y]["coord"]["x"], points[x][y]["coord"]["y"])
				cursor.insertRow([xy])

    def execute(self, parameters, messages):

		sys.setrecursionlimit(2000)

		startX = 117
		startY = 56
		delta = 0.007
		file = "C:/arc/srtm_60_01/srtm_60_01.tif"
		'''
		Точки для тестирования(сейчас не используются)
		all_points = {2:{2:{"height": 60}, 3:{"height": 70}, 4:{"height": 80}, 5:{"height": 60}},
					  3:{2:{"height": 60}, 3:{"height": 110}, 4:{"height": 100}, 5:{"height": 80}},
					  4:{2:{"height": 60}, 3:{"height": 80}, 4:{"height": 110}, 5:{"height": 80}},
					  5:{2:{"height": 50}, 3:{"height": 60}, 4:{"height": 60}, 5:{"height": 60}}}
		filled_points = {3:{4:{"height": 100}}}
		'''

		all_points = self.heightGrid(startX, startY, delta, file)
		self.print_points(all_points)
		#filled_points = {20:{}}
		#filled_points[20][20] = all_points[20][20]
		#total_v = 20
		#delta_v = 1
		#filled_points = self.filled_points(all_points,filled_points,total_v,delta_v)
		#arcpy.AddMessage(filled_points)
		#self.draw_points(filled_points)

		return
