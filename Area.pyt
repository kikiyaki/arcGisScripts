import arcpy
import math
import time


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

    def heightGrid(self, startX, startY, delta, file):
		"""
		returns two diemensional array like:
		grid[i][k] = {
						"coord" : {"x" : xCoord, "y" : yCoord}, 
						"height" : pointHeight
					  }
		"""
		points = []
		
		for x in range(11):
			points.append([])
			for y in range(11):
				result = arcpy.GetCellValue_management("C:/arc/srtm_60_01/srtm_60_01.tif", str(startX+delta*(x-5)) + " " + str(startY+delta*(y-5)))
				height = int(result.getOutput(0))
				point = {
					"coord" : {"x" : startX+delta*(x-5), "y" : startY+delta*(y-5)},
					"height" : height
					}
				points[x].append(point)
		
		return points

    def neighbors(self, x, y, points):
		neighbors = []
		
		neighbors.append(points[x-1][y])
		neighbors.append(points[x][y+1])
		neighbors.append(points[x+1][y])
		neighbors.append(points[x][y-1])
		
		return neighbors

    def execute(self, parameters, messages):
		startX = 117
		startY = 56
		delta = 0.1
		file = "C:/arc/srtm_60_01/srtm_60_01.tif"
	
		grid = self.heightGrid(startX, startY, delta, file)
		
		arcpy.AddMessage(self.neighbors(5,5,grid))
	
		return















