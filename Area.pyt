import arcpy
import math
from math import radians, cos, sin, asin, sqrt
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
	filled_points_len = -1
	new_filled_points_len = 0
	# Default values
	x_number = 200
	y_number = 200
	i = 0

	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Tool"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):
		param0 = arcpy.Parameter(
			displayName="Start point X coordinate",
			name="x0",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param0.value = 117
			
		param1 = arcpy.Parameter(
			displayName="Start point Y coordinate",
			name="y0",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")
			
		param1.value = 56

		param2 = arcpy.Parameter(
			displayName="Grid pitch",
			name="delta",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")

		param2.value = 0.0008

		param3 = arcpy.Parameter(
			displayName="Terrain heights file",
			name="file",
			datatype="DEFile",
			parameterType="Required",
			direction="Input")

		param4 = arcpy.Parameter(
			displayName="Total volume",
			name="total_v",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")

		param4.value = 1000

		param5 = arcpy.Parameter(
			displayName="Elemental volume",
			name="delta_v",
			datatype="GPDouble",
			parameterType="Required",
			direction="Input")

		param5.value = 1

		param6 = arcpy.Parameter(
			displayName="Points number X-axis",
			name="x_number",
			datatype="GPLong",
			parameterType="Required",
			direction="Input")

		param6.value = 200

		param7 = arcpy.Parameter(
			displayName="Points number Y-axis",
			name="y_number",
			datatype="GPLong",
			parameterType="Required",
			direction="Input")

		param7.value = 200
			
		return [
			param0,
			param1,
			param2,
			param3,
			param4,
			param5,
			param6,
			param7
		]

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

		for x in range(self.x_number + 1):
			points[x] = {}
			for y in range(self.y_number + 1):
				result = arcpy.GetCellValue_management(str(file), str(startX+delta*(x - self.x_number/2)) + " " + str(startY+delta*(y - self.y_number/2)))
				height = int(result.getOutput(0))
				point = {
					"coord" : {"x" : startX+delta*(x - self.x_number/2), "y" : startY+delta*(y - self.y_number/2)},
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
		self.filled_points_len = self.new_filled_points_len
		self.new_filled_points_len = self.points_count(filled_points)

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

		if self.filled_points_len == self.new_filled_points_len:
			self.draw_all_points(all_points)
			self.draw_neighbor_points(neighbors)
			return filled_points
		new_filled_points = self.filled_points(all_points, filled_points, total_v, delta_v)

		return new_filled_points

	def draw_all_points(self, points):
		"""
		Отрисовывает точки на карте
		:param points: массив(словарь) точек
		:return:
		"""
		fc = "C:/arc/My/DB.gdb/point/all_points"
		cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
		for x in points:
			for y in points[x]:
				xy = (points[x][y]["coord"]["x"], points[x][y]["coord"]["y"])
				cursor.insertRow([xy])


	def draw_filled_points(self, points):
		"""
		Отрисовывает точки на карте
		:param points: массив(словарь) точек
		:return:
		"""
		fc = "C:/arc/My/DB.gdb/point/filled_points"
		cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
		for x in points:
			for y in points[x]:
				xy = (points[x][y]["coord"]["x"], points[x][y]["coord"]["y"])
				cursor.insertRow([xy])

	def draw_neighbor_points(self, points):
		"""
		Отрисовывает точки на карте
		:param points: массив(словарь) точек
		:return:
		"""
		fc = "C:/arc/My/DB.gdb/point/neighbor_points"
		cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
		for x in points:
			for y in points[x]:
				xy = (points[x][y]["coord"]["x"], points[x][y]["coord"]["y"])
				cursor.insertRow([xy])

	def points_count(self, points):
		i = 0
		for x in points:
			for y in points[x]:
				i = i + 1
		return i

	def haversine(self, lon1, lat1, lon2, lat2):
		"""
        По формуле гаверсинусов считает расстояние в километрах
        между двумя точками по их десятичным координатам
        """
		# convert decimal degrees to radians
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		# haversine formula
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
		c = 2 * asin(sqrt(a))
		r = 6371  # Radius of earth in kilometers. Use 3956 for miles
		return c * r

	def execute(self, parameters, messages):
		sys.setrecursionlimit(10000)

		start_x_coord = parameters[0].value
		start_y_coord = parameters[1].value
		delta = parameters[2].value
		file = parameters[3].value
		total_v = parameters[4].value
		delta_v = parameters[5].value
		self.x_number = parameters[6].value
		self.y_number = parameters[7].value
		if self.x_number % 2 == 1:
			self.x_number = self.x_number + 1
		if self.y_number % 2 == 1:
			self.y_number = self.y_number + 1
		start_x = self.x_number / 2
		start_y = self.y_number / 2

		all_points = self.heightGrid(start_x_coord, start_y_coord, delta, file)
		self.draw_all_points(all_points)
		filled_points = {start_x:{}}
		filled_points[start_x][start_y] = all_points[start_x][start_y]

		filled_points = self.filled_points(all_points, filled_points, total_v, delta_v)
		self.draw_filled_points(filled_points)

		delta_km = self.haversine(0, 0, 0, delta)
		one_point_area = delta_km * delta_km
		total_area = one_point_area * self.points_count(filled_points)

		arcpy.AddMessage("Total area:")
		arcpy.AddMessage(total_area)

		return

	###
#
#  На последнем этипе перед выходом из цикла, посмотреть соседей всех заполненных точек
#  и понять почему они не заполняются (и соответствуют ли реальным соседям)
#
# Почему-то
##

